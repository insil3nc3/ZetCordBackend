from fastapi import APIRouter, Depends, status, Response, Request
from app.schemas.v1.endpoints.auth import UserCreate, UserLogin
from app.db.postgres.session import get_session
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.services.auth_service.is_refresh_token_expired import check_refresh_token_expired
from app.services.auth_service.register import register_user
from app.services.auth_service.request_code import code_request
from app.services.auth_service.login import user_login
from app.services.auth_service.refresh import access_token_refresh

# ========== logger settings ==========
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
# =====================================


auth_router = APIRouter(prefix="/auth", tags=["auth"])


@auth_router.post("/request_code", status_code=status.HTTP_200_OK)
async def request_code(email: str, session: AsyncSession = Depends(get_session)):
    code_sent = await code_request(email, session)
    if code_sent == 1:
        logger.info(f"Sending verification code to {email}")
        return {"detail": "Code sent"}



@auth_router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user_create: UserCreate, response: Response, code: str,  session: AsyncSession = Depends(get_session)):
    access_token, refresh_token = await register_user(user_create, code, session)
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=60*60*24*7,
        path="auth/refresh"
    )
    logger.info(f"Successfully registered {user_create.email}")
    return {"access_token": access_token}


@auth_router.post("/login", status_code=status.HTTP_200_OK)
async def login_user(user_log_in: UserLogin, response: Response, session: AsyncSession = Depends(get_session)):
    access_token, refresh_token = await user_login(user_log_in, session)
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=60*60*24*7,
        path="auth/refresh"
    )
    logger.info(f"Successfully login {user_log_in.email}")
    return {"access_token": access_token}

@auth_router.post("/refresh")
async def refresh_access_token(request: Request, response: Response, session: AsyncSession = Depends(get_session)):
    new_access_token, new_refresh_token = await access_token_refresh(request, session)

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

@auth_router.get("/check_refresh_token")
async def is_refresh_token_expired(request: Request, session: AsyncSession = Depends(get_session)):
    is_token_expired = await check_refresh_token_expired(request, session)
    return is_token_expired

# for user:
# refresh_token = request.cookies.get("refresh_token")
