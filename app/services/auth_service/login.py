import logging
from datetime import timedelta

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import verify_password, create_token
from app.models.models import Users
from app.schemas.v1.endpoints.auth import UserLogin

logger = logging.getLogger(__name__)

async def user_login(user: UserLogin, session: AsyncSession):
    result = await session.execute(select(Users).where(Users.email == user.email))
    existing_user = result.scalars().first()

    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")
    logger.info(f"Вошёл: {existing_user.email}")

    is_password_correct = verify_password(user.password, existing_user.hashed_password)

    if not is_password_correct:
        raise HTTPException(status_code=401, detail="Incorrect password")

    access_token = create_token({"sub": existing_user.email, "role": existing_user.role}, settings.private_key_path,
                                expires_delta=timedelta(minutes=settings.access_token_expire_minutes))
    refresh_token = create_token({"sub": existing_user.email}, settings.private_key_path,
                                 expires_delta=timedelta(days=settings.refresh_token_expire_days))
    existing_user.refresh_token = refresh_token
    await session.commit()

    return access_token, refresh_token