import requests
import json

def test_simple():
    """简单的API测试"""
    base_url = "http://localhost:8000"
    
    # 测试基本连接
    try:
        response = requests.get(f"{base_url}/")
        print(f"基本连接测试: {response.status_code}")
    except Exception as e:
        print(f"连接失败: {e}")
        return
    
    # 第一次调用
    print("\n=== 第一次调用 ===")
    first_request = {
        "message": json.dumps({
            "problemType": "构建",
            "cdInstId": "123456",
            "problemDesc": "构建失败怎么办"
        })
    }
    
    try:
        response = requests.post(f"{base_url}/api/chat", json=first_request, timeout=10)
        print(f"第一次调用状态码: {response.status_code}")
        if response.status_code == 200:
            print(f"第一次调用响应长度: {len(response.text)}")
            print(f"第一次调用响应前200字符: {response.text[:200]}...")
        else:
            print(f"第一次调用失败: {response.status_code}")
    except Exception as e:
        print(f"第一次调用异常: {e}")

if __name__ == "__main__":
    test_simple()
