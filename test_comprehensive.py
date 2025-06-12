import requests
import json
import time

# 测试不同关键词的检索效果
test_keywords = ["diabetes", "hypertension", "insomnia", "cancer", "covid-19"]

def test_keyword_search(keyword):
    print(f"\n=== 测试关键词: {keyword} ===")
    
    # 第一步：生成Prompt
    url = "http://localhost:5000/api/generate_prompt"
    data = {"keyword": keyword}
    
    response = requests.post(url, json=data)
    if response.status_code != 200:
        print(f"生成Prompt失败: {response.text}")
        return False
    
    prompt = response.json()["prompt"]
    print(f"生成Prompt成功")
    
    # 第二步：生成AI策略
    url = "http://localhost:5000/api/get_ai_strategy"
    data = {"prompt": prompt}
    
    response = requests.post(url, json=data)
    if response.status_code != 200:
        print(f"AI策略生成失败: {response.text}")
        return False
    
    ai_response = response.json()["ai_response"]
    search_strategy = ai_response["search_strategy"]
    print(f"AI策略生成成功")
    print(f"检索策略: {search_strategy[:100]}...")
    
    # 第三步：执行PubMed检索
    url = "http://localhost:5000/api/execute_pubmed_search"
    data = {"search_strategy": search_strategy}
    
    response = requests.post(url, json=data)
    if response.status_code != 200:
        print(f"PubMed检索失败: {response.text}")
        return False
    
    result = response.json()
    print(f"PubMed检索成功: 总数 {result['total_count']}, 获取 {result['retrieved_count']} 篇")
    
    # 验证CSV内容
    if result.get("pubmed_results_csv"):
        print("CSV文件生成成功")
        return True
    else:
        print("CSV文件生成失败")
        return False

def test_error_handling():
    print("\n=== 测试错误处理 ===")
    
    # 测试空关键词
    url = "http://localhost:5000/api/generate_prompt"
    data = {"keyword": ""}
    response = requests.post(url, json=data)
    print(f"空关键词测试: {response.status_code} - {response.json().get('error', 'OK')}")
    
    # 测试空Prompt
    url = "http://localhost:5000/api/get_ai_strategy"
    data = {"prompt": ""}
    response = requests.post(url, json=data)
    print(f"空Prompt测试: {response.status_code} - {response.json().get('error', 'OK')}")
    
    # 测试空检索策略
    url = "http://localhost:5000/api/execute_pubmed_search"
    data = {"search_strategy": ""}
    response = requests.post(url, json=data)
    print(f"空检索策略测试: {response.status_code} - {response.json().get('error', 'OK')}")

if __name__ == "__main__":
    print("=== PubMed检索功能验证与优化测试 ===")
    
    success_count = 0
    total_count = len(test_keywords)
    
    for keyword in test_keywords:
        if test_keyword_search(keyword):
            success_count += 1
        time.sleep(1)  # 避免请求过于频繁
    
    print(f"\n=== 测试结果汇总 ===")
    print(f"成功: {success_count}/{total_count}")
    print(f"成功率: {success_count/total_count*100:.1f}%")
    
    # 测试错误处理
    test_error_handling()
    
    print("\n=== 测试完成 ===")

