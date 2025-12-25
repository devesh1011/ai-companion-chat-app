from sqlalchemy import Column, Text, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from .db import Base
import uuid


class AICharacter(Base):
    __tablename__ = "ai_characters"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    name = Column(Text, nullable=False)
    slug = Column(Text, unique=True, nullable=False)
    description = Column(Text)

    # Prompting
    system_prompt = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True)

    created_by = Column(UUID(as_uuid=True), nullable=True)
    is_public = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
