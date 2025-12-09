# what ai consumer would do is
# 1. listen to the queue message
# 2. fetch the system prompt from the ai_character db for the character_id
# 3. fetch the last 10 messages between the user and character
# 4. generate the response
# 5. publish the message on the chat.ai.msg queue
import pika
import json
import os
import sys
import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from character_response import reply
from redis_config import r

# Database setup for chat-ws
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://chat_user:chat_password@postgres:5432/ai-companion-chat",
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
            f"http://{os.getenv('AI_CHAR_SVC_ADDR', 'ai-character:8003')}/api/characters/id/{character_id}",
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
    user_id: str, character_id: str, session_id: str, limit: int = 10
) -> list[dict]:
    """
       Fetch last N messages between user and character.
       Tries Redis first (fast cache), falls back to database if not found.

       Args:
           user_id: User's unique ID
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
            WHERE user_id = '{user_id}'
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


def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host="rabbitmq"))

    channel = connection.channel()
    channel.queue_declare("chat.ai.msg")

    def callback(ch, method, properties, body):
        try:
            print(f"Received message: {body}")

            # Step 1: Parse incoming message
            message_data = json.loads(body)
            user_id = message_data.get("user_id")
            character_id = message_data.get("character_id")
            session_id = message_data.get("session_id")
            user_content = message_data.get("content")

            if not all([user_id, character_id, session_id, user_content]):
                print("Invalid message format, missing required fields")
                ch.basic_nack(delivery_tag=method.delivery_tag)
                return

            # Step 2: Fetch system prompt from ai_character service
            system_prompt = fetch_character_system_prompt(character_id)
            if not system_prompt:
                print(f"Could not fetch system prompt for character {character_id}")
                ch.basic_nack(delivery_tag=method.delivery_tag)
                return

            # Fetch last 10 messages between user and character
            conversation_history = fetch_conversation_history(
                user_id, character_id, session_id
            )

            # Format for display
            formatted_history = "\n".join(
                [
                    f"{msg['role'].upper()}: {msg['content']}"
                    for msg in conversation_history
                ]
            )
            print(f"Conversation history:\n{formatted_history}")

            # Generate response using system prompt and history
            result = reply(message_data, system_prompt, conversation_history)

            # Step 5 - Publish to chat.ai.msg queue
            channel.basic_publish(
                exchange="",
                routing_key="chat.ai.msg",
                body=json.dumps(result),
                properties=pika.BasicProperties(
                    delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
                ),
            )

            ch.basic_ack(delivery_tag=method.delivery_tag)

        except json.JSONDecodeError:
            print("Error: Invalid JSON in message")
            ch.basic_nack(delivery_tag=method.delivery_tag)
        except Exception as e:
            print(f"Error processing message: {str(e)}")
            ch.basic_nack(delivery_tag=method.delivery_tag)

    queue_name = os.getenv("QUEUE_NAME", "chat.user.msg")
    channel.queue_declare(queue=queue_name, durable=True)
    channel.basic_consume(queue=queue_name, on_message_callback=callback)
    print(f"Waiting for messages on queue: {queue_name}")

    channel.start_consuming()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupted")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
