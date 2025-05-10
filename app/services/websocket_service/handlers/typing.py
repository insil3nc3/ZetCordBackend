
async def handle_typing(data, sender_id, session, db, manager):
    chat_id = data.get("chat_id")
    receiver_id = data.get("receiver_id")

    if not chat_id or not receiver_id:
        return

    await manager.send_personal_message({
        "type": "typing",
        "chat_id": chat_id,
        "from": sender_id
    }, receiver_id)
