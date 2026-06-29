"""LifeOS AI — Configuration"""
from pydantic_settings import BaseSettings
from functools import lru_cache
import os


class Settings(BaseSettings):
    # App
    app_name: str = "LifeOS AI"
    app_version: str = "1.0.0"
    debug: bool = False
    environment: str = "development"

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000", "http://localhost:3711"]

    # Database
    database_url: str = "sqlite+aiosqlite:///./lifeos.db"

    # Auth
    secret_key: str = "lifeos-super-secret-key-change-in-production-32chars"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 43200  # 30 days

    # OpenAI
    openai_api_key: str = ""
    openai_model: str = "gpt-4o"
    openai_embedding_model: str = "text-embedding-3-small"

    # Lemma SDK
    lemma_server_url: str = "http://localhost:8711"
    lemma_api_key: str = ""
    lemma_pod_name: str = "lifeos-ai"
    lemma_enabled: bool = True

    # Vector DB (ChromaDB)
    chroma_host: str = "localhost"
    chroma_port: int = 8001
    chroma_collection: str = "lifeos_memories"

    # File uploads
    upload_dir: str = "./uploads"
    max_file_size_mb: int = 50
    allowed_extensions: list[str] = [".pdf", ".png", ".jpg", ".jpeg", ".txt", ".docx"]

    # Agent settings
    agent_max_tokens: int = 4096
    agent_temperature: float = 0.3
    workflow_timeout_seconds: int = 120

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
