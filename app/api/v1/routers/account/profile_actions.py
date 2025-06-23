import os

from fastapi import APIRouter, Depends, status, UploadFile, File
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import FileResponse
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.db.mongo.db import get_mongo
from app.db.postgres.session import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.user_actions_service.avatar_get import avatar_get
from app.services.user_actions_service.avatar_upload import avatar_upload
from app.services.user_actions_service.edit_nickname import nickname_edit
from app.services.user_actions_service.edit_unique_name import unique_name_edit
from app.services.user_actions_service.get_user_by_unique_name import user_get_info_by_unique_name
from app.services.user_actions_service.get_user_info import user_info_get
from app.services.user_actions_service.users import current_user_get

user_router = APIRouter(prefix="/user", tags=["user"])
oauth2 = OAuth2PasswordBearer(tokenUrl="/auth/login")

@user_router.post("/edit_nickname", status_code=status.HTTP_200_OK)
async def edit_nickname(nickname: str, token: str = Depends(oauth2), session: AsyncSession = Depends(get_session)):
    await nickname_edit(nickname, token, session)

AVATAR_DIR = "media/avatars"

@user_router.post("/upload_avatar/", status_code=status.HTTP_200_OK)
async def upload_avatar(file: UploadFile = File(...), token: str = Depends(oauth2), session: AsyncSession = Depends(get_session)):
    await avatar_upload(file, token, session)

@user_router.get("/avatar/{user_profile_id}")
async def get_avatar(user_profile_id: int, token: str = Depends(oauth2), session: AsyncSession = Depends(get_session)):
    avatar_path = await avatar_get(user_profile_id, token, session)
    if not avatar_path:
        avatar_path = os.path.join("app", "media", "avatars", "default.jpg")
    return FileResponse(avatar_path)

@user_router.post("/edit_unique_name", status_code=status.HTTP_200_OK)
async def edit_unique_name(name: str, token: str = Depends(oauth2), session: AsyncSession = Depends(get_session)):
    await unique_name_edit(name, token, session)

@user_router.get("/me")
async def get_current_user(token: str = Depends(oauth2), session: AsyncSession = Depends(get_session), db: AsyncIOMotorDatabase = Depends(get_mongo)):
    user_info = await current_user_get(token, session, db)
    return user_info

@user_router.get("/get_user_info")
async def get_user_info(user_id: int, token: str = Depends(oauth2), session: AsyncSession = Depends(get_session), db: AsyncIOMotorDatabase = Depends(get_mongo)):
    user_info = await user_info_get(user_id, token, session, db)
    return user_info

@user_router.get("/get_user/{user_unique_name}")
async def get_user_by_unique_name(user_unique_name: str, token: str = Depends(oauth2), session: AsyncSession = Depends(get_session)):
    user_info = await user_get_info_by_unique_name(user_unique_name, token, session)
    return user_info