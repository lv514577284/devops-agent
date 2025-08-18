from typing import Dict, Any, List
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from models import ConversationState, IntentType, MessageRole
from intent_classifier import IntentClassifier
from build_log_service import BuildLogService
from knowledge_base import KnowledgeBase
from llm_service import LLMService
import uuid
import asyncio

class ChatAgent:
    def __init__(self):
        self.intent_classifier = IntentClassifier()
        self.build_log_service = BuildLogService()
        self.knowledge_base = KnowledgeBase()
        self.llm_service = LLMService()
        
        # 创建状态图
        self.graph = self.create_graph()
        
        # 创建内存保存器
        self.memory = MemorySaver()
        
        # 编译图
        self.app = self.graph.compile(checkpointer=self.memory)
    
    def create_graph(self) -> StateGraph:
        """创建LangGraph状态图"""
        workflow = StateGraph(ConversationState)
        
        # 添加节点
        workflow.add_node("intent_classification", self.intent_classification_node)
        workflow.add_node("request_build_log", self.request_build_log_node)
        workflow.add_node("extract_build_log", self.extract_build_log_node)
        workflow.add_node("query_build_errors", self.query_build_errors_node)
        workflow.add_node("search_knowledge_base", self.search_knowledge_base_node)
        workflow.add_node("generate_response", self.generate_response_node)
        
        # 设置入口点
        workflow.set_entry_point("intent_classification")
        
        # 添加条件边
        workflow.add_conditional_edges(
            "intent_classification",
            self.route_after_intent,
            {
                "build": "request_build_log",
                "general": "search_knowledge_base"
            }
        )
        
        workflow.add_conditional_edges(
            "request_build_log",
            self.route_after_build_log_request,
            {
                "has_url": "extract_build_log",
                "no_url": END
            }
        )
        
        workflow.add_conditional_edges(
            "extract_build_log",
            self.route_after_extract_build_log,
            {
                "extracted": "query_build_errors",
                "not_extracted": "request_build_log"
            }
        )
        
        # 添加普通边
        workflow.add_edge("query_build_errors", "search_knowledge_base")
        workflow.add_edge("search_knowledge_base", "generate_response")
        workflow.add_edge("generate_response", END)
        
        return workflow
    
    async def intent_classification_node(self, state: ConversationState) -> ConversationState:
        """意图识别节点"""
        print("正在识别用户意图...")
        
        if not state.messages:
            return state
        
        user_message = state.messages[-1].content
        intent = await self.intent_classifier.classify_intent(user_message)
        
        state.current_intent = intent
        print(f"识别到意图: {intent.value}")
        
        return state
    
    async def request_build_log_node(self, state: ConversationState) -> ConversationState:
        """请求构建日志节点"""
        print("正在检查用户消息中是否包含构建日志链接...")
        
        if not state.messages:
            return state
        
        # 检查用户消息中是否已经包含构建日志链接
        user_message = state.messages[-1].content
        build_log_url = self.intent_classifier.extract_build_log_url(user_message)
        
        if build_log_url:
            # 用户已经提供了构建日志链接，直接提取并跳过请求步骤
            print(f"检测到用户已提供构建日志链接: {build_log_url}")
            state.build_log_url = build_log_url
            state.waiting_for_build_log = False
            
            # 生成一个确认消息而不是请求消息
            confirm_message = f"我检测到您提供的构建日志链接: {build_log_url}。正在分析构建日志中的错误信息..."
            state.add_message(MessageRole.ASSISTANT, confirm_message)
        else:
            # 用户没有提供构建日志链接，请求用户提供
            print("用户消息中未找到构建日志链接，请求用户提供...")
            request_message = await self.llm_service.generate_build_log_request()
            state.add_message(MessageRole.ASSISTANT, request_message)
            state.waiting_for_build_log = True
        
        return state
    
    async def extract_build_log_node(self, state: ConversationState) -> ConversationState:
        """提取构建日志链接节点"""
        print("正在提取构建日志链接...")
        
        if not state.messages:
            return state
        
        user_message = state.messages[-1].content
        build_log_url = self.intent_classifier.extract_build_log_url(user_message)
        
        if build_log_url:
            state.build_log_url = build_log_url
            state.waiting_for_build_log = False
            print(f"提取到构建日志链接: {build_log_url}")
        else:
            print("未找到构建日志链接")
        
        return state
    
    async def query_build_errors_node(self, state: ConversationState) -> ConversationState:
        """查询构建错误节点"""
        print("正在查询构建日志中的错误关键字...")
        
        if not state.build_log_url:
            return state
        
        # 使用模拟服务进行测试，实际使用时替换为真实API调用
        build_errors = await self.build_log_service.mock_query_build_errors(state.build_log_url)
        state.build_errors = build_errors
        
        print(f"查询到错误关键字: {build_errors}")
        
        return state
    
    async def search_knowledge_base_node(self, state: ConversationState) -> ConversationState:
        """搜索知识库节点"""
        print("正在查询知识库...")
        
        if not state.messages:
            return state
        
        user_question = state.messages[-1].content
        
        try:
            # 根据意图和构建错误搜索知识库
            if state.current_intent == IntentType.BUILD and state.build_errors:
                results = self.knowledge_base.search_knowledge(user_question, state.build_errors)
            else:
                results = self.knowledge_base.search_knowledge(user_question)
            
            # 确保knowledge_base_results属性存在
            if not hasattr(state, 'knowledge_base_results'):
                state.knowledge_base_results = []
            
            state.knowledge_base_results = results
            print(f"知识库搜索结果数量: {len(results)}")
            
        except Exception as e:
            print(f"知识库搜索错误: {e}")
            state.knowledge_base_results = []
        
        return state
    
    async def generate_response_node(self, state: ConversationState) -> ConversationState:
        """生成回答节点"""
        print("正在生成回答...")
        
        if not state.messages:
            return state
        
        user_question = state.messages[-1].content
        response = await self.llm_service.generate_response(state, user_question)
        
        # 打印生成的回答内容
        print(f"生成的回答内容: {response}")
        print(f"回答长度: {len(response) if response else 0} 字符")
        
        state.add_message(MessageRole.ASSISTANT, response)
        print("回答生成完成")
        
        return state
    
    def route_after_intent(self, state: ConversationState) -> str:
        """意图识别后的路由"""
        if state.current_intent == IntentType.BUILD:
            return "build"
        else:
            return "general"
    
    def route_after_build_log_request(self, state: ConversationState) -> str:
        """构建日志请求后的路由"""
        # 如果已经设置了构建日志URL，说明用户已经提供了链接
        if state.build_log_url:
            return "has_url"
        
        # 如果还在等待构建日志，说明用户没有提供链接
        if state.waiting_for_build_log:
            return "no_url"
        
        # 检查用户消息中是否包含构建日志链接
        if not state.messages:
            return "no_url"
        
        user_message = state.messages[-1].content
        build_log_url = self.intent_classifier.extract_build_log_url(user_message)
        
        if build_log_url:
            return "has_url"
        else:
            return "no_url"
    
    def route_after_extract_build_log(self, state: ConversationState) -> str:
        """提取构建日志后的路由"""
        if state.build_log_url:
            return "extracted"
        else:
            return "not_extracted"
    
    async def process_message(self, message: str, session_id: str = None) -> ConversationState:
        """处理用户消息"""
        if not session_id:
            session_id = str(uuid.uuid4())
        
        # 使用完整的LangGraph工作流处理
        config = {"configurable": {"thread_id": session_id}}
        
        # 添加用户消息到状态
        state = ConversationState(session_id=session_id)
        state.add_message(MessageRole.USER, message)
        
        # 运行完整的图处理流程
        result = await self.app.ainvoke(state, config)
        
        return result
    
    async def process_streaming_message(self, message: str, session_id: str = None):
        """处理流式消息"""
        if not session_id:
            session_id = str(uuid.uuid4())
        
        # 创建或获取会话状态
        config = {"configurable": {"thread_id": session_id}}
        
        # 添加用户消息到状态
        state = ConversationState(session_id=session_id)
        state.add_message(MessageRole.USER, message)
        
        # 保存最后一个有效的状态
        last_valid_state = state
        
        # 运行图并流式输出
        async for event in self.app.astream(state, config):
            for node_name, node_state in event.items():
                if node_name == "__end__":
                    continue
                
                # 保存每个节点的状态，最后一个就是最终状态
                if node_state is not None:
                    last_valid_state = node_state
                
                # 根据节点名称输出对应的处理步骤
                if node_name == "intent_classification":
                    yield "正在识别用户意图..."
                elif node_name == "request_build_log":
                    if hasattr(node_state, 'build_log_url') and node_state.build_log_url:
                        yield f"检测到构建日志链接: {node_state.build_log_url}"
                    else:
                        yield "正在请求用户提供构建日志链接..."
                elif node_name == "extract_build_log":
                    yield "正在提取构建日志链接..."
                elif node_name == "query_build_errors":
                    yield "正在查询构建日志中的错误关键字..."
                elif node_name == "search_knowledge_base":
                    yield "正在查询知识库..."
                elif node_name == "generate_response":
                    yield "正在生成回答..."
                else:
                    yield f"正在执行: {node_name}..."
        
        # 流程完成后，从最后一个有效状态中获取最终答案
        print(f"流程完成，last_valid_state类型: {type(last_valid_state)}")
        assistant_message_content = ""
        
        if last_valid_state:
            messages = None
            if isinstance(last_valid_state, ConversationState):
                messages = last_valid_state.messages
            elif isinstance(last_valid_state, dict) and 'messages' in last_valid_state:
                messages = last_valid_state['messages']
            
            if messages:
                print(f"从状态中找到 {len(messages)} 条消息")
                for msg_item in reversed(messages):
                    if isinstance(msg_item, dict) and msg_item.get('role') == 'assistant':
                        assistant_message_content = msg_item.get('content', '')
                        break
                    elif hasattr(msg_item, 'role') and msg_item.role.value == 'assistant':
                        assistant_message_content = msg_item.content
                        break
            else:
                print("状态中没有找到消息列表或消息列表为空")
        else:
            print("last_valid_state为None")
        
        if assistant_message_content:
            print(f"找到助手消息，内容长度: {len(assistant_message_content)}")
            # 流式输出回答内容
            chunk_size = 50  # 每次输出50个字符
            for i in range(0, len(assistant_message_content), chunk_size):
                chunk = assistant_message_content[i:i + chunk_size]
                yield chunk
                await asyncio.sleep(0.1)  # 控制输出速度
        else:
            print("未找到最终结果或消息")
