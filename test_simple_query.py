import requests

# 测试简化的PubMed查询
def test_simple_query():
    search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    search_params = {
        'db': 'pubmed',
        'term': 'diabetes',  # 简化查询
        'retmax': 5,
        'retmode': 'json',
        'tool': 'literature_search_tool',
        'email': 'developer@example.com'
    }
    
    try:
        print("测试简化查询...")
        response = requests.get(search_url, params=search_params, timeout=30)
        print(f"状态码: {response.status_code}")
        print(f"URL: {response.url}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"成功获取数据: {data}")
        else:
            print(f"错误响应: {response.text}")
            
    except Exception as e:
        print(f"错误: {str(e)}")

if __name__ == "__main__":
    test_simple_query()

