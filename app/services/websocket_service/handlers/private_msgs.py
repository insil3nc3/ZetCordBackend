from bson import ObjectId
from datetime import datetime, UTC
import logging

logger = logging.getLogger("websocket")
logger.setLevel(logging.INFO)  # или DEBUG


async def handle_private_message(data: dict, sender_id: int, session, db, manager):
    logger.info(f"📨 handle_private_message called by user {sender_id} with data: {data}")

    chat_id = data.get("chat_id")
    receiver_id = data.get("receiver_id")
    content = data.get("content")

    if not all([chat_id, receiver_id, content]):
        logger.warning("❌ Missing required fields for private message")
        return

    message = {
        "chat_id": chat_id,
        "sender_id": sender_id,
        "receiver_id": receiver_id,
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
        logger.exception(f"❌ Failed to insert message into MongoDB: {e}")
        return

    try:
        await db["chats"].update_one(
            {"_id": ObjectId(chat_id)},
            {"$set": {"last_message": message}}
        )
        logger.info(f"🔄 Updated last_message for chat_id={chat_id}")
    except Exception as e:
        logger.exception(f"❌ Failed to update last_message in chat: {e}")

    payload = {
        "type": "chat_message",
        "chat_id": chat_id,
        "message": message
    }

    await manager.send_json(receiver_id, payload)
    await manager.send_json(sender_id, payload)
    logger.info(f"📤 Sent message to sender ({sender_id}) and receiver ({receiver_id})")


async def handle_chat_messages(data: dict, sender_id: int, session, db, manager):
    logger.info(f"📚 handle_chat_messages called by user {sender_id} with data: {data}")

    before = data.get("before", None)
    limit = data.get("limit", 50)
    chat_id = data.get("chat_id")

    query = {"chat_id": chat_id}
    if before:
        query["timestamp"] = {"$lt": before}
        logger.info(f"🕒 Fetching messages before {before}")

    try:
        messages_cursor = db["message"].find(query).sort("timestamp", -1).limit(limit)
        messages = [
            {**msg, "_id": str(msg["_id"])}
            async for msg in messages_cursor
        ]
        logger.info(f"✅ Retrieved {len(messages)} messages for chat_id={chat_id}")
    except Exception as e:
        logger.exception(f"❌ Error fetching messages for chat {chat_id}: {e}")
        return

    payload = {
        "type": "chat_history",
        "chat_id": chat_id,
        "messages": messages
    }

    await manager.send_json(sender_id, payload)
    logger.info(f"📤 Sent chat history to user {sender_id}")
