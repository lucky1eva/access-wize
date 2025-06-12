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
        
        # 根据用户新的要求生成Prompt
        prompt = f"""请为疾病或干预方式：{keyword} 为主题生成一段可以用于PubMed的文献检索策略，以获得卫生技术评估相关的所有文献。\n\n请以JSON格式返回结果，包含以下字段： \n{{\n    "search_strategy": "完整的PubMed搜索策略", \n    "explanation": "搜索策略的详细说明", \n    "keywords_analysis": {{\n        "disease": "识别出的疾病/病症", \n        "intervention": "识别出的干预措施", \n        "population": "识别出的目标人群", \n        "study_type": "推荐的研究类型" \n    }}, \n    "estimated_results": "预估检索结果数量范围", \n    "mesh_terms": ["相关的MeSH术语列表"], \n    "search_tips": "检索优化建议" \n}}\n\n请确保搜索策略专业、准确、全面。特别需要注意：不要在"search_strategy"中出现"\\n", 或""符号。"""
        
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
        keyword_start = prompt.find("疾病或干预方式：") + len("疾病或干预方式：")
        keyword_end = prompt.find(" 为主题", keyword_start)
        keyword = prompt[keyword_start:keyword_end].strip()
        
        # 模拟AI生成的JSON结果
        ai_response = {
            "search_strategy": f"(\"{keyword}\" [MeSH Terms] OR {keyword} [Text Word]) AND (health technology assessment [MeSH Terms] OR HTA [Text Word]) AND (clinical trial [pt] OR randomized controlled trial [pt] OR systematic review [pt] OR meta-analysis [pt] OR cohort studies [pt] OR real world evidence [Text Word]) AND ((\"2015/01/01\"[Date - Publication] : \"3000/12/31\"[Date - Publication])) AND (English [Language])",
            "explanation": f"本检索策略针对关键词 \"{keyword}\" 设计，结合了疾病相关术语、卫生技术评估相关术语、高质量研究类型限制、时间限制和语言限制。策略包含了临床有效性、安全性、经济性评价以及生命质量相关的结局指标，同时涵盖了流行病学和卫生经济学评价的关键要素。",
            "keywords_analysis": {
                "disease": keyword,
                "intervention": "相关干预措施（药物治疗、非药物治疗、医疗器械等）",
                "population": "成年患者群体",
                "study_type": "随机对照试验、系统评价、Meta分析、队列研究、真实世界研究"
            },
            "estimated_results": "500-2000篇文献",
            "mesh_terms": [keyword, "Health Technology Assessment", "Cost-Effectiveness Analysis", "Quality of Life", "Clinical Effectiveness", "Safety", "Economic Evaluation"],
            "search_tips": "建议根据实际检索结果调整检索词的组合方式，如果结果过多可以增加更具体的限制条件，如果结果过少可以减少部分限制或使用更广泛的同义词。可以考虑分步检索，先检索核心概念，再逐步添加限制条件。"
        }
        
        return jsonify({"ai_response": ai_response})
        
    except Exception as e:
        return jsonify({"error": f"AI策略生成失败: {str(e)}"}), 500

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
    """执行PubMed检索并返回结果"""
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
        
        # 将结果转换为CSV格式
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



