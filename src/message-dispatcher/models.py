from sqlalchemy import Column, UUID, String, DateTime, Index
from sqlalchemy.sql.functions import func
import uuid
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import create_engine
from config import get_settings

settings = get_settings()

DATABASE_URL = f"postgresql+psycopg2://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"

engine = create_engine(DATABASE_URL)
sessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

Base = declarative_base()


def get_db():
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()


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
