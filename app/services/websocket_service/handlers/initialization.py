from fastapi import HTTPException

from app.repository.postgres.crud import get_user_profile_by_id, get_user_by_id


async def handle_init(data, sender_id, session, db, manager):
    profile = await get_user_profile_by_id(sender_id, session)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    user = await get_user_by_id(sender_id, session)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user_profile_data = {
        "id": profile.id,
        "email": user.email,
        "nickname": profile.nickname,
        "unique_name": profile.unique_name
    }

    chats_cursor = db["chats"].find({
        "$or": [
            {"user1_id": user.id},
            {"user2_id": user.id}
        ]
    })
    user_chats = await chats_cursor.to_list(length=100)
    for chat in user_chats:
        chat["_id"] = str(chat["_id"])

    profile_chats_data = {
        "chats": user_chats
    }

    data = {"type": "init", "profile_data": user_profile_data, "chats_data": profile_chats_data}
    await manager.send_json(sender_id, data)