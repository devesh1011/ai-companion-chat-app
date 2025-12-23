from models import Message, get_db
import uuid
from redis_config import r
import json
from datetime import datetime


async def save_msg_to_db(message_data: dict):
    db = next(get_db())
    try:
        username = message_data.get("username")
        print(username)
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
        print("Error storing in redis", e)


async def publish_to_session_channel(message_data: dict) -> bool:
    """
    Publish message to session-specific Redis Pub/Sub channel
    This allows connected WebSocket clients to receive real-time updates
    """
    session_id = message_data.get("session_id")

    if not session_id:
        print("Error: session_id not found in message_data", flush=True)
        return False

    channel_message = {
        "role": message_data.get("role"),
        "content": message_data.get("content"),
        "username": message_data.get("username"),
        "character_id": message_data.get("character_id"),
        "session_id": session_id,
        "timestamp": datetime.now().isoformat(),
    }

    try:
        channel_name = f"session:{session_id}"
        r.publish(channel_name, json.dumps(channel_message))
        print(f"Message published to channel {channel_name}", flush=True)
        return True
    except Exception as e:
        print(f"Error publishing to Redis channel: {str(e)}", flush=True)
        return False
