from fastapi import UploadFile, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.repository.postgres.crud import get_user_by_email, get_user_profile_by_email
from app.core.config import settings
from app.core.security import verify_token
import uuid
from pathlib import Path
import shutil
async def avatar_upload(file: UploadFile, token: str, session: AsyncSession):
    try:# 1) verify token
        try:
            payload = verify_token(token, settings.public_key_path)
            email = payload.get("sub")
            if not email:
                raise HTTPException(status_code=401, detail="Invalid token")
        except Exception:
            raise HTTPException(status_code=401, detail="Invalid token")
        # 2) get user_profile
        user = await get_user_profile_by_email(email, session)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        # 3) save photo
        suffix = Path(file.filename).suffix
        file_id = f"{uuid.uuid4()}{suffix}"
        file_path = Path("media/avatars") / file_id
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        # 4) save photo path to db
        user.avatar = file_id
        await session.commit()
        await session.refresh(user)
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")