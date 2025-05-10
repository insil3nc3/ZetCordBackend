from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.core.security import verify_token
from app.repository.postgres.crud import get_user_profile_by_email, get_profile_by_unique_name
from app.schemas.v1.mongo.private_chat import PrivateChatCreate, PrivateChatInDB
from app.db.mongo.db import get_mongo
from motor.motor_asyncio import AsyncIOMotorDatabase

async def private_chat_create(user2_unique_name: str, db: AsyncIOMotorDatabase, token: str, session: AsyncSession):
    try:
        payload = verify_token(token, settings.public_key_path)
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="Invalid token")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

    user_profile = await get_user_profile_by_email(email, session)
    user1 = user_profile.id

    user2_profile = await get_profile_by_unique_name(user2_unique_name, session)
    user2 = user2_profile.id
    existing_chat = await db["chats"].find_one({
        "$or": [
            {"user1_id": user1, "user2_id": user2},
            {"user1_id": user2, "user2_id": user1}
        ]
    })

    if existing_chat:
        # Приведение к единому формату
        chat_data = PrivateChatCreate(
            user1_id=existing_chat["user1_id"],
            user2_id=existing_chat["user2_id"]
        )
        chat_dict = chat_data.model_dump()
        chat_dict["_id"] = str(existing_chat["_id"])
        return chat_dict

    chat_data = PrivateChatCreate(user1_id=user1, user2_id=user2)
    chat_dict = chat_data.model_dump()
    result = await db["chats"].insert_one(chat_dict)
    chat_dict["_id"] = str(result.inserted_id)
    return chat_dict