
async def handle_answer(data, user_id, session, db, manager):

    target_user_id = data.get("to")
    answer = data.get("answer")
    if target_user_id and answer:
        target_socket = await manager.get_socket(target_user_id)
        if target_socket:
            await target_socket.send_json({
                "type": "answer",
                "from": user_id,
                "answer": answer
            })