from typing import List, Dict, Any, AsyncGenerator
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage, SystemMessage
from models import ConversationState
from config import config
import asyncio

class LLMService:
    def __init__(self):
        # self.llm = ChatOpenAI(
        #     model=config.OPENAI_MODEL,
        #     api_key=config.OPENAI_API_KEY,
        #     temperature=0.7,
        #     streaming=True
        # )
        self.llm = ChatOpenAI(
            model="qwq-32b",  # 百炼云上的模型名称
            api_key="sk-d61a92f522dd49ffa38787277dc6e65b",  # 百炼云 API Key
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",  # 百炼云的 API 地址
            temperature=0.7,
            streaming=True  # 百炼云模型要求必须启用流式模式
        )
        
        self.system_prompt = """你是一个专业的智能助手，专门帮助用户解决技术问题。

你的回答应该：
1. 准确、专业、易懂
2. 基于提供的知识库信息
3. 结合用户的具体问题
4. 提供实用的解决方案
5. 如果知识库信息不足，可以补充一般性建议

请用中文回答，保持友好和专业的语调。"""
    
    def format_context(self, state: ConversationState) -> str:
        """格式化上下文信息"""
        context_parts = []
        
        # 添加知识库搜索结果
        if state.knowledge_base_results:
            context_parts.append("相关知识点：")
            for i, result in enumerate(state.knowledge_base_results[:3], 1):
                context_parts.append(f"{i}. 问题：{result['question']}")
                context_parts.append(f"   答案：{result['answer']}")
        
        # 添加构建错误信息
        if state.build_errors:
            context_parts.append(f"构建错误关键字：{', '.join(state.build_errors)}")
        
        # 添加对话历史
        if state.messages:
            context_parts.append("对话历史：")
            context_parts.append(state.get_context())
        
        return "\n".join(context_parts)
    
    async def generate_response(self, state: ConversationState, user_question: str, context_info: List[str] = None) -> str:
        """生成回答"""
        # 构建上下文信息
        context_parts = []
        
        # 添加自定义上下文信息
        if context_info:
            context_parts.extend(context_info)
        
        # 添加知识库搜索结果
        if state.knowledge_base_results:
            context_parts.append("相关知识点：")
            for i, result in enumerate(state.knowledge_base_results[:3], 1):
                context_parts.append(f"{i}. 问题：{result['question']}")
                context_parts.append(f"   答案：{result['answer']}")
        
        # 添加构建错误信息
        if state.build_errors:
            context_parts.append(f"构建错误关键字：{', '.join(state.build_errors)}")
        
        # 添加对话历史
        if state.messages:
            context_parts.append("对话历史：")
            context_parts.append(state.get_context())
        
        context = "\n".join(context_parts)
        
        prompt = f"""系统提示：{self.system_prompt}

上下文信息：
{context}

用户问题：{user_question}

请基于以上信息，为用户提供专业、准确的回答："""
        
        print(f"发送给LLM的提示词: {prompt[:200]}...")
        print(f"提示词总长度: {len(prompt)} 字符")
        
        try:
            response = await self.llm.ainvoke([
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=f"上下文信息：\n{context}\n\n用户问题：{user_question}")
            ])
            
            print(f"LLM原始响应: {response}")
            print(f"LLM响应内容: {response.content}")
            print(f"LLM响应类型: {type(response)}")
            
            return response.content
            
        except Exception as e:
            print(f"LLM调用失败: {e}")
            print(f"错误类型: {type(e)}")
            print(f"错误详情: {str(e)}")
            return "抱歉，我暂时无法回答您的问题，请稍后再试。"
    
    async def generate_streaming_response(self, state: ConversationState, user_question: str) -> AsyncGenerator[str, None]:
        """生成流式回答"""
        context = self.format_context(state)
        
        try:
            async for chunk in self.llm.astream([
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=f"上下文信息：\n{context}\n\n用户问题：{user_question}")
            ]):
                if chunk.content:
                    yield chunk.content
                    
        except Exception as e:
            print(f"流式LLM调用失败: {e}")
            yield "抱歉，我暂时无法回答您的问题，请稍后再试。"
    
    async def generate_build_log_request(self) -> str:
        """生成请求流水线实例ID的消息"""
        return """我检测到您的问题与构建相关。为了更好地帮助您解决问题，请提供流水线实例ID (cdInstId)。

流水线实例ID通常可以从以下地方获取：
- Jenkins构建页面
- GitLab CI/CD流水线
- GitHub Actions
- 其他CI/CD平台

请将流水线实例ID粘贴在下方，我将查询相关的构建日志错误信息并为您提供解决方案。"""
