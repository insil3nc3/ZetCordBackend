from fastapi import FastAPI
from app.api.v1.routers.auth.auth import auth_router
from app.api.v1.routers.account.profile_actions import user_router
from app.services.websocket_service.connection_manager import ConnectionManager
from app.api.v1.routers.chat.private_chat import chat_router
from app.api.v1.routers.ws.ws import ws_router

app = FastAPI()
manager = ConnectionManager()
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(chat_router)
app.include_router(ws_router)