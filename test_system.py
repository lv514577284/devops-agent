#!/usr/bin/env python3
"""
系统功能测试脚本
"""

import asyncio
import json
from chat_agent import ChatAgent
from models import ConversationState, MessageRole

async def test_intent_classification():
    """测试意图识别"""
    print("🧪 测试意图识别...")
    
    agent = ChatAgent()
    
    # 测试构建问题
    build_questions = [
        "我的Jenkins构建失败了",
        "GitLab CI流水线报错",
        "编译时出现错误",
        "构建过程中遇到问题"
    ]
    
    for question in build_questions:
        state = ConversationState(session_id="test_session")
        state.add_message(MessageRole.USER, question)
        
        # 运行意图识别
        result = await agent.intent_classification_node(state)
        print(f"问题: {question}")
        print(f"识别意图: {result.current_intent.value}")
        print("-" * 50)
    
    # 测试一般问题
    general_questions = [
        "如何优化应用性能？",
        "数据库连接问题",
        "部署应用的方法",
        "代码审查流程"
    ]
    
    for question in general_questions:
        state = ConversationState(session_id="test_session")
        state.add_message(MessageRole.USER, question)
        
        result = await agent.intent_classification_node(state)
        print(f"问题: {question}")
        print(f"识别意图: {result.current_intent.value}")
        print("-" * 50)

async def test_knowledge_base():
    """测试知识库查询"""
    print("\n🧪 测试知识库查询...")
    
    agent = ChatAgent()
    
    # 测试构建错误查询
    build_query = "构建失败怎么办？"
    state = ConversationState(session_id="test_session")
    state.build_errors = ["BUILD FAILED", "Compilation failed"]
    state.add_message(MessageRole.USER, build_query)
    
    result = await agent.search_knowledge_base_node(state)
    print(f"查询: {build_query}")
    print(f"构建错误: {result.build_errors}")
    print(f"知识库结果数量: {len(result.knowledge_base_results)}")
    for i, kb_result in enumerate(result.knowledge_base_results[:2], 1):
        print(f"  {i}. {kb_result['question']}")
    print("-" * 50)
    
    # 测试一般问题查询
    general_query = "如何优化应用性能？"
    state = ConversationState(session_id="test_session")
    state.add_message(MessageRole.USER, general_query)
    
    result = await agent.search_knowledge_base_node(state)
    print(f"查询: {general_query}")
    print(f"知识库结果数量: {len(result.knowledge_base_results)}")
    for i, kb_result in enumerate(result.knowledge_base_results[:2], 1):
        print(f"  {i}. {kb_result['question']}")
    print("-" * 50)

async def test_build_log_extraction():
    """测试构建日志链接提取"""
    print("\n🧪 测试构建日志链接提取...")
    
    agent = ChatAgent()
    
    test_messages = [
        "构建日志链接是 https://jenkins.example.com/build/123",
        "这是GitLab CI的链接: http://gitlab.com/project/-/jobs/456",
        "没有链接的消息",
        "访问 https://github.com/actions/runs/789 查看详情"
    ]
    
    for message in test_messages:
        url = agent.intent_classifier.extract_build_log_url(message)
        print(f"消息: {message}")
        print(f"提取链接: {url if url else '无'}")
        print("-" * 50)

async def test_full_conversation():
    """测试完整对话流程"""
    print("\n🧪 测试完整对话流程...")
    
    agent = ChatAgent()
    
    # 模拟构建问题对话
    print("📝 构建问题对话测试:")
    state = await agent.process_message("我的Jenkins构建失败了", "test_build_session")
    
    # 检查状态
    print(f"当前意图: {state.current_intent.value if state.current_intent else 'None'}")
    print(f"等待构建日志: {state.waiting_for_build_log}")
    print(f"消息数量: {len(state.messages)}")
    
    # 模拟提供构建日志
    print("\n📝 提供构建日志:")
    state = await agent.process_message("https://jenkins.example.com/build/123", "test_build_session")
    
    print(f"构建日志URL: {state.build_log_url}")
    print(f"构建错误: {state.build_errors}")
    print(f"知识库结果: {len(state.knowledge_base_results)}")
    
    # 模拟一般问题对话
    print("\n📝 一般问题对话测试:")
    state = await agent.process_message("如何优化应用性能？", "test_general_session")
    
    print(f"当前意图: {state.current_intent.value if state.current_intent else 'None'}")
    print(f"知识库结果: {len(state.knowledge_base_results)}")
    print(f"消息数量: {len(state.messages)}")

def test_knowledge_base_creation():
    """测试知识库创建"""
    print("\n🧪 测试知识库创建...")
    
    from knowledge_base import KnowledgeBase
    
    kb = KnowledgeBase()
    
    # 添加新知识
    kb.add_knowledge(
        category="build_errors",
        keywords=["Docker build failed", "镜像构建失败"],
        question="Docker镜像构建失败怎么办？",
        answer="Docker构建失败解决方案：1. 检查Dockerfile语法 2. 确认基础镜像存在 3. 检查网络连接 4. 清理Docker缓存"
    )
    
    # 测试查询
    results = kb.search_knowledge("Docker构建失败", ["Docker build failed"])
    print(f"新增知识查询结果: {len(results)}")
    for result in results:
        print(f"  - {result['question']}: {result['answer'][:50]}...")

async def main():
    """主测试函数"""
    print("🚀 开始系统功能测试\n")
    
    try:
        await test_intent_classification()
        await test_knowledge_base()
        await test_build_log_extraction()
        await test_full_conversation()
        test_knowledge_base_creation()
        
        print("\n✅ 所有测试完成！")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
