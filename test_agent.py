#!/usr/bin/env python3
"""
直接测试chat_agent的脚本
"""

import asyncio
from chat_agent import ChatAgent

async def test_agent():
    """测试聊天智能体"""
    print("开始测试聊天智能体...")
    
    try:
        # 创建聊天智能体
        agent = ChatAgent()
        print("✅ 聊天智能体创建成功")
        
        # 测试消息
        message = "我的构建为什么出错了"
        session_id = "test_session_123"
        problem_type = "构建"
        cd_inst_id = "123456"
        problem_desc = "我的构建为什么出错了"
        
        print(f"测试消息: {message}")
        print(f"会话ID: {session_id}")
        print(f"问题类型: {problem_type}")
        print(f"实例ID: {cd_inst_id}")
        print(f"问题描述: {problem_desc}")
        
        # 调用流式处理方法
        print("\n开始调用process_streaming_message...")
        chunk_count = 0
        async for chunk in agent.process_streaming_message(
            message, session_id, problem_type, cd_inst_id, problem_desc
        ):
            chunk_count += 1
            print(f"Chunk {chunk_count}: {chunk}")
        
        print(f"\n✅ 流式处理完成，共生成 {chunk_count} 个chunk")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_agent())
