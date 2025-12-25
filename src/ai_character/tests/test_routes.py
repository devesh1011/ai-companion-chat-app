from fastapi import HTTPException
from unittest.mock import MagicMock, patch
from uuid import uuid4
from datetime import datetime


def test_create_ai_character_route_success(client):
    """Test creating AI character via POST /api/characters/"""
    with patch("routers.create_ai_character") as mock_create:
        fake_character = MagicMock()
        fake_character.id = uuid4()
        fake_character.name = "Tony Stark"
        fake_character.slug = "tony-stark"
        fake_character.description = "Genius billionaire"
        fake_character.system_prompt = "You are Tony Stark"
        fake_character.is_active = True
        fake_character.created_at = datetime.now()

        mock_create.return_value = fake_character

        response = client.post(
            "/api/characters/",
            json={
                "name": "Tony Stark",
                "slug": "tony-stark",
                "description": "Genius billionaire",
                "system_prompt": "You are Tony Stark",
            },
        )

        assert response.status_code == 200
        assert response.json()["slug"] == "tony-stark"
        assert response.json()["name"] == "Tony Stark"


def test_create_ai_character_route_conflict(monkeypatch, client):
    def fake_create_ai_character(*args, **kwargs):
        raise HTTPException(
            status_code=409,
            detail="AI character with this slug already exists",
        )

    monkeypatch.setattr(
        "routers.create_ai_character",
        fake_create_ai_character,
    )

    response = client.post(
        "/api/characters/",
        json={
            "name": "Tony Stark",
            "slug": "tony-stark",
            "description": "abc",
            "system_prompt": "abc",
        },
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "AI character with this slug already exists"


def test_get_ai_char_by_id_success(monkeypatch, client):
    fake_character = {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "name": "Tony Stark",
        "slug": "tony-stark",
        "description": "abc",
        "system_prompt": "abc",
        "is_active": True,
        "created_at": datetime.now(),
    }

    def fake_get_ai_character_by_id(*args, **kwargs):
        return fake_character

    monkeypatch.setattr(
        "routers.get_ai_character_by_id",
        fake_get_ai_character_by_id,
    )

    response = client.get("/api/characters/id/550e8400-e29b-41d4-a716-446655440000")

    assert response.status_code == 200
    assert response.json()["slug"] == "tony-stark"


def test_get_ai_char_by_id_failed(monkeypatch, client):
    fake_character = None

    def fake_get_ai_character_by_id(*args, **kwargs):
        return fake_character

    monkeypatch.setattr("routers.get_ai_character_by_id", fake_get_ai_character_by_id)

    response = client.get("/api/characters/id/550e8400-e29b-41d4-a716-446655440000")

    assert response.status_code == 404
    assert response.json()["detail"] == "Character not found"


def test_get_all_ai_chars(client):
    """Test getting all characters"""
    with patch("routers.list_ai_characters") as mock_list:
        char_id1 = uuid4()
        char_id2 = uuid4()

        fake_char1 = MagicMock()
        fake_char1.id = char_id1
        fake_char1.name = "Tony Stark"
        fake_char1.slug = "tony-stark"
        fake_char1.is_active = True
        fake_char1.created_at = datetime.now()
        fake_char1.description = "Genius billionaire"
        fake_char1.system_prompt = "You are Tony"

        fake_char2 = MagicMock()
        fake_char2.id = char_id2
        fake_char2.name = "Steve Rogers"
        fake_char2.slug = "steve-rogers"
        fake_char2.is_active = True
        fake_char2.created_at = datetime.now()
        fake_char2.description = "Super soldier"
        fake_char2.system_prompt = "You are Steve"

        mock_list.return_value = [fake_char1, fake_char2]

        response = client.get("/api/characters/")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
