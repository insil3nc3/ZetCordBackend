from bson import ObjectId
from datetime import datetime, UTC
import logging

logger = logging.getLogger("websocket")
logger.setLevel(logging.INFO)  # или DEBUG

async def handle_group_message(data: dict, sender_id: int, session, db, manager):
    logger.info(f"👥 handle_group_message called by user {sender_id} with data: {data}")

    chat_id = data.get("chat_id")
    content = data.get("content")

    if not all([chat_id, content]):
        logger.warning("❌ Missing required fields for group message")
        return

    # Получаем чат и проверяем, является ли sender участником
    chat = await db["groups"].find_one({"_id": ObjectId(chat_id)})
    if not chat:
        logger.warning(f"❌ Group chat with id {chat_id} not found")
        return

    if sender_id not in chat.get("member_ids", []):
        logger.warning(f"⛔ Sender {sender_id} is not a member of the group chat {chat_id}")
        return

    # Создание сообщения
    message = {
        "chat_id": chat_id,
        "sender_id": sender_id,
        "content": content,
        "timestamp": datetime.now(UTC).isoformat(),
        "edited": False,
        "read": False
    }

    try:
        result = await db["message"].insert_one(message)
        message["_id"] = str(result.inserted_id)
        logger.info(f"✅ Message inserted into MongoDB with _id={message['_id']}")
    except Exception as e:
        logger.exception(f"❌ Failed to insert group message: {e}")
        return

    try:
        await db["groups"].update_one(
            {"_id": ObjectId(chat_id)},
            {"$set": {"last_message": message}}
        )
        logger.info(f"🔄 Updated last_message for group chat_id={chat_id}")
    except Exception as e:
        logger.exception(f"❌ Failed to update last_message in group chat: {e}")

    # Рассылка всем участникам
    payload = {
        "type": "group_message",
        "chat_id": chat_id,
        "message": message
    }

    for user_id in chat["member_ids"]:
        await manager.send_json(user_id, payload)
    logger.info(f"📤 Sent group message to {len(chat['member_ids'])} users")
