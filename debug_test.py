#!/usr/bin/env python3
"""
调试测试脚本
"""

def test_imports():
    """测试导入"""
    print("开始测试导入...")
    
    try:
        print("1. 测试基础模块导入...")
        from models import ConversationState, MessageRole, IntentType
        print("✅ 基础模块导入成功")
        
        print("2. 测试服务模块导入...")
        from intent_classifier import IntentClassifier
        print("✅ IntentClassifier导入成功")
        
        from build_log_service import BuildLogService
        print("✅ BuildLogService导入成功")
        
        from knowledge_base import KnowledgeBase
        print("✅ KnowledgeBase导入成功")
        
        from llm_service import LLMService
        print("✅ LLMService导入成功")
        
        print("3. 测试LangGraph导入...")
        from langgraph.graph import StateGraph, END
        print("✅ LangGraph导入成功")
        
        print("4. 测试数据库模块导入...")
        from database_service import DatabaseService
        print("✅ DatabaseService导入成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 导入失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_service_creation():
    """测试服务创建"""
    print("\n开始测试服务创建...")
    
    try:
        print("1. 创建IntentClassifier...")
        from intent_classifier import IntentClassifier
        intent_classifier = IntentClassifier()
        print("✅ IntentClassifier创建成功")
        
        print("2. 创建BuildLogService...")
        from build_log_service import BuildLogService
        build_log_service = BuildLogService()
        print("✅ BuildLogService创建成功")
        
        print("3. 创建KnowledgeBase...")
        from knowledge_base import KnowledgeBase
        knowledge_base = KnowledgeBase()
        print("✅ KnowledgeBase创建成功")
        
        print("4. 创建LLMService...")
        from llm_service import LLMService
        llm_service = LLMService()
        print("✅ LLMService创建成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 服务创建失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=== 调试测试开始 ===")
    
    # 测试导入
    if not test_imports():
        print("❌ 导入测试失败，停止测试")
        exit(1)
    
    # 测试服务创建
    if not test_service_creation():
        print("❌ 服务创建测试失败，停止测试")
        exit(1)
    
    print("✅ 所有测试通过")
    
    # 测试聊天智能体创建
    print("\n开始测试聊天智能体创建...")
    try:
        from chat_agent import ChatAgent
        print("正在创建聊天智能体...")
        agent = ChatAgent()
        print("✅ 聊天智能体创建成功")
        
        # 测试流式处理方法
        print("测试流式处理方法...")
        import asyncio
        
        async def test_streaming():
            chunk_count = 0
            async for chunk in agent.process_streaming_message(
                "测试消息", "test_session", "构建", "123456", "测试问题"
            ):
                chunk_count += 1
                print(f"Chunk {chunk_count}: {chunk}")
                if chunk_count >= 5:  # 只测试前5个chunk
                    break
        
        asyncio.run(test_streaming())
        print("✅ 流式处理测试成功")
        
    except Exception as e:
        print(f"❌ 聊天智能体测试失败: {e}")
        import traceback
        traceback.print_exc()
