import json
import uuid

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager

from db import get_db, Base, engine
from models import ChatSession, SessionStatus
from connection_manager import manager
from config import get_settings
from utils import validate_token
from models import Message
from rabbitmq_config import channel
from redis_config import r
import pika


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    print("Tables created.")
    yield


app = FastAPI(title="Chat WebSocket Service", version="1.0.0", lifespan=lifespan)

settings = get_settings()


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "ok", "service": "chat-ws"}


def create_chat_session(db: Session, user_id: str, character_id: str) -> ChatSession:
    """
    Create a new chat session in the database

    Args:
        db: Database session
        user_id: User's unique ID
        character_id: AI character's unique ID

    Returns:
        Created ChatSession object
    """
    session = ChatSession(
        id=uuid.uuid4(),
        user_id=user_id,
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

    user_id = token_data.get("username")

    if not user_id:
        await websocket.close(code=4001, reason="Invalid token payload")
        return

    db = next(get_db())
    try:
        chat_session = create_chat_session(db, user_id, character_id)
        session_id = str(chat_session.id)
    except Exception:
        await websocket.close(code=4002, reason="Database error")
        db.close()
        return

    # Step 3: Register connection
    await manager.connect(session_id, user_id, character_id, websocket)
    channel.queue_declare("chat.user.msg", passive=True, durable=True)

    try:
        # Send welcome message
        await websocket.send_text(
            json.dumps(
                {
                    "type": "connection",
                    "message": "Connected to chat",
                    "session_id": session_id,
                    "user_id": user_id,
                    "character_id": character_id,
                }
            )
        )

        # Step 4: Listen for incoming messages
        while True:
            # Receive message from client
            data = await websocket.receive_text()

            try:
                message_data = json.loads(data)
                content = message_data.get("content", "")

                if not content:
                    await websocket.send_text(
                        json.dumps({"type": "error", "message": "Empty message"})
                    )
                    continue

                # Store message to the database (reuse existing connection)
                try:
                    user_message = Message(
                        id=uuid.uuid4(),
                        user_id=user_id,
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

                # Store the message in Redis for fast access
                redis_key = f"conversation:{session_id}"
                message_obj = {
                    "role": "user",
                    "content": content,
                    "timestamp": str(uuid.uuid4()),
                }
                try:
                    # Push message to Redis list
                    r.rpush(redis_key, json.dumps(message_obj))
                    # Set expiration to 24 hours (86400 seconds)
                    r.expire(redis_key, 86400)
                except Exception as e:
                    print(f"Warning: Failed to store in Redis: {str(e)}")

                # Send the message to the queue
                message = {
                    "user_id": user_id,
                    "character_id": character_id,
                    "session_id": session_id,
                    "content": content,
                }

                try:
                    channel.basic_publish(
                        exchange="",
                        routing_key="chat.user.msg",
                        body=json.dumps(message),
                        properties=pika.BasicProperties(
                            delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
                        ),
                    )
                except Exception as e:
                    await websocket.send_text(
                        json.dumps({"type": "error", "message": "message was not sent"})
                    )

                # Echo message back (skeleton - just for testing connection)
                await websocket.send_text(
                    json.dumps(
                        {
                            "type": "echo",
                            "role": "user",
                            "content": content,
                            "timestamp": str(uuid.uuid4()),
                        }
                    )
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

    except Exception:
        manager.disconnect(session_id)
        db.close()
