from fastapi import APIRouter, Depends, WebSocket, HTTPException
from fastapi.security import OAuth2PasswordBearer
from starlette.websockets import WebSocketDisconnect

from app.core.config import settings
from app.core.security import verify_token
from app.db.mongo.db import get_mongo
from app.db.postgres.session import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.websocket_service.ws_endpoint import endpoint_ws
from app.repository.postgres.crud import get_user_profile_by_email
from app.services.websocket_service.connection_manager import ConnectionManager

ws_router = APIRouter(prefix="/ws", tags=["websocket"])

oauth2 = OAuth2PasswordBearer(tokenUrl="/auth/login")

@ws_router.websocket("")
async def websocket_endpoint(websocket: WebSocket, db = Depends(get_mongo), session: AsyncSession = Depends(get_session)):
    await endpoint_ws(websocket, db, session)