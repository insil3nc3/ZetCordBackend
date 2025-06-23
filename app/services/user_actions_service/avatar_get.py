from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import verify_token
from app.core.config import settings
from app.repository.postgres.crud import get_user_profile_by_email, get_avatar_by_id
from fastapi.responses import FileResponse
from pathlib import Path
from app.db.mongo import db  # для группы из MongoDB

async def avatar_get(profile_id: int | str, token: str, session: AsyncSession, group_id: str = None):
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

    if type(profile_id) == "int":
        # путь для диалога — media/avatars/dialogs/<profile_id> с расширением
        # тут можно получить расширение из БД, либо подставить .png по умолчанию
        avatar_path = Path("media/avatars/dialogs") / str(profile_id)
        # если файла нет, можно подставить дефолтный аватар
        if not avatar_path.exists():
            avatar_path = Path("media/avatars/dialogs/default.jpg")

    elif type(profile_id) == "str":
        if not group_id:
            raise HTTPException(status_code=400, detail="group_id required for group chat_type")
        # из MongoDB забираем путь к аватару
        group = await db["groups"].find_one({"_id": group_id})
        if not group or "avatar" not in group:
            avatar_path = Path("media/avatars/dialogs/default.jpg")
        else:
            filename = group["avatar"]
            avatar_path = Path("media/avatars/groups") / filename
            if not avatar_path.exists():
                avatar_path = Path("media/avatars/dialogs/default.jpg")
    else:
        raise HTTPException(status_code=400, detail="Invalid chat_type")

    return FileResponse(str(avatar_path))
