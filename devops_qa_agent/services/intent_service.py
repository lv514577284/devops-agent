from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from ..models import IntentType
from ..config import config

class IntentClassifier:
    def __init__(self):
        # self.llm = ChatOpenAI(
        #     model=config.OPENAI_MODEL,
        #     api_key=config.OPENAI_API_KEY,
        #     temperature=0.1
        # )


        self.llm = ChatOpenAI(
            model="qwq-32b",  # 百炼云上的模型名称
            api_key="sk-d61a92f522dd49ffa38787277dc6e65b",  # 百炼云 API Key
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",  # 百炼云的 API 地址
            temperature=0.1,
            streaming=True  # 百炼云模型要求必须启用流式模式
        )
        
        self.intent_prompt = ChatPromptTemplate.from_template("""
你是一个专业的意图识别助手。请分析用户的问题，判断其意图类型。

用户问题: {user_question}

请从以下选项中选择最合适的意图类型：
1. build - 构建问题：涉及代码编译、构建失败、构建错误、CI/CD构建、Jenkins构建、GitLab CI、构建日志等
2. general - 一般问题：其他所有类型的问题

请只返回意图类型（build 或 general），不要包含其他内容。

意图类型:""")
    
    async def classify_intent(self, user_question: str) -> IntentType:
        """识别用户问题的意图"""
        try:
            response = await self.llm.ainvoke(
                self.intent_prompt.format(user_question=user_question)
            )
            
            intent_text = response.content.strip().lower()
            
            if "build" in intent_text:
                return IntentType.BUILD
            else:
                return IntentType.GENERAL
                
        except Exception as e:
            print(f"意图识别失败: {e}")
            # 默认返回一般问题
            return IntentType.GENERAL
    
    def extract_build_log_url(self, message: str) -> str:
        """从用户消息中提取构建日志链接"""
        import re
        
        # 匹配常见的URL模式
        url_patterns = [
            r'https?://[^\s]+',
            r'http://[^\s]+',
            r'https://[^\s]+'
        ]
        
        for pattern in url_patterns:
            matches = re.findall(pattern, message)
            if matches:
                return matches[0]
        
        return ""
