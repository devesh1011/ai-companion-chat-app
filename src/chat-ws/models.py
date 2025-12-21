from sqlalchemy import Column, String, UUID, DateTime, Index
from sqlalchemy.sql.functions import func
from db import Base
import uuid
import enum


class SessionStatus(str, enum.Enum):
    ACTIVE = "active"
    CLOSED = "closed"
    ARCHIVED = "archived"


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign keys
    username = Column(String, nullable=False, index=True)
    character_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Session metadata
    status = Column(String, default=SessionStatus.ACTIVE.value, nullable=False)
    title = Column(String, nullable=True)  # Optional session title/name

    # Timestamps
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    ended_at = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Indexes
    __table_args__ = (
        Index("idx_user_character_session", "username", "character_id"),
        Index("idx_user_sessions", "username"),
        Index("idx_active_sessions", "status"),
    )


class Message(Base):
    __tablename__ = "messages"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign keys / relationships
    username = Column(String, nullable=False, index=True)
    character_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    session_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Message content
    content = Column(String, nullable=False)
    role = Column(String, nullable=False)  # "user" or "ai"

    # Timestamps
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Indexes for common queries
    __table_args__ = (
        Index("idx_user_character", "username", "character_id"),
        Index("idx_session_messages", "session_id"),
        Index("idx_message_role", "role"),
    )
