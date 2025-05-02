from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.repository.postgres.crud import get_user_profile_by_email
from app.core.config import settings
from app.core.security import verify_token
from datetime import datetime, UTC
async def nickname_edit(nickname: str, token: str, session: AsyncSession):
    try:
        try:
            payload = verify_token(token, settings.public_key_path)
            email = payload.get("sub")
            if not email:
                raise HTTPException(status_code=401, detail="Invalid token")
        except Exception:
            raise HTTPException(status_code=401, detail="Invalid token")

        user_profile = await get_user_profile_by_email(email, session)

        if not user_profile:
            raise HTTPException(status_code=404, detail="Profile not found")

        user_profile.nickname = nickname
        await session.commit()
        await session.refresh(user_profile)
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")