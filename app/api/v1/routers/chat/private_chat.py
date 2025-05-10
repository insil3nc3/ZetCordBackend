from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordBearer
from app.db.postgres.session import get_session
from app.schemas.v1.mongo.private_chat import PrivateChatInDB
from app.db.mongo.db import get_mongo
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.services.chat_service.private_chat import private_chat_create

chat_router = APIRouter(prefix="/chats", tags=["Private Chat"])
oauth2 = OAuth2PasswordBearer(tokenUrl="/auth/login")
@chat_router.post("/private", response_model=PrivateChatInDB)
async def create_private_chat(user2_unique_name: str, db: AsyncIOMotorDatabase = Depends(get_mongo), token: str = Depends(oauth2), session: AsyncSession = Depends(get_session)):
    chat = await private_chat_create(user2_unique_name, db, token, session)
    return PrivateChatInDB.from_mongo(chat)