
from fastapi import APIRouter, Depends, WebSocket, HTTPException
from fastapi.security import OAuth2PasswordBearer
from starlette.websockets import WebSocketDisconnect

from app.core.config import settings
from app.core.security import verify_token
from app.db.mongo.db import get_mongo
from app.db.postgres.session import get_session
from sqlalchemy.ext.asyncio import AsyncSession

from app.repository.postgres.crud import get_user_profile_by_email
from app.services.websocket_service.connection_manager import ConnectionManager
from app.services.websocket_service.handlers.private_msgs import handle_private_message, handle_chat_messages
from app.services.websocket_service.handlers.update_profile import handle_profile_update
from app.services.websocket_service.handlers.typing import handle_typing
from app.services.websocket_service.handlers.notification import handle_notification
from app.services.websocket_service.handlers.initialization import handle_init
manager = ConnectionManager()


event_handlers = {
    "chat_message": handle_private_message,
    "profile_update": handle_profile_update,
    "typing": handle_typing,
    "notification": handle_notification,
    "chat_history": handle_chat_messages,
    "init": handle_init
}



async def endpoint_ws(websocket: WebSocket, db, session: AsyncSession):
    token = websocket.query_params.get("token")
    if token is None:
        await websocket.close(code=1008)
        return
    try:
        payload = verify_token(token, settings.public_key_path)
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="Invalid token")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

    user_profile = await get_user_profile_by_email(email, session)

    if not user_profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    user_id = user_profile.id
    await manager.connect(user_id, websocket)
    try:
        while True:
            data = await websocket.receive_json()
            event_type = data.get("type")
            handler = event_handlers.get(event_type)
            if handler:
                await handler(data, user_id, session, db, manager)
            else:
                print("Unknown event type")
    except WebSocketDisconnect:
        await manager.disconnect(user_id)