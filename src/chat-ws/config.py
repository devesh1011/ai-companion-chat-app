from pydantic_settings import BaseSettings
from functools import lru_cache
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # App Configuration
    app_name: str = "websocket chat service"
    app_version: str = "0.1.0"
    debug: bool = False
    env: str = "development"

    DB_HOST: str = os.getenv("DB_HOST", "postgres-headless")
    DB_PORT: str = os.getenv("DB_PORT", "5432")
    DB_USER: str = os.getenv("DB_USER", "chat_user")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")
    DB_NAME: str = os.getenv("DB_NAME", "chat_db")

    AUTH_SVC_ADDR: str = os.getenv("AUTH_SVC_ADDR", "ai-companion-auth-service:3001")

    RABBITMQ_HOST: str = os.getenv("RABBITMQ_HOST", "rabbitmq-headless")


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
