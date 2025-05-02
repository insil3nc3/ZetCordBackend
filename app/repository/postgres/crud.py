"""temporarily: file to get some information from DB"""
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from app.models.models import Users, UserProfile
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
base_url = "postgresql://user_user:user@localhost:5432/user_db"

async def get_user_by_email(user_email: str, session: AsyncSession) -> Users | None:
    result = await session.execute(select(Users).where(Users.email == user_email))
    if result:
        return result.scalars().first()

async def get_user_profile_by_email(email: str, session: AsyncSession):
    user = await get_user_by_email(email, session)
    result = await session.execute(select(UserProfile).where(UserProfile.user_id == user.id))
    if result:
        return result.scalars().first()

async def get_avatar_by_id(profile_id: int, session: AsyncSession):
    result = await session.execute(select(UserProfile).where(UserProfile.id == profile_id))
    profile = result.scalars().first()
    if not profile:
        raise HTTPException(status_code=404, detail="Avatar not found")
    return profile.avatar