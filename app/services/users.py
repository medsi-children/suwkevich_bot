from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.user import UserCreate


PREFERRED_FIRST_NAME_KEY = "_preferred_first_name"


async def get_or_create_user(db: AsyncSession, payload: UserCreate) -> User:
    user: User | None = None
    if payload.telegram_id is not None:
        result = await db.execute(select(User).where(User.telegram_id == payload.telegram_id))
        user = result.scalar_one_or_none()

    now = datetime.now(UTC)
    if user is None:
        user = User(
            telegram_id=payload.telegram_id,
            username=payload.username,
            first_name=payload.first_name,
            language_code=payload.language_code,
            support_preferences={},
            last_seen_at=now,
        )
        db.add(user)
        await db.flush()
        return user

    user.username = payload.username or user.username

    preferences = user.support_preferences or {}
    has_preferred_first_name = bool(preferences.get(PREFERRED_FIRST_NAME_KEY))
    if payload.first_name and not has_preferred_first_name:
        user.first_name = payload.first_name

    user.language_code = payload.language_code or user.language_code
    user.last_seen_at = now
    await db.flush()
    return user

