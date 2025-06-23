from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from motor.motor_asyncio import AsyncIOMotorDatabase
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import verify_token
from app.core.config import settings
from app.db.postgres.session import get_session
from app.repository.postgres.crud import get_user_profile_by_email, get_user_profile_by_id
from app.db.mongo.db import get_mongo


async def user_info_get(
    user_id: int,
    token: str,
    session: AsyncSession = Depends(get_session),
    mongo_db: AsyncIOMotorDatabase = Depends(get_mongo)
):
    # ========== Проверка токена и получение текущего пользователя ==========
    try:
        payload = verify_token(token, settings.public_key_path)
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="Invalid token")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = await get_user_profile_by_email(email, session)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    # ==============================

    # ========== Получение профиля запрашиваемого пользователя ==========
    search_user = await get_user_profile_by_id(user_id, session)
    if not search_user:
        raise HTTPException(status_code=404, detail="Requested user not found")
    # ==============================

    # ========== Проверка наличия чата между пользователями в MongoDB ==========
    chats_collection = mongo_db["chats"]
    # Поиск чата, где user.id и search_user.id участвуют (в любом порядке)
    chat = await chats_collection.find_one({
        "$or": [
            {"user1_id": user.id, "user2_id": search_user.id},
            {"user1_id": search_user.id, "user2_id": user.id}
        ]
    })
    # if not chat:
    #     raise HTTPException(
    #         status_code=403,
    #         detail="No chat found between the current user and the requested user"
    #     )
    # ==============================

    # ========== Формирование и возврат данных ==========
    data = {
        "id": search_user.id,
        "nickname": search_user.nickname,
        "unique_name": search_user.unique_name,
        "last_seen": search_user.last_seen,
        "online_status": search_user.online_status
    }
    return data
    # ==============================