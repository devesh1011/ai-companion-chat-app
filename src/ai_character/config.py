from pydantic_settings import BaseSettings
from functools import lru_cache
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # App Configuration
    app_name: str = "Vyloc API"
    app_version: str = "0.1.0"
    debug: bool = False
    env: str = "development"

    DB_HOST: str = os.getenv("DB_HOST", "postgres-headless")
    DB_PORT: str = os.getenv("DB_PORT", "5432")
    DB_USER: str = os.getenv("DB_USER", "postgres")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "mysecretpassword")
    DB_NAME: str = os.getenv("DB_NAME", "character")


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
