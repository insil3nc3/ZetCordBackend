from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from motor.motor_asyncio import AsyncIOMotorDatabase
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import verify_token
from app.core.config import settings
from app.db.postgres.session import get_session
from app.repository.postgres.crud import get_user_profile_by_email, get_user_profile_by_id, \
    get_profile_by_unique_name
from app.db.mongo.db import get_mongo

async def user_get_info_by_unique_name(user_name, token, session):
    # ========== Проверка токена и получение текущего пользователя ==========
    try:
        payload = verify_token(token, settings.public_key_path)
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="Invalid token")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")
    # ==============================

    # ========== Получение профиля запрашиваемого пользователя ==========
    search_user = await get_profile_by_unique_name(user_name, session)
    if not search_user:
        raise HTTPException(status_code=404, detail="Requested user not found")
    # ==============================

    user_data = {"nickname": search_user.nickname,
                 "id": search_user.id
                 }
    return user_data