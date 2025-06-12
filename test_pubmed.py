import requests
import json

# 测试PubMed API调用
def test_pubmed_api():
    # 简单的测试查询
    search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    search_params = {
        'db': 'pubmed',
        'term': 'hypertension',
        'retmax': 5,
        'retmode': 'json',
        'tool': 'literature_search_tool',
        'email': 'developer@example.com'
    }
    
    try:
        print("正在测试PubMed API...")
        response = requests.get(search_url, params=search_params, timeout=30)
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {response.text[:500]}...")
        
        if response.status_code == 200:
            data = response.json()
            print(f"解析后的JSON: {json.dumps(data, indent=2)}")
        
    except Exception as e:
        print(f"错误: {str(e)}")

if __name__ == "__main__":
    test_pubmed_api()

