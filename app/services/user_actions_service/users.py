from fastapi import HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import verify_token
from app.core.config import settings
from app.db.postgres.session import get_session
from app.repository.postgres.crud import get_user_profile_by_email


async def current_user_get(token: str, session: AsyncSession, db: AsyncIOMotorDatabase):
    # Проверка токена
    try:
        payload = verify_token(token, settings.public_key_path)
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="Invalid token")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

    # Получение пользователя
    user = await get_user_profile_by_email(email, session)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user_profile_data = {
        "id": user.id,
        "email": email,
        "nickname": user.nickname,
        "unique_name": user.unique_name
    }

    # Получение только тех чатов, где участвует пользователь
    chats_cursor = db["chats"].find({
        "$or": [
            {"user1_id": user.id},
            {"user2_id": user.id}
        ]
    })
    user_chats = await chats_cursor.to_list(length=100)
    for chat in user_chats:
        chat["_id"] = str(chat["_id"])

    profile_chats_data = {
        "chats": user_chats
    }

    return {
        "profile_data": user_profile_data,
        "chats_data": profile_chats_data
    }
