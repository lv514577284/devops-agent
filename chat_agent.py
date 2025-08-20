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
        #workflow.add_node("query_build_errors", self.query_build_errors_node)
        #workflow.add_node("wait_for_inst_id", self.wait_for_inst_id_node)
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
        
        # workflow.add_conditional_edges(
        #     "request_build_log",
        #     self.route_after_build_log_request,
        #     {
        #         "has_inst_id": "query_build_errors",
        #         "no_inst_id": "search_knowledge_base"
        #     }
        # )
        
        # workflow.add_conditional_edges(
        #     "wait_for_inst_id",
        #     self.route_after_wait_for_inst_id,
        #     {
        #         "got_inst_id": "request_build_log",
        #         "still_waiting": END
        #     }
        # )
        
        # 添加普通边
        workflow.add_edge("request_build_log","search_knowledge_base")
        #workflow.add_edge("query_build_errors", "search_knowledge_base")
        workflow.add_edge("search_knowledge_base", "generate_response")
        workflow.add_edge("generate_response", END)
        
        return workflow
    
    async def intent_classification_node(self, state: ConversationState) -> ConversationState:
        """意图识别节点"""
        print("正在识别用户意图...")
        
        # 如果提供了问题类型，直接使用
        if state.problem_type:
            if state.problem_type == "构建":
                state.current_intent = IntentType.BUILD
                print(f"根据问题类型识别到意图: {state.current_intent.value}")
                return state
        
        # 否则从消息内容识别意图
        if not state.messages:
            return state
        
        user_message = state.messages[-1].content
        intent = await self.intent_classifier.classify_intent(user_message)
        
        state.current_intent = intent
        print(f"识别到意图: {intent.value}")
        
        return state
    
    async def request_build_log_node(self, state: ConversationState) -> ConversationState:
        """请求构建日志节点"""
        print("正在检查构建日志信息...")
        
        # 检查是否提供了流水线实例ID
        if state.cd_inst_id:
            print(f"检测到流水线实例ID: {state.cd_inst_id}")
            build_errors = await self.build_log_service.get_build_log_errors_by_inst_id(state.cd_inst_id)
            state.build_errors = build_errors
            print(f"查询到构建日志错误关键字: {build_errors}")
            return state
        
        # 如果没有提供实例ID，设置等待状态
        print("未检测到流水线实例ID，设置等待状态...")
        state.waiting_for_build_log = True
        
        return state
    
    async def query_build_errors_node(self, state: ConversationState) -> ConversationState:
        """查询构建错误节点"""
        print("正在查询构建日志中的错误关键字...")
        
        # 如果已经有构建错误信息，直接返回
        if state.build_errors:
            print(f"已有构建错误信息: {state.build_errors}")
            return state
        
        # 如果没有实例ID，无法查询
        if not state.cd_inst_id:
            print("没有实例ID，无法查询构建错误")
            return state
        
        # 查询构建日志错误
        build_errors = await self.build_log_service.get_build_log_errors_by_inst_id(state.cd_inst_id)
        state.build_errors = build_errors
        
        print(f"查询到错误关键字: {build_errors}")
        
        return state
    
    async def wait_for_inst_id_node(self, state: ConversationState) -> ConversationState:
        """等待用户提供实例ID节点"""
        print("正在等待用户提供流水线实例ID...")
        
        # 检查用户最新消息中是否包含实例ID
        if state.messages:
            user_message = state.messages[-1].content
            
            # 简单的实例ID提取逻辑（可以根据需要改进）
            import re
            # 匹配数字ID模式
            inst_id_pattern = r'\b\d{6,}\b'  # 匹配6位或更多数字
            matches = re.findall(inst_id_pattern, user_message)
            
            if matches:
                # 假设第一个匹配的数字就是实例ID
                state.cd_inst_id = matches[0]
                print(f"从用户消息中提取到实例ID: {state.cd_inst_id}")
                
                # 添加确认消息
                confirm_message = f"已获取到流水线实例ID: {state.cd_inst_id}，正在查询构建日志错误信息..."
                state.add_message(MessageRole.ASSISTANT, confirm_message)
            else:
                # 继续请求实例ID
                request_message = await self.llm_service.generate_build_log_request()
                state.add_message(MessageRole.ASSISTANT, request_message)
        
        return state
    
    async def search_knowledge_base_node(self, state: ConversationState) -> ConversationState:
        """搜索知识库节点"""
        print("正在查询知识库...")
        
        # 确定搜索关键词
        search_keywords = []
        
        # 如果有问题描述，使用问题描述
        if state.problem_desc:
            search_keywords.append(state.problem_desc)
        elif state.messages:
            search_keywords.append(state.messages[-1].content)
        
        # 如果是构建类型的问题，添加构建错误信息
        if state.current_intent == IntentType.BUILD and state.build_errors:
            search_keywords.extend(state.build_errors)
        
        # 组合搜索关键词
        combined_query = " ".join(search_keywords)
        print(f"知识库搜索关键词: {combined_query}")
        
        try:
            # 搜索知识库
            results = self.knowledge_base.search_knowledge(combined_query)
            
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
        
        # 确定用户问题
        user_question = ""
        if state.problem_desc:
            user_question = state.problem_desc
        elif state.messages:
            user_question = state.messages[-1].content
        
        # 构建上下文信息
        context_info = []
        
        # 添加问题描述
        if state.problem_desc:
            context_info.append(f"用户问题描述: {state.problem_desc}")
        
        # 如果是构建类型的问题，添加构建错误信息
        if state.current_intent == IntentType.BUILD and state.build_errors:
            context_info.append(f"构建日志错误关键字: {', '.join(state.build_errors)}")
        
        # 添加知识库搜索结果
        if state.knowledge_base_results:
            context_info.append(f"知识库相关内容: {state.knowledge_base_results}")
        
        # 生成回答
        response = await self.llm_service.generate_response(state, user_question, context_info)
        
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
        # 如果已经设置了构建错误，说明已经查询到了错误信息
        if state.build_errors:
            return "has_inst_id"
        
        # 如果还在等待构建日志，说明用户没有提供实例ID
        if state.waiting_for_build_log:
            return "no_inst_id"
        
        # 检查是否提供了实例ID
        if state.cd_inst_id:
            return "has_inst_id"
        else:
            return "no_inst_id"
    
    def route_after_wait_for_inst_id(self, state: ConversationState) -> str:
        """等待实例ID后的路由"""
        # 如果已经获取到实例ID，继续处理
        if state.cd_inst_id:
            return "got_inst_id"
        else:
            # 继续等待
            return "still_waiting"
    

    
    async def process_message(self, message: str, session_id: str = None, 
                            problem_type: str = None, cd_inst_id: str = None, 
                            problem_desc: str = None) -> ConversationState:
        """处理用户消息"""
        if not session_id:
            session_id = str(uuid.uuid4())
        
        # 使用完整的LangGraph工作流处理
        config = {"configurable": {"thread_id": session_id}}
        
        # 尝试从检查点恢复历史状态
        state = None
        try:
            # 获取检查点中的历史状态
            checkpoint = await self.memory.aget_tuple(config)
            if checkpoint and checkpoint.checkpoint:
                # 如果有历史状态，从中恢复
                historical_state = checkpoint.checkpoint.get('channel_values', {})
                if historical_state:
                    # 从历史状态创建ConversationState对象
                    state = ConversationState(**historical_state)
                    print(f"从检查点恢复状态，包含 {len(state.messages)} 条历史消息")
                else:
                    # 没有历史状态，创建新的
                    state = ConversationState(session_id=session_id)
                    print("创建新的对话状态")
            else:
                # 没有检查点，创建新的状态
                state = ConversationState(session_id=session_id)
                print("创建新的对话状态")
        except Exception as e:
            print(f"恢复状态失败: {e}，创建新的状态")
            state = ConversationState(session_id=session_id)
        
        # 添加当前用户消息
        state.add_message(MessageRole.USER, message)
        print(f"添加用户消息后，总消息数: {len(state.messages)}")
        
        # 设置新的字段
        if problem_type:
            state.problem_type = problem_type
        if cd_inst_id:
            state.cd_inst_id = cd_inst_id
        if problem_desc:
            state.problem_desc = problem_desc
        
        # 运行完整的图处理流程
        result = await self.app.ainvoke(state, config)
        
        return result
    
    async def process_streaming_message(self, message: str, session_id: str = None,
                                      problem_type: str = None, cd_inst_id: str = None,
                                      problem_desc: str = None):
        """处理流式消息"""
        if not session_id:
            session_id = str(uuid.uuid4())
        
        # 创建或获取会话状态
        config = {"configurable": {"thread_id": session_id}}
        
        # 尝试从检查点恢复历史状态
        state = None
        try:
            # 获取检查点中的历史状态
            checkpoint = await self.memory.aget_tuple(config)
            if checkpoint and checkpoint.checkpoint:
                # 如果有历史状态，从中恢复
                historical_state = checkpoint.checkpoint.get('channel_values', {})
                if historical_state:
                    # 从历史状态创建ConversationState对象
                    state = ConversationState(**historical_state)
                    print(f"从检查点恢复状态，包含 {len(state.messages)} 条历史消息")
                else:
                    # 没有历史状态，创建新的
                    state = ConversationState(session_id=session_id)
                    print("创建新的对话状态")
            else:
                # 没有检查点，创建新的状态
                state = ConversationState(session_id=session_id)
                print("创建新的对话状态")
        except Exception as e:
            print(f"恢复状态失败: {e}，创建新的状态")
            state = ConversationState(session_id=session_id)
        
        # 添加当前用户消息
        state.add_message(MessageRole.USER, message)
        print(f"添加用户消息后，总消息数: {len(state.messages)}")
        
        # 设置新的字段
        if problem_type:
            state.problem_type = problem_type
        if cd_inst_id:
            state.cd_inst_id = cd_inst_id
        if problem_desc:
            state.problem_desc = problem_desc
        
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
                    yield "已完成识别用户意图...\n"
                elif node_name == "request_build_log":
                    yield "已完成查询构建日志...\n"
                elif node_name == "search_knowledge_base":
                    yield "已完成查询知识库...\n"
                elif node_name == "generate_response":
                    yield "已完成生成回答...\n"
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
