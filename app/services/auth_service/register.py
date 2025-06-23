from datetime import timedelta, datetime, UTC
from app.core.config import settings
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.redis.redis_client import redis_client
from app.models.models import Users, UserProfile
from app.core.security import hash_password, create_token
from fastapi import HTTPException, status
import logging
from app.schemas.v1.endpoints.auth import UserCreate
logger = logging.getLogger(__name__)
async def register_user(user_create: UserCreate, code: str, session: AsyncSession):
    saved_code = await redis_client.get(f"email_code:{user_create.email}")
    if not saved_code or saved_code != code:
        logger.info( f"Received user_create: {user_create}")
        raise HTTPException(status_code=401, detail="Invalid or expired code")


    result = await session.execute(select(Users).where(Users.email == user_create.email))
    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    hashed_password = hash_password(user_create.password)
    new_user = Users(email=user_create.email, hashed_password=hashed_password)
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)

    access_token = create_token({"sub": new_user.email, "role": new_user.role}, settings.private_key_path,
                                expires_delta=timedelta(minutes=settings.access_token_expire_minutes))
    refresh_token = create_token({"sub": new_user.email}, settings.private_key_path,
                                 expires_delta=timedelta(days=settings.refresh_token_expire_days))
    new_user.refresh_token = refresh_token
    await session.commit()
    user_profile = UserProfile(user_id=new_user.id, nickname=f"user{new_user.id}")
    session.add(user_profile)
    await session.commit()
    await session.refresh(user_profile)
    await redis_client.delete(f"email_code:{user_create.email}")
    return access_token, refresh_token


