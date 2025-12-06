# schemas/ai_character.py
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class AICharacterCreate(BaseModel):
    name: str
    slug: str
    description: str
    system_prompt: str


class AICharacterResponse(BaseModel):
    id: UUID
    name: str
    slug: str
    description: str
    system_prompt: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
