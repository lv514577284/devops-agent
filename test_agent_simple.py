#!/usr/bin/env python3
"""
简单聊天智能体测试
"""

import asyncio

async def test_agent_creation():
    """测试聊天智能体创建"""
    print("开始测试聊天智能体创建...")
    
    try:
        # 测试创建聊天智能体
        from chat_agent import ChatAgent
        print("正在创建聊天智能体...")
        agent = ChatAgent()
        print("✅ 聊天智能体创建成功")
        
        # 测试基本属性
        print(f"智能体类型: {type(agent)}")
        print(f"是否有app属性: {hasattr(agent, 'app')}")
        print(f"是否有process_streaming_message方法: {hasattr(agent, 'process_streaming_message')}")
        
        return agent
        
    except Exception as e:
        print(f"❌ 聊天智能体创建失败: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    agent = asyncio.run(test_agent_creation())
    if agent:
        print("✅ 测试完成，聊天智能体创建成功")
    else:
        print("❌ 测试失败，聊天智能体创建失败")
