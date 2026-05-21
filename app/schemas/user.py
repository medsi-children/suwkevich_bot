from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class UserCreate(BaseModel):
    telegram_id: int | None = None
    username: str | None = None
    first_name: str | None = None
    language_code: str | None = None


class UserRead(BaseModel):
    id: UUID
    telegram_id: int | None
    username: str | None
    first_name: str | None
    language_code: str | None
    profile_summary: str | None
    support_preferences: dict
    risk_notes: str | None
    created_at: datetime
    updated_at: datetime
    last_seen_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


class MemoryRead(BaseModel):
    id: UUID
    memory_type: str
    title: str
    content: str
    importance: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

