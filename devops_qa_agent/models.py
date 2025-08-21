from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from enum import Enum
import uuid
from datetime import datetime

class IntentType(str, Enum):
    BUILD = "build"
    GENERAL = "general"

class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class Message(BaseModel):
    id: str = None
    role: MessageRole
    content: str
    timestamp: datetime = None
    
    def __init__(self, **data):
        super().__init__(**data)
        if self.id is None:
            self.id = str(uuid.uuid4())
        if self.timestamp is None:
            self.timestamp = datetime.now()

class ConversationState(BaseModel):
    session_id: str
    messages: List[Message] = []
    current_intent: Optional[IntentType] = None
    build_log_url: Optional[str] = None
    build_errors: List[str] = []
    knowledge_base_results: List[Dict[str, Any]] = []
    waiting_for_build_log: bool = False
    conversation_history: List[Dict[str, Any]] = []
    problem_type: Optional[str] = None
    cd_inst_id: Optional[str] = None
    problem_desc: Optional[str] = None
    
    def add_message(self, role: MessageRole, content: str):
        message = Message(role=role, content=content)
        self.messages.append(message)
        return message
    
    def get_context(self) -> str:
        """获取对话上下文"""
        context = []
        for msg in self.messages[-10:]:  # 只保留最近10条消息
            context.append(f"{msg.role.value}: {msg.content}")
        return "\n".join(context)

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    problemType: Optional[str] = None
    cdInstId: Optional[str] = None
    problemDesc: Optional[str] = None

class ChatResponse(BaseModel):
    session_id: str
    message: str
    is_streaming: bool = False
    status: str = "success"

class StreamResponse(BaseModel):
    session_id: str
    chunk: str
    is_final: bool = False
    status: str = "streaming"
