
async def handle_profile_update(data, sender_id, db, session, manager):
    new_data = data["new_data"]
    # SQLAlchemy

    payload = {
        "type": "profile_updated",
        "user_id": sender_id,
        "new_data": new_data
    }
    for uid in manager.active_connections:
        if uid != sender_id:
            await manager.send_json(uid, payload)