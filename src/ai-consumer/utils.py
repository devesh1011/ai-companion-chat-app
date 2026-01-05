from redis_config import r
from datetime import datetime
import json


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
        "role": "ai",
        "content": "Too many requests",
        "username": message_data.get("username"),
        "character_id": message_data.get("character_id"),
        "session_id": session_id,
        "timestamp": datetime.now().isoformat(),
    }

    try:
        channel_name = f"session:{session_id}"
        r.publish(channel_name, json.dumps(channel_message))
        print(f"Sent the rate limit message to user {channel_name}", flush=True)
        return True
    except Exception as e:
        print(f"Error publishing to Redis channel: {str(e)}", flush=True)
        return False
