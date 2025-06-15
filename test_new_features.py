import requests
import json

# 测试新的Prompt生成和AI响应格式
def test_new_prompt_format():
    print("=== 测试新的Prompt生成和AI响应格式 ===")
    
    test_keywords = ["diabetes", "hypertension", "cancer"]
    
    for keyword in test_keywords:
        print(f"\n--- 测试关键词: {keyword} ---")
        
        # 第一步：生成新的详细Prompt
        url = "http://localhost:5000/api/generate_prompt"
        data = {"keyword": keyword}
        
        response = requests.post(url, json=data)
        if response.status_code != 200:
            print(f"生成Prompt失败: {response.text}")
            continue
        
        prompt_data = response.json()
        prompt = prompt_data["prompt"]
        print(f"✅ Prompt生成成功")
        print(f"Prompt长度: {len(prompt)} 字符")
        
        # 验证Prompt包含新的要求
        required_elements = [
            "医学文献检索专家",
            "卫生技术评估（HTA）",
            "MeSH术语",
            "布尔逻辑操作符",
            "近10年",
            "英文",
            "临床有效性、安全性、经济性",
            "QALY",
            "成本效果",
            "JSON格式"
        ]
        
        missing_elements = []
        for element in required_elements:
            if element not in prompt:
                missing_elements.append(element)
        
        if missing_elements:
            print(f"❌ Prompt缺少以下要素: {missing_elements}")
        else:
            print(f"✅ Prompt包含所有必需要素")
        
        # 第二步：测试AI策略生成
        url = "http://localhost:5000/api/get_ai_strategy"
        data = {"prompt": prompt}
        
        response = requests.post(url, json=data)
        if response.status_code != 200:
            print(f"AI策略生成失败: {response.text}")
            continue
        
        ai_data = response.json()
        ai_response = ai_data["ai_response"]
        print(f"✅ AI策略生成成功")
        
        # 验证AI响应格式
        required_fields = [
            "search_strategy",
            "explanation", 
            "keywords_analysis",
            "estimated_results",
            "mesh_terms",
            "search_tips"
        ]
        
        missing_fields = []
        for field in required_fields:
            if field not in ai_response:
                missing_fields.append(field)
        
        if missing_fields:
            print(f"❌ AI响应缺少字段: {missing_fields}")
        else:
            print(f"✅ AI响应包含所有必需字段")
        
        # 验证keywords_analysis子字段
        if "keywords_analysis" in ai_response:
            analysis = ai_response["keywords_analysis"]
            required_sub_fields = ["disease", "intervention", "population", "study_type"]
            missing_sub_fields = []
            for field in required_sub_fields:
                if field not in analysis:
                    missing_sub_fields.append(field)
            
            if missing_sub_fields:
                print(f"❌ keywords_analysis缺少子字段: {missing_sub_fields}")
            else:
                print(f"✅ keywords_analysis包含所有必需子字段")
        
        # 验证检索策略格式
        search_strategy = ai_response.get("search_strategy", "")
        if "\\n" in search_strategy or '\\"' in search_strategy:
            print(f"❌ 检索策略包含禁止的字符")
        else:
            print(f"✅ 检索策略格式正确")
        
        print(f"检索策略长度: {len(search_strategy)} 字符")
        print(f"MeSH术语数量: {len(ai_response.get('mesh_terms', []))}")

def test_pubmed_preview_function():
    print("\n=== 测试PubMed预览功能 ===")
    
    # 使用一个简单的检索策略进行测试
    search_strategy = '("diabetes" [MeSH Terms] OR diabetes [Text Word]) AND ("Health Technology Assessment" [MeSH Terms] OR "health technology assessment" [Text Word]) AND ("Randomized Controlled Trial" [Publication Type] OR "Systematic Review" [Publication Type]) AND ("2015/01/01"[Date - Publication] : "3000/12/31"[Date - Publication]) AND (English [Language])'
    
    url = "http://localhost:5000/api/execute_pubmed_search"
    data = {"search_strategy": search_strategy}
    
    response = requests.post(url, json=data)
    if response.status_code != 200:
        print(f"❌ PubMed检索失败: {response.text}")
        return
    
    result = response.json()
    print(f"✅ PubMed检索成功")
    
    # 验证预览功能
    if "preview_results" not in result:
        print(f"❌ 响应中缺少preview_results字段")
        return
    
    preview_results = result["preview_results"]
    total_count = result.get("total_count", 0)
    retrieved_count = result.get("retrieved_count", 0)
    
    print(f"总文献数: {total_count}")
    print(f"获取文献数: {retrieved_count}")
    print(f"预览文献数: {len(preview_results)}")
    
    # 验证预览结果数量
    expected_preview_count = min(10, retrieved_count)
    if len(preview_results) != expected_preview_count:
        print(f"❌ 预览结果数量不正确，期望: {expected_preview_count}, 实际: {len(preview_results)}")
    else:
        print(f"✅ 预览结果数量正确")
    
    # 验证预览结果格式
    if preview_results:
        first_result = preview_results[0]
        required_fields = ["PMID", "Title", "Authors", "Journal", "Publication_Date", "DOI", "Study_Type", "URL"]
        missing_fields = []
        for field in required_fields:
            if field not in first_result:
                missing_fields.append(field)
        
        if missing_fields:
            print(f"❌ 预览结果缺少字段: {missing_fields}")
        else:
            print(f"✅ 预览结果格式正确")
        
        # 显示第一个预览结果
        print(f"\n第一个预览结果:")
        print(f"PMID: {first_result.get('PMID', 'N/A')}")
        print(f"标题: {first_result.get('Title', 'N/A')[:100]}...")
        print(f"作者: {first_result.get('Authors', 'N/A')}")
        print(f"期刊: {first_result.get('Journal', 'N/A')}")
        print(f"研究类型: {first_result.get('Study_Type', 'N/A')}")
    
    # 验证CSV文件仍然包含完整结果
    if "pubmed_results_csv" in result:
        print(f"✅ CSV文件生成成功")
    else:
        print(f"❌ CSV文件生成失败")

if __name__ == "__main__":
    test_new_prompt_format()
    test_pubmed_preview_function()
    print("\n=== 测试完成 ===")

