import mysql.connector
from mysql.connector import pooling
from typing import List, Dict, Any, Optional
import json
from datetime import datetime
from models import ConversationState, Message, MessageRole, IntentType
import uuid

class DatabaseService:
    def __init__(self, host='localhost', port=3306, user='root', 
                 password='Paomoxiashang0.', database='mydatabase'):
        self.db_config = {
            'host': host,
            'port': port,
            'user': user,
            'password': password,
            'database': database,
            'charset': 'utf8mb4',
            'autocommit': True,
            'raise_on_warnings': True
        }
        
        print(f"正在连接数据库: {host}:{port}, 数据库: {database}")
        
        try:
            # 创建连接池
            self.connection_pool = mysql.connector.pooling.MySQLConnectionPool(
                pool_name="mypool",
                pool_size=5,
                **self.db_config
            )
            
            # 测试连接
            test_connection = self.connection_pool.get_connection()
            test_connection.close()
            print("数据库连接成功！")
            
            # 初始化数据库表
            self._init_tables()
            
        except mysql.connector.Error as e:
            print(f"数据库连接失败: {e}")
            print("请确保:")
            print("1. MySQL服务正在运行")
            print("2. 数据库 'mydatabase' 已创建")
            print("3. 用户名和密码正确")
            print("4. 端口3306未被占用")
            raise
    
    def _init_tables(self):
        """初始化数据库表"""
        connection = self.connection_pool.get_connection()
        cursor = connection.cursor()
        
        try:
            # 创建会话表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    session_id VARCHAR(255) PRIMARY KEY,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    problem_type VARCHAR(50),
                    cd_inst_id VARCHAR(100),
                    problem_desc TEXT,
                    current_intent VARCHAR(50),
                    build_log_url TEXT,
                    build_errors JSON,
                    knowledge_base_results JSON,
                    waiting_for_build_log BOOLEAN DEFAULT FALSE,
                    conversation_history JSON
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            
            # 创建消息表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id VARCHAR(255) PRIMARY KEY,
                    session_id VARCHAR(255) NOT NULL,
                    role VARCHAR(20) NOT NULL,
                    content TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_session_id (session_id),
                    INDEX idx_timestamp (timestamp)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            
            connection.commit()
            print("数据库表初始化完成")
            
        except Exception as e:
            print(f"初始化数据库表时出错: {e}")
            connection.rollback()
        finally:
            cursor.close()
            connection.close()
    
    def save_conversation_state(self, state: ConversationState):
        """保存会话状态"""
        connection = self.connection_pool.get_connection()
        cursor = connection.cursor()
        
        try:
            # 保存会话基本信息
            cursor.execute("""
                INSERT INTO conversations (
                    session_id, problem_type, cd_inst_id, problem_desc, 
                    current_intent, build_log_url, build_errors, 
                    knowledge_base_results, waiting_for_build_log, conversation_history
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) AS new_data
                ON DUPLICATE KEY UPDATE
                    problem_type = new_data.problem_type,
                    cd_inst_id = new_data.cd_inst_id,
                    problem_desc = new_data.problem_desc,
                    current_intent = new_data.current_intent,
                    build_log_url = new_data.build_log_url,
                    build_errors = new_data.build_errors,
                    knowledge_base_results = new_data.knowledge_base_results,
                    waiting_for_build_log = new_data.waiting_for_build_log,
                    conversation_history = new_data.conversation_history,
                    updated_at = CURRENT_TIMESTAMP
            """, (
                state.session_id,
                state.problem_type,
                state.cd_inst_id,
                state.problem_desc,
                state.current_intent.value if state.current_intent else None,
                state.build_log_url,
                json.dumps(state.build_errors, ensure_ascii=False),
                json.dumps(state.knowledge_base_results, ensure_ascii=False),
                state.waiting_for_build_log,
                json.dumps(state.conversation_history, ensure_ascii=False)
            ))
            
            # 保存消息
            for message in state.messages:
                cursor.execute("""
                    INSERT INTO messages (id, session_id, role, content)
                    VALUES (%s, %s, %s, %s) AS new_data
                    ON DUPLICATE KEY UPDATE
                        content = new_data.content,
                        timestamp = CURRENT_TIMESTAMP
                """, (
                    message.id,
                    state.session_id,
                    message.role.value,
                    message.content
                ))
            
            connection.commit()
            
        except Exception as e:
            print(f"保存会话状态时出错: {e}")
            connection.rollback()
        finally:
            cursor.close()
            connection.close()
    
    def load_conversation_state(self, session_id: str) -> Optional[ConversationState]:
        """加载会话状态"""
        connection = self.connection_pool.get_connection()
        cursor = connection.cursor(dictionary=True)
        
        try:
            # 加载会话基本信息
            cursor.execute("""
                SELECT * FROM conversations WHERE session_id = %s
            """, (session_id,))
            
            conv_data = cursor.fetchone()
            if not conv_data:
                return None
            
            # 加载消息
            cursor.execute("""
                SELECT * FROM messages 
                WHERE session_id = %s 
                ORDER BY timestamp ASC
            """, (session_id,))
            
            messages_data = cursor.fetchall()
            
            # 构建ConversationState对象
            state = ConversationState(
                session_id=session_id,
                problem_type=conv_data['problem_type'],
                cd_inst_id=conv_data['cd_inst_id'],
                problem_desc=conv_data['problem_desc'],
                current_intent=IntentType(conv_data['current_intent']) if conv_data['current_intent'] else None,
                build_log_url=conv_data['build_log_url'],
                build_errors=json.loads(conv_data['build_errors']) if conv_data['build_errors'] else [],
                knowledge_base_results=json.loads(conv_data['knowledge_base_results']) if conv_data['knowledge_base_results'] else [],
                waiting_for_build_log=conv_data['waiting_for_build_log'],
                conversation_history=json.loads(conv_data['conversation_history']) if conv_data['conversation_history'] else []
            )
            
            # 添加消息
            for msg_data in messages_data:
                message = Message(
                    id=msg_data['id'],
                    role=MessageRole(msg_data['role']),
                    content=msg_data['content']
                )
                state.messages.append(message)
            
            return state
            
        except Exception as e:
            print(f"加载会话状态时出错: {e}")
            return None
        finally:
            cursor.close()
            connection.close()
    
    def delete_conversation(self, session_id: str):
        """删除会话"""
        connection = self.connection_pool.get_connection()
        cursor = connection.cursor()
        
        try:
            # 删除消息
            cursor.execute("DELETE FROM messages WHERE session_id = %s", (session_id,))
            # 删除会话
            cursor.execute("DELETE FROM conversations WHERE session_id = %s", (session_id,))
            
            connection.commit()
            
        except Exception as e:
            print(f"删除会话时出错: {e}")
            connection.rollback()
        finally:
            cursor.close()
            connection.close()
    
    def get_conversation_list(self, limit: int = 50) -> List[Dict[str, Any]]:
        """获取会话列表"""
        connection = self.connection_pool.get_connection()
        cursor = connection.cursor(dictionary=True)
        
        try:
            cursor.execute("""
                SELECT session_id, created_at, updated_at, problem_type, problem_desc
                FROM conversations 
                ORDER BY updated_at DESC 
                LIMIT %s
            """, (limit,))
            
            return cursor.fetchall()
            
        except Exception as e:
            print(f"获取会话列表时出错: {e}")
            return []
        finally:
            cursor.close()
            connection.close()
