"""Application settings — loaded from environment variables / .env, validated by Pydantic."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    #Database
    database_url: str


    #Auth / JWT
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30


    #Redis (cache) + Celery (broker/backend)
    redis_url: str = "redis://localhost:6379/1"
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/0"

    # Google Gemini
    google_api_key: str
    gemini_model: str = "gemini-2.0-flash"



@lru_cache
def get_settings() -> Settings:
        return Settings()
    

settings = get_settings()

