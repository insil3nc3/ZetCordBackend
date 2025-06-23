import logging

logger = logging.getLogger("websocket")
logger.setLevel(logging.INFO)  # или DEBUG
async def handle_ping_pong(data, user_id, session, db, manager):
    logger.info(f"🔁 Received data: {data}")  # Добавить эту строку
    if data["type"] == "ping":
        logger.info(f"🔁 Ping received from user {user_id}")
        payload = {"type": "pong"}
        await manager.send_json(user_id, payload)
