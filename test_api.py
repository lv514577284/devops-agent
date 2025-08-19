#!/usr/bin/env python3
"""
API测试脚本
"""

import asyncio
import aiohttp
import json

async def test_chat_api():
    """测试聊天API"""
    url = "http://localhost:8000/api/chat"
    
    # 测试数据
    payload = {
        "message": "{\"problemType\": \"构建\", \"cdInstId\": \"123456\", \"problemDesc\": \"我的构建为什么出错了\"}"
    }
    
    print("开始测试聊天API...")
    print(f"请求URL: {url}")
    print(f"请求数据: {json.dumps(payload, ensure_ascii=False)}")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                print(f"响应状态码: {response.status}")
                print(f"响应头: {dict(response.headers)}")
                
                # 读取流式响应
                print("\n开始读取流式响应:")
                chunk_count = 0
                async for line in response.content:
                    line = line.decode('utf-8').strip()
                    if line.startswith('data: '):
                        chunk_count += 1
                        data = line[6:]  # 移除 'data: ' 前缀
                        try:
                            json_data = json.loads(data)
                            print(f"Chunk {chunk_count}: {json.dumps(json_data, ensure_ascii=False)}")
                            
                            # 检查是否完成
                            if json_data.get('complete'):
                                print("✅ 流式响应完成")
                                break
                            elif json_data.get('error'):
                                print(f"❌ 错误: {json_data['error']}")
                                break
                        except json.JSONDecodeError:
                            print(f"Chunk {chunk_count}: 非JSON数据 - {data}")
                
                print(f"\n总共接收到 {chunk_count} 个数据块")
                
    except Exception as e:
        print(f"❌ 请求失败: {e}")

if __name__ == "__main__":
    asyncio.run(test_chat_api())
