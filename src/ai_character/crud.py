# crud.py
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from models import AICharacter


def create_ai_character(
    db: Session,
    name: str,
    slug: str,
    description: str,
    system_prompt: str,
) -> AICharacter:
    existing = db.query(AICharacter).filter(AICharacter.slug == slug).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="AI character with this slug already exists",
        )

    ai_character = AICharacter(
        name=name,
        slug=slug,
        description=description,
        system_prompt=system_prompt,
    )

    db.add(ai_character)
    db.commit()
    db.refresh(ai_character)
    return ai_character


def get_ai_character_by_id(db: Session, character_id: str) -> AICharacter:
    character = db.query(AICharacter).filter(AICharacter.id == character_id).first()
    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="AI character not found",
        )
    return character


def get_ai_character_by_slug(db: Session, slug: str) -> AICharacter:
    character = db.query(AICharacter).filter(AICharacter.slug == slug).first()
    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="AI character not found",
        )
    return character


def list_ai_characters(
    db: Session,
    skip: int = 0,
    limit: int = 20,
    active_only: bool = True,
):
    query = db.query(AICharacter)

    if active_only:
        query = query.filter(AICharacter.is_active)

    return query.offset(skip).limit(limit).all()


def update_ai_character(
    db: Session,
    character_id: str,
    name: str | None = None,
    description: str | None = None,
    system_prompt: str | None = None,
    is_active: bool | None = None,
) -> AICharacter:
    character = get_ai_character_by_id(db, character_id)

    if name is not None:
        character.name = name
    if description is not None:
        character.description = description
    if system_prompt is not None:
        character.system_prompt = system_prompt
    if is_active is not None:
        character.is_active = is_active

    db.commit()
    db.refresh(character)
    return character


def delete_ai_character(db: Session, character_id: str):
    character = get_ai_character_by_id(db, character_id)
    db.delete(character)
    db.commit()
    return {"deleted": True}
