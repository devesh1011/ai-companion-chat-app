"""Pytest configuration for AI Character Service tests."""

import sys
import os
from pathlib import Path
from unittest.mock import patch

# Add parent directory to path so imports work
sys.path.insert(0, str(Path(__file__).parent.parent))

# Mock the database URL creation before importing the app
# This prevents the app from trying to connect to postgres-headless during tests
with patch.dict(
    os.environ,
    {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "DB_USER": "test",
        "DB_PASSWORD": "test",
        "DB_NAME": "test_db",
    },
):
    from app.main import app
    from app.db import get_db, Base

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

# Create test database engine (in-memory SQLite)
TEST_DATABASE_URL = "sqlite:///:memory:"
test_engine = create_engine(
    TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="function")
def db():
    """Create a fresh test database for each test."""
    Base.metadata.create_all(bind=test_engine)
    session = TestingSessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def client(db):
    """Provide a test client with in-memory SQLite database."""

    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()
