from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://scientia:password@localhost:5432/scientia"
    REDIS_URL: str = "redis://localhost:6379/0"
    SECRET_KEY: str = "change-this-secret-key-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    CLOUDINARY_CLOUD_NAME: str = ""
    CLOUDINARY_API_KEY: str = ""
    CLOUDINARY_API_SECRET: str = ""
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:3000/auth/google/callback"
    ANTHROPIC_API_KEY: str = ""
    APP_NAME: str = "Scientia AI"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    ALGORITHM: str = "HS256"
    FAISS_INDEX_PATH: str = "./faiss_indexes"
    MAX_FILE_SIZE_MB: int = 50

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
