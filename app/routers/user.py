from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.models.types import UserCreate, UserInDB, UserBase, UserLogin
from app.db import db  # 你连接 MongoDB 的地方
from datetime import datetime, timezone
from pymongo.errors import DuplicateKeyError
import hashlib
import bcrypt


router = APIRouter(prefix="/user", tags=["user"])

# 简单的密码加密函数
def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

# 注册接口

@router.post("/register", response_model=UserBase)
async def register_user(user: UserCreate):
    existing = await db.users.find_one({"username": user.username})
    if existing:
        raise HTTPException(status_code=400, detail="用户名已被注册")
    
    user_dict = user.model_dump()
    user_dict["password"] = hash_password(user.password)
    user_dict["created_at"] = datetime.now(timezone.utc)
    user_dict["status"] = "offline"

    result = await db.users.insert_one(user_dict)
    return UserBase(**user_dict)

class UserPublic(BaseModel):
    id: str
    username: str
    avatar: Optional[str] = None

@router.post("/login",response_model= UserPublic)
async def login_user(user: UserLogin):
    user_data = await db.users.find_one({"username": user.username})
    
    if not user_data:
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    # 验证密码
    stored_hash = user_data["password"]
    if not bcrypt.checkpw(user.password.encode('utf-8'), stored_hash.encode('utf-8')):
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    return {
        "id": str(user_data["_id"]),
        "username": user_data["username"],
        "avatar": user_data.get("avatar")
    }
