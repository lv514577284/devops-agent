#!/usr/bin/env python3
"""
智能问答系统主启动文件
"""

import uvicorn
from .api.server import app
from .config import config

def main():
    """启动服务器"""
    print("🚀 启动智能问答系统...")
    print(f"📡 服务器地址: http://{config.HOST}:{config.PORT}")
    print(f"🔧 配置信息:")
    print(f"   - OpenAI模型: {config.OPENAI_MODEL}")
    print(f"   - 构建日志API: {config.BUILD_LOG_API_URL}")
    print(f"   - 知识库路径: {config.KNOWLEDGE_BASE_PATH}")
    print(f"   - 流式输出延迟: {config.STREAM_DELAY}秒")
    print("\n✨ 系统功能:")
    print("   ✅ 多轮对话支持")
    print("   ✅ 意图识别")
    print("   ✅ 构建日志分析")
    print("   ✅ 知识库查询")
    print("   ✅ 流式输出")
    print("   ✅ WebSocket实时通信")
    print("\n🌐 访问 http://localhost:8000 开始使用")
    
    uvicorn.run(
        app,
        host=config.HOST,
        port=config.PORT,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    main()
