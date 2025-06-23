from bson import ObjectId
from datetime import datetime, UTC
import logging

logger = logging.getLogger("websocket")
logger.setLevel(logging.INFO)  # или DEBUG

async def handle_create_group(data: dict, sender_id: int, session, db, manager):
    logger.info(f"➕ handle_create_group called by user {sender_id} with data: {data}")

    name = data.get("name")
    unique_name = data.get("unique_name")
    member_ids = data.get("member_ids", [])

    if not name or not isinstance(member_ids, list):
        logger.warning("❌ Missing required fields or member_ids is not a list")
        return

    # Убираем дубликаты и добавляем создателя
    member_ids = list(set(member_ids + [sender_id]))

    group_chat = {
        "name": name,
        "unique_name": unique_name,
        "creator_id": sender_id,
        "admin_ids": [sender_id],
        "member_ids": member_ids,
        "last_message": None,
        "avatar": None
    }

    try:
        result = await db["groups"].insert_one(group_chat)
        chat_id = str(result.inserted_id)
        logger.info(f"✅ Group chat created with _id={chat_id}")
    except Exception as e:
        logger.exception(f"❌ Failed to create group chat: {e}")
        return

    payload = {
        "type": "group_created",
        "chat": {
            **group_chat,
            "_id": chat_id
        }
    }

    # Рассылаем участникам
    for user_id in member_ids:
        await manager.send_json(user_id, payload)

    logger.info(f"📤 Sent group creation info to {len(member_ids)} users")
