#!/usr/bin/env python3
"""
测试导入脚本
"""

def test_imports():
    """测试所有模块的导入"""
    try:
        print("测试配置模块...")
        from devops_qa_agent.config import config
        print("✅ 配置模块导入成功")
        
        print("测试模型模块...")
        from devops_qa_agent.models import ChatRequest, ChatResponse
        print("✅ 模型模块导入成功")
        
        print("测试服务模块...")
        from devops_qa_agent.services.chat_service import ChatAgent
        from devops_qa_agent.services.llm_service import LLMService
        from devops_qa_agent.services.intent_service import IntentClassifier
        from devops_qa_agent.services.build_log_service import BuildLogService
        print("✅ 服务模块导入成功")
        
        print("测试知识库模块...")
        from devops_qa_agent.knowledge.base import KnowledgeBase
        print("✅ 知识库模块导入成功")
        
        print("测试API模块...")
        from devops_qa_agent.api.server import app
        print("✅ API模块导入成功")
        
        print("\n🎉 所有模块导入成功！")
        return True
        
    except Exception as e:
        print(f"❌ 导入失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_imports()
