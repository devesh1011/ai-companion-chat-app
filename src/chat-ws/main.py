import json
import uuid
import os
import asyncio

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager

from db import get_db
from models import ChatSession, SessionStatus
from connection_manager import manager
from config import get_settings
from utils import validate_token
from models import Message
from redis_config import r
import aio_pika


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(title="Chat WebSocket Service", version="1.0.0", lifespan=lifespan)

settings = get_settings()


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "ok", "service": "chat-ws"}


def create_chat_session(db: Session, username: str, character_id: str) -> ChatSession:
    """
    Create a new chat session in the database

    Args:
        db: Database session
        username: Username
        character_id: AI character's unique ID

    Returns:
        Created ChatSession object
    """
    session = ChatSession(
        username=username,
        character_id=character_id,
        status=SessionStatus.ACTIVE.value,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


@app.websocket("/ws/{character_id}")
async def websocket_endpoint(
    websocket: WebSocket, character_id: str, token: str = Query(...)
):
    """
    WebSocket endpoint for real-time chat

    Args:
        websocket: WebSocket connection object
        character_id: AI character's unique ID (from URL path)
        token: JWT token (from query parameter)
    """
    token_data = await validate_token(token)

    if not token_data:
        await websocket.close(code=4001, reason="Invalid token")
        return

    username = token_data.get("username")

    if not username:
        await websocket.close(code=4001, reason="Invalid token payload")
        return

    await websocket.accept()

    db = next(get_db())
    try:
        chat_session = create_chat_session(db, username, character_id)
        session_id = str(chat_session.id)
    except Exception:
        await websocket.close(code=4002, reason="Database error")
        db.close()
        return

    await manager.connect(session_id, username, character_id, websocket)

    try:
        rabbitmq_host = os.getenv("RABBITMQ_HOST", "rabbitmq")
        rb_connection = await aio_pika.connect_robust(
            f"amqp://guest:guest@{rabbitmq_host}/",
            client_properties={"connection_name": "chat-ws"},
        )
        channel = await rb_connection.channel()
        queue = await channel.declare_queue("chat.user.msg", durable=True)
        exchange = await channel.declare_exchange(
            "chat_app", type="topic", durable=True
        )
        await queue.bind(exchange=exchange, routing_key="chat.user.msg")
        print("Connected to RabbitMQ and bound queue", flush=True)
    except Exception as e:
        print(f"ERROR connecting to RabbitMQ: {e}", flush=True)
        await websocket.close(code=5000, reason="Server error")
        return

    try:
        await websocket.send_text(
            json.dumps(
                {
                    "type": "connection",
                    "message": "Connected to chat",
                    "session_id": session_id,
                    "username": username,
                    "character_id": character_id,
                }
            )
        )

        # Redis Pub/Sub setup: subscribe to session-specific channel
        pubsub = r.pubsub()
        channel_name = f"session:{session_id}"
        pubsub.subscribe(channel_name)
        print(f"Subscribed to Redis channel: {channel_name}", flush=True)

        # Create async tasks for receiving messages and listening to Redis
        async def listen_to_redis():
            """Listen for messages from message-dispatcher via Redis Pub/Sub"""
            loop = asyncio.get_event_loop()
            while True:
                try:
                    message = await loop.run_in_executor(None, pubsub.get_message, True)

                    if message and message.get("type") == "message":
                        data = json.loads(message.get("data", "{}"))
                        print(f"Received AI response from Redis: {data}", flush=True)
                        await websocket.send_json({"type": "ai_response", "data": data})
                except asyncio.CancelledError:
                    print(f"Stopping Redis listener for {channel_name}", flush=True)
                    break
                except Exception as e:
                    print(
                        f"Error in Redis listener: {e}",
                        flush=True,
                    )
                    await asyncio.sleep(0.1)

        # Start Redis listener task
        redis_task = asyncio.create_task(listen_to_redis())

        # Step 4: Listen for incoming messages
        while True:
            data = await websocket.receive_text()

            try:
                message_data = json.loads(data)
                content = message_data.get("content", "")

                if not content:
                    await websocket.send_text(
                        json.dumps({"type": "error", "message": "Empty message"})
                    )
                    continue

                try:
                    user_message = Message(
                        username=username,
                        character_id=character_id,
                        session_id=session_id,
                        content=content,
                        role="user",
                    )
                    db.add(user_message)
                    db.commit()
                except Exception as e:
                    db.rollback()
                    await websocket.send_text(
                        json.dumps(
                            {"type": "error", "message": "Failed to save message"}
                        )
                    )
                    continue

                redis_key = f"conversation:{session_id}"
                message_obj = {
                    "role": "user",
                    "content": content,
                    "timestamp": str(uuid.uuid4()),
                }
                try:
                    r.rpush(redis_key, json.dumps(message_obj))
                    r.expire(redis_key, 86400)
                except Exception as e:
                    print(f"Warning: Failed to store in Redis: {str(e)}")

                message = {
                    "username": username,
                    "character_id": character_id,
                    "session_id": session_id,
                    "content": content,
                }

                try:
                    message_body = json.dumps(message).encode()
                    print(f"Publishing message to chat.user.msg: {message}", flush=True)
                    await exchange.publish(
                        aio_pika.Message(body=message_body), routing_key="chat.user.msg"
                    )
                    print("Message published successfully", flush=True)
                except Exception as e:
                    print(f"ERROR publishing message: {e}", flush=True)
                    await websocket.send_text(
                        json.dumps({"type": "error", "message": "message was not sent"})
                    )

            except json.JSONDecodeError:
                await websocket.send_text(
                    json.dumps({"type": "error", "message": "Invalid JSON"})
                )
            except Exception:
                await websocket.send_text(
                    json.dumps({"type": "error", "message": "Processing error"})
                )

    except WebSocketDisconnect:
        manager.disconnect(session_id)

        # Cancel Redis listener task
        try:
            redis_task.cancel()
            await redis_task
        except asyncio.CancelledError:
            pass
        except Exception as e:
            print(f"Error cancelling redis_task: {e}", flush=True)

        # Unsubscribe from Redis channel
        try:
            pubsub.unsubscribe(channel_name)
            pubsub.close()
            print(f"Unsubscribed from Redis channel: {channel_name}", flush=True)
        except Exception as e:
            print(f"Error unsubscribing from Redis: {e}", flush=True)

        # Update session status to closed in DB
        try:
            session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
            if session:
                session.status = SessionStatus.CLOSED.value
                db.commit()
        except Exception:
            pass
        finally:
            db.close()  # Close DB when user disconnects
            try:
                await rb_connection.close()
            except Exception:
                pass

    except Exception:
        manager.disconnect(session_id)

        # Cancel Redis listener task on exception
        try:
            redis_task.cancel()
            await redis_task
        except asyncio.CancelledError:
            pass
        except Exception as e:
            print(f"Error cancelling redis_task: {e}", flush=True)

        # Unsubscribe from Redis channel
        try:
            pubsub.unsubscribe(channel_name)
            pubsub.close()
            print(f"Unsubscribed from Redis channel: {channel_name}", flush=True)
        except Exception as e:
            print(f"Error unsubscribing from Redis: {e}", flush=True)

        db.close()
        try:
            await rb_connection.close()
        except Exception:
            pass
