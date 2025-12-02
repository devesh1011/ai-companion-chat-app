from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    # DB Config
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: str = os.getenv("DB_PORT", "5432")
    DB_USER: str = os.getenv("DB_USER", "postgres")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "haunted97!")
    DB_NAME: str = os.getenv("DB_NAME", "postgres")

    JWT_SECRET: str = os.getenv(
        "JWT_SECRET", "61587d1f1b1139e59061068cf33e46e5f6b08a91adb6f1ad40284ac107d9e1e9"
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30


def get_settings() -> Settings:
    return Settings()
