from pydantic import BaseModel, Field
from typing import Literal, Optional, List
from datetime import datetime, timezone

# ========================
# ✅ 用户模型
# ========================

class UserBase(BaseModel):
    username: str                             # 用户名（唯一）
    nickname: Optional[str] = None            # 昵称
    avatar: Optional[str] = None              # 头像 URL

class UserCreate(UserBase):
    password: str                             # 注册或登录时的密码（需要后端加密）

class UserInDB(UserBase):
    id: Optional[str] = None                  # 用户 ID（MongoDB 中是 _id）
    created_at: datetime                      # 创建时间
    status: Optional[str] = "offline"         # 当前状态：online / offline


# ========================
# 💬 消息模型
# ========================

class Message(BaseModel):
    room_id: str                              # 所属房间的 ID
    sender_id: str                            # 发送者用户 ID
    content: str                              # 消息内容
    message_type: str = "text"                # 消息类型：text / image / file / emoji 等
    timestamp: datetime                       # 发送时间
    read_by: Optional[List[str]] = []         # 已读用户 ID 列表


# ========================
# 🏠 聊天房间模型
# ========================

class Room(BaseModel):
    type: str                                 # 房间类型：private / group
    members: List[str]                        # 成员用户 ID 列表
    created_at: datetime                      # 房间创建时间
    last_message: Optional[str] = None        # 最后一条消息内容（用于列表预览）


# ========================
# 🔑 Token 数据模型（用于验证）
# ========================

class TokenData(BaseModel):
    user_id: str                              # 用户 ID
    exp: datetime                             # Token 过期时间

class ChatMessage(BaseModel):
    sender_id: str                      # 发送者ID
    content: str                        # 消息内容
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))  # UTC时间
    type: Literal["text"] = "text"      # 消息类型（目前仅支持文本）