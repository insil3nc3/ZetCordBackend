
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
from app.services.websocket_service.handlers.create_group import handle_create_group
from app.services.websocket_service.handlers.group_msgs import handle_group_message
from app.services.websocket_service.handlers.private_msgs import handle_private_message, handle_chat_messages
from app.services.websocket_service.handlers.update_profile import handle_profile_update
from app.services.websocket_service.handlers.typing import handle_typing
from app.services.websocket_service.handlers.notification import handle_notification
from app.services.websocket_service.handlers.initialization import handle_init
from app.services.websocket_service.handlers.webrtc.offer import handle_offer
from app.services.websocket_service.handlers.webrtc.answer import handle_answer
from app.services.websocket_service.handlers.webrtc.ice_candidate import handle_ice_candidate
from app.services.websocket_service.handlers.ping_pong import handle_ping_pong
import logging

logger = logging.getLogger("websocket")
logger.setLevel(logging.INFO)  # или DEBUG

# Убедимся, что логгер не пустой
if not logger.hasHandlers():
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '[%(asctime)s] [%(levelname)s] %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)


manager = ConnectionManager()


event_handlers = {
    "chat_message": handle_private_message,
    "profile_update": handle_profile_update,
    "typing": handle_typing,
    "notification": handle_notification,
    "chat_history": handle_chat_messages,
    "init": handle_init,
    "offer": handle_offer,
    "answer": handle_answer,
    "ice_candidate": handle_ice_candidate,
    "ping": handle_ping_pong,
    "create_group": handle_create_group,
    "group_message": handle_group_message
}



async def endpoint_ws(websocket: WebSocket, db, session: AsyncSession):
    token = websocket.query_params.get("token")
    if token is None:
        logger.warning("❌ No token provided in WebSocket connection.")
        await websocket.close(code=1008)
        return

    try:
        payload = verify_token(token, settings.public_key_path)
        email = payload.get("sub")
        if not email:
            logger.error("❌ Token verified, but no subject (email) found.")
            raise HTTPException(status_code=401, detail="Invalid token")
        logger.info(f"✅ Token verified. Email: {email}")
    except Exception as e:
        logger.exception(f"❌ Token verification failed: {e}")
        raise HTTPException(status_code=401, detail="Invalid token")

    try:
        user_profile = await get_user_profile_by_email(email, session)
        if not user_profile:
            logger.warning(f"❌ User profile not found for email: {email}")
            raise HTTPException(status_code=404, detail="Profile not found")
        logger.info(f"✅ User profile loaded: id={user_profile.id}, email={email}")
    except Exception as e:
        logger.exception(f"❌ Error retrieving user profile: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

    user_id = user_profile.id
    await manager.connect(user_id, websocket)
    logger.info(f"✅ WebSocket connected: user_id={user_id}")

    try:
        while True:
            data = await websocket.receive_json()
            logger.info(f"📥 Received WebSocket data from user {user_id}: {data}")

            event_type = data.get("type")
            if not event_type:
                logger.warning(f"⚠️ No event type specified in data: {data}")
                continue

            handler = event_handlers.get(event_type)
            if handler:
                logger.info(f"➡️ Handling event '{event_type}' for user {user_id}")
                await handler(data, user_id, session, db, manager)
            else:
                logger.warning(f"❓ Unknown event type received: {event_type}")
    except WebSocketDisconnect:
        logger.warning(f"🔌 WebSocket disconnected: user_id={user_id}")
        await manager.disconnect(user_id)
    except Exception as e:
        logger.exception(f"❌ Unhandled exception in WebSocket handler for user {user_id}: {e}")
        await manager.disconnect(user_id)
