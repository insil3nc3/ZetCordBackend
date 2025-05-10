from bson import ObjectId
from datetime import datetime, UTC



async def handle_private_message(data: dict, sender_id: int, session, db, manager):
    chat_id = data.get("chat_id")
    receiver_id = data.get("receiver_id")
    content = data.get("content")

    if not all([chat_id, receiver_id, content]):
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

    result = await db["message"].insert_one(message)
    message["_id"] = str(result.inserted_id)

    await db["chats"].update_one(
        {"_id": ObjectId(chat_id)},
        {"$set": {"last_message": message}}
    )

    payload = {
        "type": "chat_message",
        "chat_id": chat_id,
        "message": message
    }

    await manager.send_json(receiver_id, payload)
    await manager.send_json(sender_id, payload)

async def handle_chat_messages(data: dict, sender_id: int, session, db, manager):
    before = data.get("before", None)
    limit = data.get("limit", 50)
    chat_id = data.get("chat_id")

    query = {"chat_id": chat_id}
    if before:
        query["timestamp"] = {"$lt": before}

    messages_cursor = db["message"].find(query).sort("timestamp", -1).limit(limit)

    messages = [
        {**msg, "_id": str(msg["_id"])}
        async for msg in messages_cursor
    ]

    payload = {
        "type": "chat_history",
        "chat_id": chat_id,
        "messages": messages
    }
    await manager.send_json(sender_id, payload)