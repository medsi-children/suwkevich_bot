from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.user import UserCreate
from app.services.memory import generate_lifehack_for_profile
from app.services.support_profile import (
    build_support_profile,
    delete_manual_diary_item,
    upsert_manual_diary_item,
)
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


class SupportDiaryUpsertRequest(SupportProfileRequest):
    item_id: str | None = None
    title: str = Field(min_length=1, max_length=78)
    text: str = Field(min_length=1, max_length=240)
    theme: str | None = None


class SupportDiaryDeleteRequest(SupportProfileRequest):
    item_id: str = Field(min_length=1, max_length=80)


class SupportLifehackGenerateRequest(SupportProfileRequest):
    prompt: str = Field(min_length=1, max_length=220)


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


@router.post("/diary/upsert")
async def upsert_support_diary_item(
    payload: SupportDiaryUpsertRequest,
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
    upsert_manual_diary_item(
        user,
        item_id=payload.item_id,
        title=payload.title,
        text=payload.text,
        theme=payload.theme,
    )
    profile = await build_support_profile(db, user)
    await db.commit()
    return profile


@router.post("/diary/delete")
async def delete_support_diary_entry(
    payload: SupportDiaryDeleteRequest,
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
    delete_manual_diary_item(user, payload.item_id)
    profile = await build_support_profile(db, user)
    await db.commit()
    return profile


@router.post("/lifehacks/generate")
async def generate_support_lifehack(
    payload: SupportLifehackGenerateRequest,
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
    item = await generate_lifehack_for_profile(
        db,
        user=user,
        prompt_text=payload.prompt,
    )
    if item is None:
        raise HTTPException(status_code=503, detail="Не получилось подготовить лайфхак")
    profile = await build_support_profile(db, user)
    await db.commit()
    return profile
