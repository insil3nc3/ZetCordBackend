from sqlalchemy import select

from app.repository.postgres.crud import get_user_profile_by_id

import logging

logger = logging.getLogger("websocket")
logger.setLevel(logging.INFO)  # или DEBUG
async def handle_offer(data, user_id, session, db, manager):
    target_user_id = data.get("to")
    offer = data.get("offer")
    if target_user_id and offer:
        target_socket = await manager.get_socket(target_user_id)
        result = await get_user_profile_by_id(user_id, session)
        from_user = {
            "id": result.id,
            "nickname": result.nickname,
            "unique_name": result.unique_name}
        if target_socket:
            await target_socket.send_json({
                "type": "offer",
                "from": from_user,
                "offer": offer
            })