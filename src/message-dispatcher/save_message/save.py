from models import Message, get_db
import uuid
from redis_config import r
import json


async def save_msg_to_db(message_data: dict):
    db = next(get_db())
    try:
        username = message_data.get("username")
        character_id = message_data.get("character_id")
        session_id = message_data.get("session_id")
        ai_response = message_data.get("content")
        role = message_data.get("role")

        ai_message = Message(
            username=username,
            character_id=character_id,
            session_id=session_id,
            content=ai_response,
            role=role,
        )

        db.add(ai_message)
        db.commit()
        print(f"Message saved to database for session {session_id}", flush=True)
    except Exception as e:
        db.rollback()
        print(f"Error saving to database: {e}", flush=True)
        raise
    finally:
        db.close()


async def store_msg_in_redis(message_data: dict) -> bool:
    session_id = message_data.get("session_id")
    ai_response = message_data.get("content")
    redis_key = f"conversation:{session_id}"
    message_obj = {
        "role": "ai",
        "content": ai_response,
        "timestamp": str(uuid.uuid4()),
    }

    try:
        r.rpush(redis_key, json.dumps(message_obj))
        r.expire(redis_key, 86400)
        print(f"Message stored in Redis for session {session_id}", flush=True)
        return True
    except Exception as e:
        print(f"Error storing in Redis: {str(e)}", flush=True)
        raise
