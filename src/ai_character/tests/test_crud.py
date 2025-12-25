from unittest.mock import MagicMock
import pytest
from crud import (
    get_ai_character_by_id,
    get_ai_character_by_slug,
    create_ai_character,
    list_ai_characters,
)
from fastapi import HTTPException


def test_get_character_by_id_failed():
    # arrange
    db = MagicMock()
    db.query().filter().first.return_value = None

    # act
    with pytest.raises(HTTPException) as exec_info:
        get_ai_character_by_id(db, "fake-id")

    # assert
    assert exec_info.value.status_code == 404
    assert exec_info.value.detail == "AI character not found"


def test_get_character_by_id_success():
    db = MagicMock()

    fake_character = MagicMock()
    fake_character.id = "char-123"

    db.query().filter().first.return_value = fake_character

    result = get_ai_character_by_id(db, "char-123")

    assert result == fake_character


def test_get_character_by_slug_failed():
    db = MagicMock()

    db.query().filter().first.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        get_ai_character_by_slug(db, "fake-slug")

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "AI character not found"


def test_get_character_by_slug_success():
    db = MagicMock()

    fake_character = MagicMock()
    fake_character.slug = "tony-stark"

    db.query().filter().first.return_value = fake_character

    result = get_ai_character_by_slug(db, "tony-stark")

    assert result == fake_character


def test_create_ai_character_failed():
    db = MagicMock()

    fake_character = MagicMock()
    fake_character.id = "char-123"
    fake_character.name = "Tony Stark"
    fake_character.slug = "tony-stark"
    fake_character.description = "abc"
    fake_character.system_prompt = "abc"

    db.query().filter().first.return_value = fake_character

    with pytest.raises(HTTPException) as exc_info:
        create_ai_character(db, "Tony Stark", "tony-stark", "abc", "abc")

    assert exc_info.value.status_code == 409
    assert exc_info.value.detail == "AI character with this slug already exists"


def test_create_ai_character_succes():
    db = MagicMock()

    db.query().filter().first.return_value = None

    result = create_ai_character(
        db,
        "Tony Stark",
        "tony-stark",
        "abc",
        "abc",
    )

    assert result.name == "Tony Stark"
    assert result.slug == "tony-stark"
    assert result.description == "abc"
    assert result.system_prompt == "abc"

    db.add.assert_called_once()
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(result)


def test_list_ai_characters_with_active_only():
    """Test listing only active characters."""
    db = MagicMock()

    fake_char1 = MagicMock()
    fake_char1.id = "char-1"
    fake_char1.name = "Tony Stark"
    fake_char1.is_active = True

    fake_char2 = MagicMock()
    fake_char2.id = "char-2"
    fake_char2.name = "Steve Rogers"
    fake_char2.is_active = True

    # Mock the chain: db.query().filter().offset().limit().all()
    mock_query = db.query.return_value
    mock_filtered = mock_query.filter.return_value
    mock_offset = mock_filtered.offset.return_value
    mock_offset.limit.return_value.all.return_value = [fake_char1, fake_char2]

    result = list_ai_characters(db, skip=0, limit=20, active_only=True)

    assert len(result) == 2
    assert result[0].name == "Tony Stark"
    assert result[1].name == "Steve Rogers"
    mock_query.filter.assert_called_once()


def test_list_ai_characters_empty():
    """Test listing when no characters exist."""
    db = MagicMock()

    mock_query = db.query.return_value
    mock_filtered = mock_query.filter.return_value
    mock_offset = mock_filtered.offset.return_value
    mock_offset.limit.return_value.all.return_value = []

    result = list_ai_characters(db)

    assert result == []
    assert len(result) == 0
