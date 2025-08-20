import asyncio
import json
import aiohttp
import uuid

async def test_multiturn_conversation():
    """测试多轮对话功能"""
    base_url = "http://localhost:8000"
    
    # 第一次调用
    print("=== 第一次调用 ===")
    session_id = str(uuid.uuid4())
    first_request = {
        "message": json.dumps({
            "problemType": "构建",
            "cdInstId": "123456",
            "problemDesc": "构建失败怎么办"
        })
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{base_url}/api/chat", json=first_request, timeout=aiohttp.ClientTimeout(total=30)) as response:
                print(f"第一次调用状态码: {response.status}")
                if response.status == 200:
                    data = await response.text()
                    print(f"第一次调用响应长度: {len(data)}")
                    print(f"第一次调用响应前200字符: {data[:200]}...")
                    
                    # 尝试解析响应获取session_id
                    try:
                        lines = data.split('\n')
                        for line in lines:
                            if line.startswith('data: '):
                                json_data = json.loads(line[6:])
                                if 'session_id' in json_data:
                                    session_id = json_data['session_id']
                                    print(f"从响应中获取到session_id: {session_id}")
                                    break
                    except Exception as e:
                        print(f"解析session_id失败: {e}")
                else:
                    print(f"第一次调用失败: {response.status}")
    except Exception as e:
        print(f"第一次调用异常: {e}")
    
    # 等待一下
    print("等待2秒...")
    await asyncio.sleep(2)
    
    # 第二次调用（使用相同的session_id）
    print(f"\n=== 第二次调用 (session_id: {session_id}) ===")
    second_request = {
        "message": json.dumps({
            "problemType": "其他",
            "cdInstId": "123456", 
            "problemDesc": "你叫什么名字"
        }),
        "session_id": session_id
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{base_url}/api/chat", json=second_request, timeout=aiohttp.ClientTimeout(total=30)) as response:
                print(f"第二次调用状态码: {response.status}")
                if response.status == 200:
                    data = await response.text()
                    print(f"第二次调用响应长度: {len(data)}")
                    print(f"第二次调用响应前200字符: {data[:200]}...")
                else:
                    print(f"第二次调用失败: {response.status}")
    except Exception as e:
        print(f"第二次调用异常: {e}")

if __name__ == "__main__":
    asyncio.run(test_multiturn_conversation())
