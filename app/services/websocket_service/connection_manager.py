from fastapi import WebSocket
from typing import Dict
import logging

logger = logging.getLogger("websocket")
logger.setLevel(logging.INFO)  # или DEBUG
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, WebSocket] = {}

    async def connect(self, user_id: int, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    async def disconnect(self, user_id: int):
        self.active_connections.pop(user_id, None)

    async def send_json(self, user_id: int, data: dict):
        try:
            ws = self.active_connections.get(user_id)
            if ws:
                await ws.send_json(data)
        except Exception as e:
            logger.info(f"!!! error:  {e}")


    async def get_socket(self, user_id: int):
        return self.active_connections.get(user_id)

    async def send_personal_message(self, message: dict, user_id: int):
        websocket = self.active_connections.get(user_id)
        if websocket:
            await websocket.send_json(message)
            print(f"Сообщение отправлено пользователю {user_id}: {message}")
        else:
            print(f"Нет активного WebSocket-подключения для пользователя {user_id}")