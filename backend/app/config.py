import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class BaseAppSettings(BaseSettings):
    """Core settings properties loaded from environment variables or .env."""
    DATABASE_URL: str = "sqlite:///./aquasentinel.db"
    GEMINI_API_KEY: str = "placeholder_key"
    SECRET_KEY: str = "aquasentinel_super_secret_session_key"
    APP_ENV: str = "development"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    CORS_ORIGINS: str = "http://localhost:5173"
    SUPABASE_URL: str = ""
    SUPABASE_JWT_SECRET: str = ""
    SUPABASE_ANON_KEY: str = ""

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

class DevelopmentSettings(BaseAppSettings):
    APP_ENV: str = "development"

class TestingSettings(BaseAppSettings):
    APP_ENV: str = "testing"
    DATABASE_URL: str = "sqlite:///:memory:"

class ProductionSettings(BaseAppSettings):
    APP_ENV: str = "production"

def get_settings() -> BaseAppSettings:
    """Returns the correct settings configurations class based on APP_ENV environment."""
    env = os.getenv("APP_ENV", "development").lower()
    if env == "production":
        return ProductionSettings()
    elif env == "testing":
        return TestingSettings()
    return DevelopmentSettings()

settings = get_settings()
