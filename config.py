import os
from typing import Optional

class Config:
    # OpenAI配置
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    
    # 外部API配置
    BUILD_LOG_API_URL: str = os.getenv("BUILD_LOG_API_URL", "http://localhost:8001/api/build-log")
    
    # 知识库配置
    KNOWLEDGE_BASE_PATH: str = os.getenv("KNOWLEDGE_BASE_PATH", "./knowledge_base")
    
    # 服务器配置
    HOST: str = os.getenv("HOST", "127.0.0.1")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # 流式输出配置
    STREAM_DELAY: float = 0.05  # 每个字符输出的延迟时间（秒）

config = Config()
