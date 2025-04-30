from app.core.config import settings
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import Users
from app.core.security import hash_password, create_token, verify_password, verify_token
from app.db.postgres.session import get_session
from app.services.confirm_code_gen.code_gen import gen_code
from app.services.email_service.send_message_to_email import send_code_async
from app.db.redis.redis_client import redis_client
from datetime import datetime
from fastapi import HTTPException, status
from app.repository.postgres.crud import get_user_by_email

async def code_request(email: str, session: AsyncSession):
    user = await get_user_by_email(email, session)
    if user:
        raise HTTPException(status_code=400, detail="User already exists")
    code = gen_code()
    code_sent = await send_code_async(recipient=email, subject="Code verification", code=code)
    if code_sent == -1:
        raise HTTPException(status_code=401, detail="Mail not sent")
    await redis_client.setex(f"email_code:{email}", 600, str(code))

    return 1