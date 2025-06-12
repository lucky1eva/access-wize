import requests
import json

# 测试生成Prompt API
def test_generate_prompt():
    url = "http://localhost:5000/api/generate_prompt"
    data = {"keyword": "diabetes"}
    
    response = requests.post(url, json=data)
    print(f"生成Prompt API状态码: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"生成的Prompt: {result['prompt'][:200]}...")
        return result['prompt']
    else:
        print(f"错误: {response.text}")
        return None

# 测试AI策略生成API
def test_ai_strategy(prompt):
    url = "http://localhost:5000/api/get_ai_strategy"
    data = {"prompt": prompt}
    
    response = requests.post(url, json=data)
    print(f"AI策略生成API状态码: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"AI生成的策略: {json.dumps(result['ai_response'], indent=2, ensure_ascii=False)}")
        return result['ai_response']
    else:
        print(f"错误: {response.text}")
        return None

# 测试PubMed检索API
def test_pubmed_search(search_strategy):
    url = "http://localhost:5000/api/execute_pubmed_search"
    data = {"search_strategy": search_strategy}
    
    response = requests.post(url, json=data)
    print(f"PubMed检索API状态码: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"检索结果: 总数 {result['total_count']}, 获取 {result['retrieved_count']} 篇")
        print(f"检索策略: {result['search_strategy_used']}")
        return result
    else:
        print(f"错误: {response.text}")
        return None

if __name__ == "__main__":
    print("=== 测试后端API ===")
    
    # 第一步：生成Prompt
    print("\n1. 测试生成Prompt API")
    prompt = test_generate_prompt()
    
    if prompt:
        # 第二步：生成AI策略
        print("\n2. 测试AI策略生成API")
        ai_response = test_ai_strategy(prompt)
        
        if ai_response and 'search_strategy' in ai_response:
            # 第三步：执行PubMed检索
            print("\n3. 测试PubMed检索API")
            pubmed_result = test_pubmed_search(ai_response['search_strategy'])
            
            if pubmed_result:
                print("\n=== 所有API测试成功 ===")
            else:
                print("\n=== PubMed检索API测试失败 ===")
        else:
            print("\n=== AI策略生成API测试失败 ===")
    else:
        print("\n=== 生成Prompt API测试失败 ===")

