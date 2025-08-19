from typing import Any, Dict, List, Optional, Sequence, Union
from langgraph.checkpoint.memory import BaseCheckpointSaver
from langgraph.checkpoint.memory import MemorySaver
from database_service import DatabaseService
from models import ConversationState
import json

class DatabaseCheckpointer(BaseCheckpointSaver):
    """基于数据库的检查点保存器"""
    
    def __init__(self, database_service: DatabaseService):
        self.db_service = database_service
        self.memory_saver = MemorySaver()  # 作为内存缓存
    
    def get(self, config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """获取检查点"""
        session_id = config.get("configurable", {}).get("session_id")
        if not session_id:
            return None
        
        # 从数据库加载会话状态
        state = self.db_service.load_conversation_state(session_id)
        if not state:
            return None
        
        # 转换为LangGraph格式
        return {
            "config": config,
            "checkpoint": {
                "values": {
                    "state": state.dict()
                },
                "metadata": {
                    "session_id": session_id,
                    "timestamp": state.messages[-1].timestamp.isoformat() if state.messages else None
                }
            }
        }
    
    def put(self, config: Dict[str, Any], checkpoint: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None) -> None:
        """保存检查点"""
        session_id = config.get("configurable", {}).get("session_id")
        if not session_id:
            return
        
        # 从检查点中提取状态
        state_data = checkpoint.get("values", {}).get("state", {})
        if not state_data:
            return
        
        # 转换为ConversationState对象
        try:
            state = ConversationState(**state_data)
            # 保存到数据库
            self.db_service.save_conversation_state(state)
        except Exception as e:
            print(f"保存检查点时出错: {e}")
    
    def list(self, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """列出检查点"""
        # 获取会话列表
        conversations = self.db_service.get_conversation_list()
        return [
            {
                "config": {"configurable": {"session_id": conv["session_id"]}},
                "metadata": {
                    "session_id": conv["session_id"],
                    "created_at": conv["created_at"],
                    "updated_at": conv["updated_at"]
                }
            }
            for conv in conversations
        ]
    
    def delete(self, config: Dict[str, Any]) -> None:
        """删除检查点"""
        session_id = config.get("configurable", {}).get("session_id")
        if session_id:
            self.db_service.delete_conversation(session_id)
    
    def delete_thread(self, config: Dict[str, Any]) -> None:
        """删除线程（别名）"""
        self.delete(config)
    
    def get_tuple(self, config: Dict[str, Any]) -> Optional[tuple]:
        """获取检查点元组"""
        result = self.get(config)
        if result:
            return (result["checkpoint"]["values"], result["checkpoint"]["metadata"])
        return None
    
    def put_writes(self, config: Dict[str, Any], writes: List[Dict[str, Any]]) -> None:
        """批量写入"""
        for write in writes:
            self.put(config, write)
