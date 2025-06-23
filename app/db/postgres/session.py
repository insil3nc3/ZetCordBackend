"""connection to db"""
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings

SQLALCHEMY_DATABASE_URL = settings.database_url

engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=False)
async_session_maker = sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)

async def get_session():
    async with async_session_maker() as session:
        yield session