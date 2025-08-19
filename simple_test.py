#!/usr/bin/env python3
"""
简单测试脚本
"""

import asyncio
from models import ConversationState, MessageRole

async def test_basic():
    """基本测试"""
    print("开始基本测试...")
    
    try:
        # 测试创建ConversationState
        state = ConversationState(session_id="test_123")
        state.add_message(MessageRole.USER, "测试消息")
        print(f"✅ ConversationState创建成功，消息数量: {len(state.messages)}")
        
        # 测试数据库服务
        from database_service import DatabaseService
        db_service = DatabaseService()
        print("✅ 数据库服务创建成功")
        
        # 测试保存状态
        db_service.save_conversation_state(state)
        print("✅ 状态保存成功")
        
        # 测试加载状态
        loaded_state = db_service.load_conversation_state("test_123")
        if loaded_state:
            print(f"✅ 状态加载成功，消息数量: {len(loaded_state.messages)}")
        else:
            print("❌ 状态加载失败")
        
    except Exception as e:
        print(f"❌ 基本测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_basic())
