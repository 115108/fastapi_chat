from datetime import datetime, timezone
from fastapi import APIRouter
from app.db import db
from app.models.types import UserCreate

router = APIRouter(
    prefix="/user",
    tags=["用户模块"]
)

@router.get("/all")
async def get_all_users():
    users = []
    async for user in db.users.find():
        user["_id"] = str(user["_id"])  # ObjectId 转字符串
        users.append(user)
    return users

@router.post("/register")
async def register(user: UserCreate):
    # 构造数据库要存的用户数据（加上时间）
    user_data = user.model_dump()
    user_data["created_at"] = datetime.now(timezone.utc)
    user_data["status"] = "offline"

    # 插入到数据库
    result = await db.users.insert_one(user_data)

    return {"message": "注册成功", "user_id": str(result.inserted_id)}
