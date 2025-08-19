#!/usr/bin/env python3
"""
数据库功能测试脚本
"""

import asyncio
import json
from database_service import DatabaseService
from models import ConversationState, Message, MessageRole, IntentType

async def test_database():
    """测试数据库功能"""
    print("开始测试数据库功能...")
    
    # 初始化数据库服务
    db_service = DatabaseService()
    
    # 测试数据
    session_id = "test_session_123"
    
    # 创建测试会话状态
    state = ConversationState(
        session_id=session_id,
        problem_type="构建",
        cd_inst_id="123456",
        problem_desc="我的构建为什么出错了",
        current_intent=IntentType.BUILD
    )
    
    # 添加测试消息
    state.add_message(MessageRole.USER, "我的构建为什么出错了")
    state.add_message(MessageRole.ASSISTANT, "我来帮您分析构建问题...")
    
    print(f"创建测试会话: {session_id}")
    print(f"消息数量: {len(state.messages)}")
    
    # 测试保存
    print("\n1. 测试保存会话状态...")
    db_service.save_conversation_state(state)
    print("✓ 会话状态保存成功")
    
    # 测试加载
    print("\n2. 测试加载会话状态...")
    loaded_state = db_service.load_conversation_state(session_id)
    if loaded_state:
        print(f"✓ 会话状态加载成功")
        print(f"  - 会话ID: {loaded_state.session_id}")
        print(f"  - 问题类型: {loaded_state.problem_type}")
        print(f"  - 实例ID: {loaded_state.cd_inst_id}")
        print(f"  - 消息数量: {len(loaded_state.messages)}")
        for i, msg in enumerate(loaded_state.messages):
            print(f"  - 消息{i+1}: [{msg.role.value}] {msg.content[:50]}...")
    else:
        print("✗ 会话状态加载失败")
    
    # 测试会话列表
    print("\n3. 测试获取会话列表...")
    conversations = db_service.get_conversation_list()
    print(f"✓ 找到 {len(conversations)} 个会话")
    for conv in conversations[:3]:  # 只显示前3个
        print(f"  - {conv['session_id']}: {conv['problem_desc'][:30]}...")
    
    # 测试多轮对话
    print("\n4. 测试多轮对话...")
    if loaded_state:
        # 添加新消息
        loaded_state.add_message(MessageRole.USER, "能详细说明一下吗？")
        loaded_state.add_message(MessageRole.ASSISTANT, "好的，让我详细分析构建日志...")
        
        # 保存更新后的状态
        db_service.save_conversation_state(loaded_state)
        print("✓ 多轮对话保存成功")
        
        # 重新加载验证
        updated_state = db_service.load_conversation_state(session_id)
        if updated_state and len(updated_state.messages) == 4:
            print(f"✓ 多轮对话验证成功，消息数量: {len(updated_state.messages)}")
        else:
            print("✗ 多轮对话验证失败")
    
    print("\n数据库功能测试完成！")

if __name__ == "__main__":
    asyncio.run(test_database())
