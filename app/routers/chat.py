from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List

from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from app.models.types import ChatMessage
from app.db import db

router = APIRouter(
    prefix="/chat",
    tags=["聊天模块"]
)

# 当前所有 WebSocket 连接
active_connections: List[WebSocket] = []

async def connect(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)

async def disconnect(websocket: WebSocket):
    if websocket in active_connections:
        active_connections.remove(websocket)

# 广播给所有在线用户
async def broadcast(message: dict):
    for conn in active_connections:
        try:
            await conn.send_json(message)
        except:
            await disconnect(conn)  # 如果发送失败，移除连接

@router.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    await connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            msg = ChatMessage(**data)
            await db.messages.insert_one(msg.model_dump())  # 存入 MongoDB
            await broadcast(msg.model_dump())               # 广播消息
    except WebSocketDisconnect:
        await disconnect(websocket)

# GET API：获取聊天记录（用于 Swagger）
@router.get("/history")
async def get_history():
    messages = []
    async for msg in db.messages.find():
        msg["_id"] = str(msg["_id"])  # 转换 ObjectId 为字符串
        messages.append(msg)
    json_data = jsonable_encoder(messages)
    return JSONResponse(content=json_data)
