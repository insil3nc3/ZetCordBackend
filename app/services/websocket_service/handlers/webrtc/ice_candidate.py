import logging

logger = logging.getLogger("websocket")
logger.setLevel(logging.INFO)  # или DEBUG
async def handle_ice_candidate(data, user_id, session, db, manager):
    target_user_id = data.get("to")
    candidate = data.get("candidate")
    logger.info(f"📥 Обработка ICE кандидата от user_id={user_id} для target_user_id={target_user_id}: {candidate}")
    if target_user_id and candidate:
        target_socket = await manager.get_socket(target_user_id)  # Исправлено: добавлен await
        if target_socket:
            await target_socket.send_json({
                "type": "ice_candidate",
                "from": user_id,
                "candidate": candidate
            })
            logger.info(f"📤 ICE кандидат отправлен пользователю {target_user_id}")
        else:
            logger.warning(f"⚠️ Сокет для пользователя {target_user_id} не найден")
    else:
        logger.warning(f"⚠️ Некорректные данные ICE кандидата: target_user_id={target_user_id}, candidate={candidate}")