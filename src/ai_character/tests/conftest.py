"""Pytest configuration for AI Character Service tests."""

import sys
from pathlib import Path

# Add parent directory to path so imports work
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from unittest.mock import MagicMock
from main import app
from db import get_db
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """Provide a test client with mocked database dependency."""

    def override_get_db():
        db = MagicMock()
        yield db

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()
