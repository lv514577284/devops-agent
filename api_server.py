from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request
import json
import asyncio
from typing import Dict, List
import uuid

from models import ChatRequest, ChatResponse, StreamResponse
from chat_agent import ChatAgent
from config import config

app = FastAPI(title="智能问答系统", version="1.0.0")

# 创建聊天智能体实例
chat_agent = ChatAgent()

# 存储活跃的WebSocket连接
active_connections: Dict[str, WebSocket] = {}

# 静态文件和模板
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def get_chat_page(request: Request):
    """获取聊天页面"""
    return templates.TemplateResponse("chat.html", {"request": request})

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    """聊天接口 - 流式返回"""
    try:
        if not request.session_id:
            request.session_id = str(uuid.uuid4())
        
        async def generate_response():
            """生成流式响应"""
            try:
                # 流式处理消息
                async for chunk in chat_agent.process_streaming_message(
                    request.message, 
                    request.session_id,
                    request.problemType,
                    request.cdInstId,
                    request.problemDesc
                ):
                    # 返回JSON格式的流式数据
                    yield f"data: {json.dumps({'chunk': chunk, 'session_id': request.session_id})}\n\n"
                    await asyncio.sleep(config.STREAM_DELAY)  # 控制输出速度
                
                # 发送完成信号
                yield f"data: {json.dumps({'complete': True, 'session_id': request.session_id})}\n\n"
                
            except Exception as e:
                # 发送错误信息
                yield f"data: {json.dumps({'error': str(e), 'session_id': request.session_id})}\n\n"
        
        return StreamingResponse(
            generate_response(),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Content-Type": "text/event-stream"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket流式聊天接口"""
    await websocket.accept()
    active_connections[session_id] = websocket
    
    try:
        while True:
            # 接收用户消息
            data = await websocket.receive_text()
            message_data = json.loads(data)
            user_message = message_data.get("message", "")
            
            if not user_message:
                continue
            
            # 发送处理步骤
            await websocket.send_text(json.dumps({
                "type": "status",
                "content": "正在处理您的问题...",
                "session_id": session_id
            }))
            
            # 流式处理消息
            async for chunk in chat_agent.process_streaming_message(user_message, session_id):
                await websocket.send_text(json.dumps({
                    "type": "chunk",
                    "content": chunk,
                    "session_id": session_id
                }))
                await asyncio.sleep(config.STREAM_DELAY)  # 控制输出速度
            
            # 发送完成信号
            await websocket.send_text(json.dumps({
                "type": "complete",
                "content": "",
                "session_id": session_id
            }))
            
    except WebSocketDisconnect:
        if session_id in active_connections:
            del active_connections[session_id]
    except Exception as e:
        await websocket.send_text(json.dumps({
            "type": "error",
            "content": f"处理失败: {str(e)}",
            "session_id": session_id
        }))

@app.get("/api/sessions/{session_id}")
async def get_session_history(session_id: str):
    """获取会话历史"""
    try:
        # 这里应该从持久化存储中获取会话历史
        # 目前返回空历史
        return {
            "session_id": session_id,
            "messages": []
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/sessions/{session_id}")
async def delete_session(session_id: str):
    """删除会话"""
    try:
        # 这里应该从持久化存储中删除会话
        return {"message": "会话已删除", "session_id": session_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api_server:app",
        host=config.HOST,
        port=config.PORT,
        reload=True
    )
