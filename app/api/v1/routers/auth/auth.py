from fastapi import APIRouter, Depends, status, HTTPException, Response, Request
from sqlalchemy.orm import Session
from sqlalchemy import select, insert
from datetime import timedelta, datetime, UTC, timezone
from app.core.config import settings
from app.schemas.v1.endpoints.auth import UserCreate, UserLogin
from app.db.session import get_session
from app.models.models import Users
from app.core.security import hash_password, create_token, verify_password, verify_token
from sqlalchemy.ext.asyncio import AsyncSession
import logging

# Создание файла логирования
file_handler = logging.FileHandler('app.log')
file_handler.setLevel(logging.INFO)
# Формат логов
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Получение логгера
logger = logging.getLogger(__name__)
# Добавление обработчика в логгер
logger.addHandler(file_handler)
logger.addHandler(file_handler)
auth_router = APIRouter(prefix="/auth", tags=["auth"])

@auth_router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(user_create: UserCreate,response: Response, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Users).where(Users.email == user_create.email))
    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    hashed_password = hash_password(user_create.password)

    new_user = Users(email=user_create.email, hashed_password=hashed_password)
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)

    access_token = create_token({"sub": new_user.email, "role": new_user.role}, settings.private_key_path, expires_delta=timedelta(minutes=settings.access_token_expire_minutes))
    refresh_token = create_token({"sub": new_user.email}, settings.private_key_path, expires_delta=timedelta(days=settings.refresh_token_expire_days))
    new_user.refresh_token = refresh_token
    await session.commit()

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=60*60*24*7,
        path="auth/refresh"
    )
    return {"access_token": access_token}

@auth_router.post("/login", status_code=status.HTTP_200_OK)
async def login_user(user_login: UserLogin, response: Response, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Users).where(Users.email == user_login.email))
    existing_user = result.scalars().first()
    logger.info(f"Вошёл: {existing_user.email}")
    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")

    is_password_correct = verify_password(user_login.password, existing_user.hashed_password)

    if not is_password_correct:
        raise HTTPException(status_code=401, detail="Incorrect password")

    access_token = create_token({"sub": existing_user.email, "role": existing_user.role}, settings.private_key_path, expires_delta=timedelta(minutes=settings.access_token_expire_minutes))
    refresh_token = create_token({"sub": existing_user.email}, settings.private_key_path, expires_delta=timedelta(days=settings.refresh_token_expire_days))
    existing_user.refresh_token = refresh_token
    await session.commit()

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=60*60*24*7,
        path="auth/refresh"
    )
    return {"access_token": access_token}

@auth_router.post("/refresh")
async def refresh_access_token(request: Request, response: Response, session: AsyncSession = Depends(get_session)):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Missing refresh token")

    try:
        payload = verify_token(refresh_token, settings.public_key_path)
        email = payload.get("sub")
        expire_time = payload.get("exp")
        if not email:
            raise HTTPException(status_code=401, detail="Invalid token")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

    result = await session.execute(select(Users).where(Users.email == email))
    user = result.scalars().first()

    if datetime.now(UTC).timestamp() > expire_time:
        raise HTTPException(status_code=401, detail="Refresh token expired")

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.refresh_token != refresh_token:
        raise HTTPException(status_code=401, detail="Invalid refresh token")


    new_access_token = create_token({"sub": user.email, "role": user.role}, settings.private_key_path, expires_delta=timedelta(minutes=settings.access_token_expire_minutes))
    new_refresh_token = create_token({"sub": user.email}, settings.private_key_path, expires_delta=timedelta(days=settings.refresh_token_expire_days))

    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=60*60*24*7,
        path="auth/refresh"
    )
    return {"access_token": new_access_token}

# for user:
# refresh_token = request.cookies.get("refresh_token")