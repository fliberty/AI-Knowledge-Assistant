"""Application settings."""

from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")


class Settings(BaseSettings):
    """Global application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = Field(default="AI Knowledge Assistant")
    app_version: str = Field(default="0.1.0")
    debug: bool = Field(default=False)
    log_level: str = Field(default="INFO")

    openai_api_key: str = Field(default="")
    openai_base_url: str | None = Field(default=None)
    openai_model_name: str = Field(default="gpt-4o")
    openai_embedding_model: str = Field(default="text-embedding-3-small")

    qdrant_host: str = Field(default="localhost")
    qdrant_port: int = Field(default=6333)
    qdrant_collection_name: str = Field(default="knowledge_base")
    qdrant_api_key: str = Field(default="")

    chunk_size: int = Field(default=1000)
    chunk_overlap: int = Field(default=200)
    max_upload_size_mb: int = Field(default=20)
    max_chat_history_messages: int = Field(default=8)


@lru_cache
def get_settings() -> Settings:
    """Return the cached settings singleton."""

    return Settings()
