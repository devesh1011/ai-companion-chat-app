import json
import os

import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from character_response import reply
from redis_config import r
import asyncio
import aio_pika

# Database setup for chat-ws
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "",
)
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


def fetch_character_system_prompt(character_id: str) -> str | None:
    """
    Fetch system prompt from ai_character service

    Args:
        character_id: AI character's unique ID

    Returns:
        System prompt if found, None otherwise
    """
    try:
        response = requests.get(
            f"http://{os.getenv('AI_CHAR_SVC_ADDR', 'ai-character-service:3000')}/api/characters/id/{character_id}",
            timeout=5,
        )

        if response.status_code == 200:
            data = response.json()
            return data.get("system_prompt")
        else:
            print(f"Error fetching character: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error fetching character system prompt: {str(e)}")
        return None


def fetch_conversation_history(
    username: str, character_id: str, session_id: str, limit: int = 10
) -> list[dict]:
    """
       Fetch last N messages between user and character.
       Tries Redis first (fast cache), falls back to database if not found.

       Args:
           username: User's unique ID
           character_id: AI character's unique ID
           session_id: Chat session ID
           limit: Number of messages to fetch (default 10)

       Returns:
           List of message dicts with format: {"role": "user|ai", "content": "message"}
    f"""
    try:
        # get from Redis first (fast)
        redis_key = f"conversation:{session_id}"
        redis_messages = r.lrange(redis_key, -limit, -1)  # Get last N items

        if redis_messages:
            messages = []
            for msg_json in redis_messages:
                try:
                    msg = json.loads(msg_json)
                    messages.append(msg)
                except json.JSONDecodeError:
                    continue

            return messages

        # Fallback to Postgres
        print("Cache miss, fetching from database...")
        db = SessionLocal()

        # Query messages from the messages table
        query = f"""
            SELECT role, content, created_at
            FROM messages
            WHERE username = '{username}'
            AND character_id = '{character_id}'
            AND session_id = '{session_id}'
            ORDER BY created_at ASC
            LIMIT {limit}
        """

        result = db.execute(query)
        messages = []

        for row in result:
            messages.append(
                {
                    "role": row[0],  # "user" or "ai"
                    "content": row[1],
                    "timestamp": row[2].isoformat() if row[2] else None,
                }
            )

        db.close()
        return messages

    except Exception as e:
        print(f"Error fetching conversation history: {str(e)}")
        return []


async def main():
    rabbitmq_host = os.getenv("RABBITMQ_HOST", "rabbitmq")
    connection = await aio_pika.connect_robust(f"amqp://guest:guest@{rabbitmq_host}/")
    channel = await connection.channel()

    queue = await channel.declare_queue("chat.user.msg", durable=True)
    exchange = await channel.declare_exchange("chat_app", type="topic", durable=True)
    await queue.bind(exchange=exchange, routing_key="chat.user.msg")
    print("Connected to RabbitMQ and bound queue", flush=True)

    async def callback(msg: aio_pika.abc.AbstractIncomingMessage) -> None:
        try:
            message_data = json.loads(msg.body)
            print(f"Received message: {message_data}", flush=True)
            username = message_data.get("username")
            character_id = message_data.get("character_id")
            session_id = message_data.get("session_id")
            user_content = message_data.get("content")

            if not all([username, character_id, session_id, user_content]):
                print("Invalid message format, missing required fields")
                await msg.nack()
                return

            system_prompt = fetch_character_system_prompt(character_id)
            if not system_prompt:
                print(f"Could not fetch system prompt for character {character_id}")
                await msg.nack()
                return

            conversation_history = fetch_conversation_history(
                username, character_id, session_id
            )
            result = reply(message_data, system_prompt, conversation_history)

            # Publish result to chat.ai.msg queue
            result_data = json.dumps(result).encode()
            await exchange.publish(
                aio_pika.Message(body=result_data), routing_key="chat.ai.msg"
            )

            await msg.ack()

        except json.JSONDecodeError:
            print("Error: Invalid JSON in message")
            await msg.nack()
        except Exception as e:
            print(f"Error processing message: {str(e)}")
            await msg.nack()

    print("Waiting for messages on queue: chat.user.msg")
    print(
        f"Queue bound to exchange: chat_app with routing key: chat.user.msg", flush=True
    )

    async with queue.iterator() as queue_iter:
        async for message in queue_iter:
            await callback(message)


if __name__ == "__main__":
    asyncio.run(main())
