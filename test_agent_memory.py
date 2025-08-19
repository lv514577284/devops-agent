#!/usr/bin/env python3
"""
使用内存检查点的聊天智能体测试
"""

import asyncio
from langgraph.checkpoint.memory import MemorySaver
from models import ConversationState, MessageRole, IntentType
from intent_classifier import IntentClassifier
from build_log_service import BuildLogService
from knowledge_base import KnowledgeBase
from llm_service import LLMService
from langgraph.graph import StateGraph, END

async def test_memory_checkpoint():
    """测试内存检查点"""
    print("开始测试内存检查点...")
    
    try:
        # 创建各个服务
        intent_classifier = IntentClassifier()
        build_log_service = BuildLogService()
        knowledge_base = KnowledgeBase()
        llm_service = LLMService()
        
        print("✅ 所有服务创建成功")
        
        # 创建状态图
        workflow = StateGraph(ConversationState)
        
        # 添加一个简单的节点
        async def simple_node(state: ConversationState) -> ConversationState:
            """简单节点"""
            print("执行简单节点")
            state.add_message(MessageRole.ASSISTANT, "这是一个测试回复")
            return state
        
        workflow.add_node("simple", simple_node)
        workflow.set_entry_point("simple")
        workflow.add_edge("simple", END)
        
        print("✅ 状态图创建成功")
        
        # 使用内存检查点
        memory = MemorySaver()
        app = workflow.compile(checkpointer=memory)
        
        print("✅ 应用编译成功")
        
        # 测试调用
        state = ConversationState(session_id="test_memory")
        state.add_message(MessageRole.USER, "测试消息")
        
        config = {"configurable": {"session_id": "test_memory"}}
        
        print("开始调用应用...")
        result = await app.ainvoke(state, config)
        
        print(f"✅ 调用成功，结果类型: {type(result)}")
        print(f"消息数量: {len(result.messages)}")
        for msg in result.messages:
            print(f"  - [{msg.role.value}] {msg.content}")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_memory_checkpoint())
    if success:
        print("✅ 内存检查点测试完成")
    else:
        print("❌ 内存检查点测试失败")
