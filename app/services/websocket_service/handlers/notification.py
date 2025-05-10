
async def handle_notification(data, sender_id, session, db, manager):
    target_user_id = data.get("target_user_id")
    notification_type = data.get("notification_type"),
    message = data.get("message")

    if not target_user_id or not notification_type:
        return

    await manager.send_personal_message({
        "type": "notification",
        "notification_type": notification_type,
        "from": sender_id,
        "message": message
    }, target_user_id)