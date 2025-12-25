from fastapi import APIRouter, HTTPException, Depends
from app.services import (
    get_ai_character_by_id,
    get_ai_character_by_slug,
    list_ai_characters,
    create_ai_character,
)
from app.db import get_db
from app.models.schemas import AICharacterResponse, AICharacterCreate
from sqlalchemy.orm import Session

router = APIRouter(prefix="/characters", tags=["AI Characters"])


@router.get("/id/{char_id}", response_model=AICharacterResponse)
def get_ai_char_by_id(char_id: str, db: Session = Depends(get_db)):
    ai_char = get_ai_character_by_id(db, character_id=char_id)
    if not ai_char:
        raise HTTPException(status_code=404, detail="Character not found")
    return ai_char


@router.get("/id/{slug}", response_model=AICharacterResponse)
def get_ai_char_by_slug(slug: str, db: Session = Depends(get_db)):
    ai_char = get_ai_character_by_slug(db, slug=slug)
    if not ai_char:
        raise HTTPException(status_code=404, detail="Character not found")


@router.get("/", response_model=list[AICharacterResponse])
def get_all_ai_chars(db: Session = Depends(get_db)):
    ai_chars = list_ai_characters(db)
    return ai_chars


@router.post("/", response_model=AICharacterResponse)
def create_ai_char(ai_char: AICharacterCreate, db: Session = Depends(get_db)):
    new_character = create_ai_character(
        db=db,
        name=ai_char.name,
        slug=ai_char.slug,
        description=ai_char.description,
        system_prompt=ai_char.system_prompt,
    )
    return new_character
