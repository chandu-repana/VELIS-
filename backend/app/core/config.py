from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "VELIS"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # Security
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    JWT_SECRET_KEY: str = "dev-jwt-secret-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60

    # Database
    DATABASE_URL: str = "postgresql://velis_user:velis_password@localhost:5432/velis_db"

    # CORS
    FRONTEND_URL: str = "http://localhost:3000"

    # File Upload
    MAX_UPLOAD_SIZE_MB: int = 10
    UPLOAD_DIR: str = "uploads/"

    # AI Models
    WHISPER_MODEL: str = "base"
    HF_MODEL_NAME: str = "google/flan-t5-base"

    class Config:
        env_file = ".env"
        case_sensitive = True


# Single instance used across the entire application
settings = Settings()