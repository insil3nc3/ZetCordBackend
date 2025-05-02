from sqlalchemy.ext.asyncio import create_async_engine
from app.models.models import Base
from app.core.config import settings
import asyncio


async def init_db():
    SQLALCHEMY_DATABASE_URL = settings.database_url
    print(SQLALCHEMY_DATABASE_URL)

    engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=True)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    print("База данных успешно создана!")