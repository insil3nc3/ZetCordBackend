from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

MONGO_URL = settings.mongo_url

client = AsyncIOMotorClient(MONGO_URL)
db = client["messages_db"]

async def get_mongo():
    yield db

