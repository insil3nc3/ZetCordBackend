from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.core.config import settings
from app.core.security import verify_token
from app.repository.postgres.crud import get_user_profile_by_email, check_for_unique_name_existing


async def unique_name_edit(name: str, token: str, session: AsyncSession):
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

        names_in_base = await check_for_unique_name_existing(name, session)
        if not names_in_base:
            user_profile.unique_name = name
            await session.commit()
            await session.refresh(user_profile)
        else:
            raise HTTPException(405, "User with this Unique name already exists")
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")