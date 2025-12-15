import os
from functools import lru_cache

from pydantic import BaseModel
from dotenv import load_dotenv


load_dotenv()


class Settings(BaseModel):
    app_name: str = "LingoBridge API"
    environment: str = os.getenv("ENVIRONMENT", "development")

    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_project_id: str | None = os.getenv("OPENAI_PROJECT_ID")
    openai_grammar_model: str = os.getenv("OPENAI_GRAMMAR_MODEL", "gpt-4.1-mini")
    openai_moderation_model: str = os.getenv(
        "OPENAI_MODERATION_MODEL", "omni-moderation-latest"
    )

    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/lingobridge",
    )

    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")


@lru_cache
def get_settings() -> Settings:
    return Settings()


