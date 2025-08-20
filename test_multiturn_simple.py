import requests
import json
import time

def test_multiturn_conversation():
    """测试多轮对话功能"""
    base_url = "http://localhost:8000"
    
    print("=== 测试多轮对话功能 ===")
    
    # 第一次调用
    print("\n1. 第一次调用...")
    first_request = {
        "message": json.dumps({
            "problemType": "构建",
            "cdInstId": "123456",
            "problemDesc": "构建失败怎么办"
        })
    }
    
    try:
        response = requests.post(f"{base_url}/api/chat", json=first_request, timeout=30)
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            # 解析响应获取session_id
            session_id = None
            lines = response.text.split('\n')
            for line in lines:
                if line.startswith('data: '):
                    try:
                        data = json.loads(line[6:])
                        if 'session_id' in data:
                            session_id = data['session_id']
                            print(f"获取到session_id: {session_id}")
                            break
                    except:
                        continue
            
            if not session_id:
                print("未能获取到session_id")
                return
                
        else:
            print(f"第一次调用失败: {response.status_code}")
            return
    except Exception as e:
        print(f"第一次调用异常: {e}")
        return
    
    # 等待一下
    print("\n等待3秒...")
    time.sleep(3)
    
    # 第二次调用（使用相同的session_id）
    print(f"\n2. 第二次调用 (session_id: {session_id})...")
    second_request = {
        "message": json.dumps({
            "problemType": "其他",
            "cdInstId": "123456",
            "problemDesc": "你叫什么名字"
        }),
        "session_id": session_id
    }
    
    try:
        response = requests.post(f"{base_url}/api/chat", json=second_request, timeout=30)
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            print("第二次调用成功!")
            print("请查看服务端日志，应该能看到：")
            print("- '从检查点恢复状态，包含 X 条历史消息'")
            print("- '对话历史：' 部分包含第一次的对话内容")
        else:
            print(f"第二次调用失败: {response.status_code}")
    except Exception as e:
        print(f"第二次调用异常: {e}")

if __name__ == "__main__":
    test_multiturn_conversation()
