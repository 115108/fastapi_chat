from bson import ObjectId
from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.db import db
from app.models.types import RoomCreate, PrivateRoomCreate, Room

import uuid

router = APIRouter(
    prefix="/rooms",
    tags=["rooms"]
)


@router.post("/create", response_model=dict)
async def create_group_room(data: RoomCreate):
    room_id = str(uuid.uuid4())
    room = Room(
        type="group",
        name=data.name,
        members=data.members,
        created_at=datetime.now(timezone.utc)
    )
    await db.room.insert_one(room.model_dump(by_alias=True))
    return {"room_id": room_id}


@router.post("/private", response_model=dict)
async def create_private_room(data: PrivateRoomCreate):
    user1 = await db.user.find_one({"_id": ObjectId(data.user1)})
    user2 = await db.user.find_one({"_id": ObjectId(data.user2)})

    if not user1 or not user2:
      raise HTTPException(status_code=404, detail="用户不存在")

    members = sorted([data.user1, data.user2])

    existing = await db.room.find_one({"_id": room_id})
    if not existing:
        room = Room(
            type="private",
            name="",
            members=members,
            created_at=datetime.now(timezone.utc)
        )
        result = await db.room.insert_one(room.model_dump(by_alias=True))
        
        room_id = str(result.inserted_id)
        
        await db.user.update_many(
        {"_id": {"$in": [ObjectId(data.user1), ObjectId(data.user2)]}},  # 多个用户
        {"$addToSet": {"room_ids": room_id}}  # 加入 room_ids 列表（防重复）
        )

    return {"room_id": room_id}


@router.get("/{room_id}", response_model=Room)
async def get_room_by_id(room_id: str):
    room = await db.room.find_one({"_id": room_id})
    if not room:
        raise HTTPException(status_code=404, detail="房间不存在")
    return Room(**room)
