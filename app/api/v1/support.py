from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.user import UserCreate
from app.services.support_profile import build_support_profile
from app.services.telegram_auth import TelegramWebAppAuthError, verify_telegram_webapp_user
from app.services.users import get_or_create_user

router = APIRouter()
DbSession = Annotated[AsyncSession, Depends(get_db)]


class SupportProfileRequest(BaseModel):
    telegram_id: int = Field(gt=0)
    init_data: str | None = None
    username: str | None = None
    first_name: str | None = None
    language_code: str | None = None


@router.post("/me")
async def read_support_profile(
    payload: SupportProfileRequest,
    db: DbSession,
) -> dict[str, Any]:
    try:
        verify_telegram_webapp_user(payload.init_data, payload.telegram_id)
    except TelegramWebAppAuthError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc

    user = await get_or_create_user(
        db,
        UserCreate(
            telegram_id=payload.telegram_id,
            username=payload.username,
            first_name=payload.first_name,
            language_code=payload.language_code,
        ),
    )
    profile = await build_support_profile(db, user)
    await db.commit()
    return profile
