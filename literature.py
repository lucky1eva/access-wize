from flask import Blueprint, request, jsonify
import json
import time
import csv
import io
import base64
import requests
from datetime import datetime
import urllib.parse
import xml.etree.ElementTree as ET

literature_bp = Blueprint("literature", __name__)

# PubMed E-utilities基础URL
PUBMED_BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"

@literature_bp.route("/generate_prompt", methods=["POST"])
def generate_prompt():
    """生成用于AI模型的Prompt"""
    try:
        data = request.get_json()
        keyword = data.get("keyword", "").strip()
        
        if not keyword:
            return jsonify({"error": "关键词不能为空"}), 400
        
        # 使用用户提供的新的详细Prompt模板
        prompt = f"""你是一位医学文献检索专家。请根据用户提供的关键词{keyword}，生成一个专业的PubMed搜索策略，以提供该疾病或干预方式相关的卫生技术评估（HTA）的所有文献。
请按照以下要求生成搜索策略：
1. 分析关键词，识别疾病、干预措施、人群等要素 
2. 使用适当的MeSH术语和自由词组合 
3. 运用布尔逻辑操作符（AND、OR、NOT） 
4. 考虑同义词和相关术语 
5. 限制研究类型为高质量研究（如RCT、系统评价、Meta分析、队列研究、真实世界研究等） 
6. 限制发表时间为近10年 
7. 限制语言为英文
8. 检索词应包含与疾病相关的所有干预措施，或与干预措施相关的所有适应症 
9. 检索词应包含与疾病相关的所有临床有效性、安全性、经济性、以及生命质量（如QALY）结局指标 
10. 检索词应包含流行病学中的患病率、发病率、疾病负担、成本效果、成本效用、患者治疗满意度、患者依从性等与卫生经济学评价相关的关键词 
请以JSON格式返回结果，包含以下字段： {{ "search_strategy": "完整的PubMed搜索策略", "explanation": "搜索策略的详细说明", "keywords_analysis": {{ "disease": "识别出的疾病/病症", "intervention": "识别出的干预措施", "population": "识别出的目标人群", "study_type": "推荐的研究类型" }}, "estimated_results": "预估检索结果数量范围", "mesh_terms": ["相关的MeSH术语列表"], "search_tips": "检索优化建议" }}
请确保搜索策略专业、准确、全面。特别需要注意：不要在"search_strategy"中出现"\\n", 或"\\"符号。"""
        
        return jsonify({"prompt": prompt})
        
    except Exception as e:
        return jsonify({"error": f"生成Prompt失败: {str(e)}"}), 500

@literature_bp.route("/get_ai_strategy", methods=["POST"])
def get_ai_strategy():
    """模拟AI模型生成检索策略"""
    try:
        data = request.get_json()
        prompt = data.get("prompt", "").strip()
        
        if not prompt:
            return jsonify({"error": "Prompt不能为空"}), 400
        
        # 模拟AI调用延迟
        time.sleep(2)
        
        # 从prompt中提取关键词
        keyword_start = prompt.find("关键词") + len("关键词")
        keyword_end = prompt.find("，生成一个专业的", keyword_start)
        keyword = prompt[keyword_start:keyword_end].strip()
        
        # 根据关键词生成更专业的AI响应
        ai_response = generate_professional_strategy(keyword)
        
        return jsonify({"ai_response": ai_response})
        
    except Exception as e:
        return jsonify({"error": f"AI策略生成失败: {str(e)}"}), 500

def generate_professional_strategy(keyword):
    """根据关键词生成专业的检索策略"""
    
    # 基础疾病和干预措施映射
    disease_interventions = {
        "diabetes": {
            "mesh_terms": ["Diabetes Mellitus", "Diabetes Mellitus, Type 2", "Diabetes Mellitus, Type 1", "Diabetic Complications"],
            "interventions": ["metformin", "insulin", "lifestyle intervention", "dietary therapy", "exercise therapy"],
            "synonyms": ["diabetes mellitus", "diabetic", "hyperglycemia", "glucose intolerance"]
        },
        "hypertension": {
            "mesh_terms": ["Hypertension", "Blood Pressure", "Antihypertensive Agents"],
            "interventions": ["ACE inhibitors", "beta blockers", "calcium channel blockers", "diuretics"],
            "synonyms": ["high blood pressure", "elevated blood pressure", "arterial hypertension"]
        },
        "insomnia": {
            "mesh_terms": ["Sleep Initiation and Maintenance Disorders", "Insomnia", "Sleep Disorders"],
            "interventions": ["cognitive behavioral therapy", "sleep hygiene", "melatonin", "hypnotics"],
            "synonyms": ["sleep disorder", "sleeplessness", "sleep disturbance"]
        },
        "cancer": {
            "mesh_terms": ["Neoplasms", "Oncology", "Antineoplastic Agents"],
            "interventions": ["chemotherapy", "radiotherapy", "immunotherapy", "targeted therapy"],
            "synonyms": ["malignancy", "tumor", "carcinoma", "oncology"]
        }
    }
    
    # 获取关键词相关信息
    keyword_lower = keyword.lower()
    disease_info = None
    for disease, info in disease_interventions.items():
        if disease in keyword_lower or keyword_lower in info["synonyms"]:
            disease_info = info
            break
    
    if not disease_info:
        # 默认策略
        disease_info = {
            "mesh_terms": [keyword],
            "interventions": ["therapeutic intervention", "treatment", "therapy"],
            "synonyms": [keyword]
        }
    
    # 构建检索策略
    # 疾病术语部分
    disease_terms = []
    disease_terms.append(f'"{keyword}"[MeSH Terms]')
    disease_terms.append(f'{keyword}[Text Word]')
    for synonym in disease_info["synonyms"]:
        disease_terms.append(f'"{synonym}"[Text Word]')
    
    disease_part = "(" + " OR ".join(disease_terms) + ")"
    
    # HTA相关术语
    hta_terms = [
        '"Health Technology Assessment"[MeSH Terms]',
        '"Technology Assessment, Biomedical"[MeSH Terms]',
        '"Cost-Benefit Analysis"[MeSH Terms]',
        '"Economics, Medical"[MeSH Terms]',
        '"Quality-Adjusted Life Years"[MeSH Terms]',
        'HTA[Text Word]',
        '"health technology assessment"[Text Word]',
        '"cost effectiveness"[Text Word]',
        '"cost utility"[Text Word]',
        '"economic evaluation"[Text Word]',
        '"budget impact"[Text Word]',
        'QALY[Text Word]',
        '"quality of life"[Text Word]',
        '"clinical effectiveness"[Text Word]',
        '"safety profile"[Text Word]',
        'prevalence[Text Word]',
        'incidence[Text Word]',
        '"disease burden"[Text Word]',
        '"patient satisfaction"[Text Word]',
        '"treatment adherence"[Text Word]'
    ]
    
    hta_part = "(" + " OR ".join(hta_terms) + ")"
    
    # 研究类型限制
    study_types = [
        '"Randomized Controlled Trial"[Publication Type]',
        '"Systematic Review"[Publication Type]',
        '"Meta-Analysis"[Publication Type]',
        '"Cohort Studies"[MeSH Terms]',
        '"Clinical Trial"[Publication Type]',
        '"real world evidence"[Text Word]',
        '"observational study"[Text Word]'
    ]
    
    study_part = "(" + " OR ".join(study_types) + ")"
    
    # 时间和语言限制
    time_limit = '("2015/01/01"[Date - Publication] : "3000/12/31"[Date - Publication])'
    language_limit = 'English[Language]'
    
    # 组合完整策略
    search_strategy = f"{disease_part} AND {hta_part} AND {study_part} AND {time_limit} AND {language_limit}"
    
    # 生成响应
    ai_response = {
        "search_strategy": search_strategy,
        "explanation": f"本检索策略针对关键词 '{keyword}' 设计，采用了多层次的检索方法。首先使用MeSH术语和自由词检索疾病相关文献，然后结合卫生技术评估相关术语，包括成本效果分析、生命质量评价、临床有效性和安全性等关键概念。策略限制了研究类型为高质量研究，时间范围为近10年，语言限制为英文。检索词涵盖了流行病学指标、经济学评价指标以及患者报告结局指标，确保检索结果的全面性和相关性。",
        "keywords_analysis": {
            "disease": keyword,
            "intervention": ", ".join(disease_info["interventions"][:3]) + "等",
            "population": "成年患者群体，包括不同年龄段和疾病严重程度的患者",
            "study_type": "随机对照试验、系统评价、Meta分析、队列研究、真实世界研究"
        },
        "estimated_results": "200-1500篇文献",
        "mesh_terms": disease_info["mesh_terms"] + ["Health Technology Assessment", "Cost-Benefit Analysis", "Quality-Adjusted Life Years", "Economics, Medical"],
        "search_tips": "建议根据实际检索结果调整策略：如果结果过多，可以增加更具体的干预措施或结局指标；如果结果过少，可以减少部分限制条件或扩展同义词。可以考虑分步检索，先检索核心疾病概念，再逐步添加HTA相关限制。对于新兴疾病或干预措施，建议适当放宽时间限制。"
    }
    
    return ai_response

def search_pubmed(query, retmax=100):
    """使用PubMed E-utilities API进行检索"""
    try:
        # 第一步：使用ESearch获取PMID列表
        search_url = f"{PUBMED_BASE_URL}esearch.fcgi"
        search_params = {
            "db": "pubmed",
            "term": query,
            "retmax": retmax,
            "retmode": "json",
            "tool": "literature_search_tool",
            "email": "developer@example.com"
        }
        
        print(f"正在搜索PubMed: {query}")
        search_response = requests.get(search_url, params=search_params, timeout=30)
        search_response.raise_for_status()
        search_data = search_response.json()
        
        if "esearchresult" not in search_data:
            print(f"PubMed ESearch结果格式错误: {search_data}")
            return None, "搜索结果格式错误"
        
        pmid_list = search_data["esearchresult"].get("idlist", [])
        total_count = int(search_data["esearchresult"].get("count", 0))
        
        print(f"找到 {total_count} 篇文献，获取前 {len(pmid_list)} 篇详细信息")
        
        if not pmid_list:
            return [], total_count
        
        # 第二步：使用ESummary获取文献摘要信息
        summary_url = f"{PUBMED_BASE_URL}esummary.fcgi"
        summary_params = {
            "db": "pubmed",
            "id": ",".join(pmid_list),
            "retmode": "json",
            "tool": "literature_search_tool",
            "email": "developer@example.com"
        }
        
        summary_response = requests.get(summary_url, params=summary_params, timeout=30)
        summary_response.raise_for_status()
        summary_data = summary_response.json()
        
        # 解析结果
        results = []
        if "result" in summary_data:
            for pmid in pmid_list:
                if pmid in summary_data["result"]:
                    article = summary_data["result"][pmid]
                    
                    # 提取作者信息
                    authors = []
                    if "authors" in article:
                        for author in article["authors"][:3]:  # 只取前3个作者
                            authors.append(author.get("name", ""))
                    author_str = ", ".join(authors)
                    if len(article.get("authors", [])) > 3:
                        author_str += " et al"
                    
                    # 提取期刊信息
                    journal = article.get("fulljournalname", article.get("source", ""))
                    
                    # 提取发表日期
                    pub_date = article.get("pubdate", "")
                    
                    # 提取DOI
                    doi = ""
                    if "articleids" in article:
                        for article_id in article["articleids"]:
                            if article_id.get("idtype") == "doi":
                                doi = article_id.get("value", "")
                                break
                    
                    # 确定研究类型
                    study_type = ""
                    if "pubtype" in article:
                        pub_types = [pt for pt in article["pubtype"]]
                        if "Randomized Controlled Trial" in pub_types:
                            study_type = "RCT"
                        elif "Systematic Review" in pub_types:
                            study_type = "Systematic Review"
                        elif "Meta-Analysis" in pub_types:
                            study_type = "Meta-Analysis"
                        elif "Review" in pub_types:
                            study_type = "Review"
                        else:
                            study_type = "Original Research"
                    
                    result = {
                        "PMID": pmid,
                        "Title": article.get("title", ""),
                        "Authors": author_str,
                        "Journal": journal,
                        "Publication_Date": pub_date,
                        "DOI": doi,
                        "Abstract": "",  # ESummary不包含摘要，需要EFetch获取
                        "Study_Type": study_type,
                        "URL": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
                    }
                    results.append(result)
        
        print(f"成功解析 {len(results)} 篇文献信息")
        return results, total_count
        
    except requests.exceptions.RequestException as e:
        print(f"网络请求错误: {str(e)}")
        return None, f"网络请求错误: {str(e)}"
    except Exception as e:
        print(f"检索过程中发生错误: {str(e)}")
        return None, f"检索过程中发生错误: {str(e)}"

@literature_bp.route("/execute_pubmed_search", methods=["POST"])
def execute_pubmed_search():
    """执行PubMed检索并返回结果（包含预览功能）"""
    try:
        data = request.get_json()
        search_strategy = data.get("search_strategy", "").strip()
        
        if not search_strategy:
            return jsonify({"error": "检索策略不能为空"}), 400
        
        # 记录检索策略日志
        search_log = {
            "timestamp": datetime.now().isoformat(),
            "search_strategy": search_strategy,
            "tool": "literature_search_tool"
        }
        
        # 执行PubMed检索
        results, total_count = search_pubmed(search_strategy, retmax=100)
        
        if results is None:
            return jsonify({"error": total_count}), 500
        
        # 生成预览结果（前10个）
        preview_results = results[:10] if results else []
        
        # 将完整结果转换为CSV格式
        output = io.StringIO()
        if results:
            fieldnames = results[0].keys()
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        else:
            # 如果没有结果，创建空的CSV结构
            fieldnames = ["PMID", "Title", "Authors", "Journal", "Publication_Date", "DOI", "Abstract", "Study_Type", "URL"]
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()
        
        csv_content = output.getvalue()
        output.close()
        
        # 将CSV内容编码为base64
        csv_base64 = base64.b64encode(csv_content.encode("utf-8")).decode("utf-8")
        
        # 更新检索日志
        search_log["results_count"] = len(results)
        search_log["total_count"] = total_count
        
        return jsonify({
            "total_count": total_count,
            "retrieved_count": len(results),
            "preview_results": preview_results,  # 新增：预览结果
            "pubmed_results_csv": csv_base64,
            "search_strategy_used": search_strategy,
            "search_timestamp": datetime.now().isoformat(),
            "search_log": search_log
        })
        
    except Exception as e:
        print(f"PubMed检索失败: {str(e)}")
        return jsonify({"error": f"PubMed检索失败: {str(e)}"}), 500

@literature_bp.route("/health", methods=["GET"])
def health_check():
    """健康检查端点"""
    return jsonify({
        "status": "healthy",
        "service": "Literature Search API",
        "timestamp": datetime.now().isoformat()
    })

