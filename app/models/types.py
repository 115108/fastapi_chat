import re
from bson import ObjectId
from pydantic import BaseModel, Field, field_validator, validator
from typing import Literal, Optional, List
from datetime import datetime, timezone

# ========================
# ✅ 用户模型
# ========================

# 基础用户信息（公开数据）
class UserBase(BaseModel):
    username: str = Field(
        ..., 
        min_length=3, 
        max_length=20, 
        pattern=r"^[a-zA-Z][a-zA-Z0-9_.-]*$",
        description="用户名",
        example="string" 
    )
    nickname: Optional[str] = Field(None, description="用户昵称")
    avatar: Optional[str] = Field(None, description="头像 URL")
    joined_rooms: List[str] = Field(default_factory=list, description="加入的房间 ID 列表")
    

# 创建用户时的字段（包含密码）
class UserCreate(UserBase):
    password: str = Field(
        ..., 
        min_length=8, 
        max_length=32, 
        description="密码，8-32位，必须包含大小写字母、数字和特殊字符",
        example="string" 
    )

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v):
        if not re.search(r'[a-z]', v):
            raise ValueError("密码必须包含至少一个小写字母")
        if not re.search(r'[A-Z]', v):
            raise ValueError("密码必须包含至少一个大写字母")
        if not re.search(r'\d', v):
            raise ValueError("密码必须包含至少一个数字")
        if not re.search(r'[^a-zA-Z0-9]', v):
            raise ValueError("密码必须包含至少一个特殊字符")
        return v
    
class UserLogin(BaseModel):
    username: str 
    password: str 

# 数据库中存储的完整信息
class UserInDB(UserBase):
    id: Optional[str] = Field(None, alias="_id", description="用户ID（MongoDB _id）")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="创建时间")
    status: Literal["online", "offline"] = Field(default="offline", description="用户在线状态")



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
    id: str = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    type: Literal["group", "private"]
    name: Optional[str] = ""
    members: List[str]
    created_at: datetime

    class Config:
        allow_population_by_field_name = True  # ✅ 允许你用 id=... 创建实例，而不是必须用 _id
        populate_by_name = True                # ✅ pydantic v2 推荐也加上这个（兼容性更好）
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class RoomCreate(BaseModel):
    name: str = ""
    members: List[str]

class PrivateRoomCreate(BaseModel):
    user1: str
    user2: str


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