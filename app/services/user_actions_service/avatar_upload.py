from fastapi import UploadFile, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.repository.postgres.crud import get_user_by_email, get_user_profile_by_email
from app.core.config import settings
from app.core.security import verify_token
import uuid
from pathlib import Path
import shutil
from app.db.mongo import db  # пример подключения к MongoDB

async def avatar_upload(file: UploadFile, token: str, session: AsyncSession, group_id: str = None):
    try:
        # 1) verify token
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

        # 3) prepare filename и path в зависимости от chat_type
        suffix = Path(file.filename).suffix
        if group_id == None:
            # сохранить с именем user.id + расширение
            filename = f"{user.id}{suffix}"
            file_path = Path("media/avatars/dialogs") / filename
        else:
            if not group_id:
                raise HTTPException(status_code=400, detail="group_id required for group chat_type")
            # уникальное имя файла с UUID
            filename = f"{uuid.uuid4()}{suffix}"
            file_path = Path("media/avatars/groups") / filename


        # создаём директорию, если её нет
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # 4) сохраняем файл
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        # 5) обновляем БД
        if group_id == None:
            # сохраняем в поле аватара пользователя
            user.avatar = filename
            await session.commit()
            await session.refresh(user)
        elif group_id:
            # обновляем MongoDB с путём аватарки для группы
            await db["groups"].update_one(
                {"_id": group_id},
                {"$set": {"avatar": filename}}
            )
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
