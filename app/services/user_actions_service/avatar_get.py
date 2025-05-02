from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import verify_token
from app.core.config import settings
from app.repository.postgres.crud import get_user_profile_by_email, get_avatar_by_id
from fastapi.responses import FileResponse
from pathlib import Path
async def avatar_get(profile_id: int, token: str, session: AsyncSession):
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

    filename = await get_avatar_by_id(profile_id, session)
    avatar_path = Path("media/avatars") / filename

    return avatar_path