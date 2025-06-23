from datetime import datetime, UTC, timedelta

from fastapi import Request, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import verify_token, create_token
from app.models.models import Users


async def access_token_refresh(request: Request, session: AsyncSession):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Missing refresh token")

    try:
        payload = verify_token(refresh_token, settings.public_key_path)
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="Invalid token")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

    result = await session.execute(select(Users).where(Users.email == email))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.refresh_token != refresh_token:
        raise HTTPException(status_code=401, detail="Invalid refresh token")


    new_access_token = create_token({"sub": user.email, "role": user.role}, settings.private_key_path, expires_delta=timedelta(minutes=settings.access_token_expire_minutes))
    new_refresh_token = create_token({"sub": user.email}, settings.private_key_path, expires_delta=timedelta(days=settings.refresh_token_expire_days))
    user.refresh_token = new_refresh_token
    await session.commit()
    await session.refresh(user)
    return new_access_token, new_refresh_token