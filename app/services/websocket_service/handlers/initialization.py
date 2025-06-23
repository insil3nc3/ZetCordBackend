from fastapi import HTTPException
import logging

from app.repository.postgres.crud import get_user_profile_by_id, get_user_by_id

logger = logging.getLogger("websocket")


from bson import ObjectId
from datetime import datetime, timezone

async def handle_init(data, sender_id, session, db, manager):
    logger.info(f"[INIT] Init requested by user_id={sender_id}")

    try:
        profile = await get_user_profile_by_id(sender_id, session)
        logger.info(f"[INIT] Loaded profile: {profile}")
        if not profile:
            logger.warning(f"[INIT] No profile found for user_id={sender_id}")
            raise HTTPException(status_code=404, detail="Profile not found")

        user = await get_user_by_id(sender_id, session)
        logger.info(f"[INIT] Loaded user: {user}")
        if not user:
            logger.warning(f"[INIT] No user found for user_id={sender_id}")
            raise HTTPException(status_code=404, detail="User not found")

        user_profile_data = {
            "id": profile.id,
            "email": user.email,
            "nickname": profile.nickname,
            "unique_name": profile.unique_name
        }

        logger.info(f"[INIT] Assembling chat list for user_id={user.id}")
        chats_cursor = db["chats"].find({
            "$or": [
                {"user1_id": user.id},
                {"user2_id": user.id}
            ]
        })
        user_chats = await chats_cursor.to_list(length=100)
        logger.info(f"[INIT] Found {len(user_chats)} chats")
        for chat in user_chats:
            chat["_id"] = str(chat["_id"])
            logger.debug(f"[INIT] Chat: {chat}")
        profile_chats_data = {
            "chats": user_chats
        }

        logger.info(f"[INIT] Assembling groups list for user_id={user.id}")
        groups_cursor = db["groups"].find({
            "member_ids": user.id
        })
        user_groups = await groups_cursor.to_list(length=100)
        logger.info(f"[INIT] Found {len(user_groups)} groups")
        for group in user_groups:
            group["_id"] = str(group["_id"])
            logger.debug(f"[INIT] Group: {group}")
        groups_data = {
            "groups": user_groups
        }

        response_data = {
            "type": "init",
            "profile_data": user_profile_data,
            "chats_data": profile_chats_data,
            "groups_data": groups_data
        }

        logger.info(f"[INIT] Sending init payload to user_id={sender_id}")
        await manager.send_json(sender_id, response_data)

    except Exception as e:
        logger.exception(f"[INIT] Error during initialization for user_id={sender_id}: {e}")
        raise

