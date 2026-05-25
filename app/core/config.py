from __future__ import annotations

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


def _normalize_database_url(url: str, *, async_driver: bool) -> str:
    clean = url.strip()
    if async_driver:
        if clean.startswith("postgresql://"):
            return clean.replace("postgresql://", "postgresql+asyncpg://", 1)
        if clean.startswith("postgres://"):
            return clean.replace("postgres://", "postgresql+asyncpg://", 1)
        if clean.startswith("postgresql+psycopg://"):
            return clean.replace("postgresql+psycopg://", "postgresql+asyncpg://", 1)
        return clean

    if clean.startswith("postgresql://"):
        return clean.replace("postgresql://", "postgresql+psycopg://", 1)
    if clean.startswith("postgres://"):
        return clean.replace("postgres://", "postgresql+psycopg://", 1)
    if clean.startswith("postgresql+asyncpg://"):
        return clean.replace("postgresql+asyncpg://", "postgresql+psycopg://", 1)
    return clean


class Settings(BaseSettings):
    app_name: str = "Сушкевич Бот"
    app_env: str = "local"
    api_v1_prefix: str = "/api/v1"
    public_base_url: str = "http://localhost:8000"
    public_webapp_url: str = ""

    database_url: str = "postgresql+asyncpg://suwkevich:suwkevich@localhost:5432/suwkevich_bot"
    sync_database_url: str = ""

    openrouter_api_key: str = ""
    openrouter_model: str = "openai/gpt-oss-120b:free"
    telegram_bot_token: str = ""
    telegram_webhook_secret_token: str = ""
    consultation_requests_chat_id: int = 7659888703

    clinical_knowledge_path: str = "app/knowledge/clinical_orientation.md"
    clinical_knowledge_max_chars: int = 5200
    memory_extraction_enabled: bool = True

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @computed_field
    @property
    def sqlalchemy_database_url(self) -> str:
        return _normalize_database_url(self.database_url, async_driver=True)

    @computed_field
    @property
    def sqlalchemy_sync_database_url(self) -> str:
        source = self.sync_database_url or self.database_url
        return _normalize_database_url(source, async_driver=False)

    @computed_field
    @property
    def webhook_url(self) -> str:
        base = self.public_base_url.strip().rstrip("/")
        return f"{base}{self.api_v1_prefix}/telegram/direct-webhook"

    @computed_field
    @property
    def support_webapp_url(self) -> str:
        if self.public_webapp_url.strip():
            return self.public_webapp_url.strip()
        base = self.public_base_url.strip().rstrip("/")
        return f"{base}/app/support"


settings = Settings()
