
from fastapi import APIRouter, Depends, status, UploadFile, File
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import FileResponse
import os
import shutil
from uuid import uuid4
from app.db.postgres.session import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from app.repository.postgres.crud import get_avatar_by_id
from app.services.user_actions_service.avatar_get import avatar_get
from app.services.user_actions_service.avatar_upload import avatar_upload
from app.services.user_actions_service.edit_nickname import nickname_edit

user_router = APIRouter(prefix="/user", tags=["user"])
oauth2 = OAuth2PasswordBearer(tokenUrl="/auth/login")

@user_router.post("/edit_nickname", status_code=status.HTTP_200_OK)
async def edit_nickname(nickname: str, token: str = Depends(oauth2), session: AsyncSession = Depends(get_session)):
    await nickname_edit(nickname, token, session)

AVATAR_DIR = "media/avatars"

@user_router.post("/upload_avatar", status_code=status.HTTP_200_OK)
async def upload_avatar(file: UploadFile = File(...), token: str = Depends(oauth2), session: AsyncSession = Depends(get_session)):
    await avatar_upload(file, token, session)

@user_router.get("/avatar/{user_profile_id}")
async def get_avatar(user_profile_id: int, token: str = Depends(oauth2), session: AsyncSession = Depends(get_session)):
    avatar_path = await avatar_get(user_profile_id, token, session)
    return FileResponse(avatar_path)