from __future__ import annotations

import json
import logging
from typing import Annotated, Any

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import AsyncSessionLocal, get_db
from app.schemas.message import MessageResponse
from app.schemas.user import UserCreate
from app.services.dialogue import add_message, get_active_session, handle_user_text
from app.services.memory import apply_memory_control, store_memory_updates
from app.services.telegram import (
    extract_chat_id,
    extract_message,
    extract_sender,
    send_message,
    support_webapp_reply_markup,
)
from app.services.users import get_or_create_user

router = APIRouter()
logger = logging.getLogger(__name__)
DbSession = Annotated[AsyncSession, Depends(get_db)]


async def build_telegram_response(update: dict[str, Any], db: AsyncSession) -> MessageResponse:
    message = extract_message(update)
    sender = extract_sender(update)
    text = message.get("text")
    web_app_data = message.get("web_app_data") or {}
    if not text and web_app_data.get("data"):
        try:
            payload = json.loads(str(web_app_data["data"]))
        except json.JSONDecodeError:
            payload = {}
        if isinstance(payload, dict):
            candidate = payload.get("text")
            if isinstance(candidate, str):
                text = candidate
    telegram_id = sender.get("id")
    chat_id = extract_chat_id(update)

    if telegram_id is None:
        raise HTTPException(status_code=400, detail="Telegram sender is missing")

    user = await get_or_create_user(
        db,
        UserCreate(
            telegram_id=int(telegram_id),
            username=sender.get("username"),
            first_name=sender.get("first_name"),
            language_code=sender.get("language_code"),
        ),
    )
    session = await get_active_session(db, user, source="telegram")

    if not text:
        reply = "Пока я умею разбирать только текст. Напишите словами, что происходит."
        await add_message(
            db,
            user=user,
            session=session,
            role="assistant",
            content=reply,
            metadata={"telegram_update_id": update.get("update_id"), "chat_id": chat_id},
        )
        await db.commit()
        return MessageResponse(user_id=user.id, session_id=session.id, reply=reply)

    user_message = await add_message(
        db,
        user=user,
        session=session,
        role="user",
        content=text,
        metadata={
            "telegram_update_id": update.get("update_id"),
            "chat_id": chat_id,
            "chat_type": (message.get("chat") or {}).get("type"),
        },
    )
    control_reply = await apply_memory_control(
        db,
        user=user,
        session=session,
        source_message=user_message,
        text=text,
    )
    if control_reply:
        await add_message(db, user=user, session=session, role="assistant", content=control_reply)
        await db.commit()
        return MessageResponse(
            user_id=user.id,
            session_id=session.id,
            reply=control_reply,
            mode="memory_control",
        )

    reply, risk_level = await handle_user_text(db, user=user, session=session, text=text)
    await add_message(db, user=user, session=session, role="assistant", content=reply)
    await store_memory_updates(
        db,
        user=user,
        session=session,
        source_message=user_message,
        user_text=text,
        assistant_reply=reply,
    )
    await db.commit()
    return MessageResponse(
        user_id=user.id,
        session_id=session.id,
        reply=reply,
        risk_level=risk_level,
    )


async def process_direct_telegram_update(update: dict[str, Any]) -> None:
    chat_id = extract_chat_id(update)
    message = extract_message(update)
    text = str(message.get("text") or "").strip().lower()
    command = text.split(maxsplit=1)[0] if text else ""
    async with AsyncSessionLocal() as db:
        try:
            response = await build_telegram_response(update, db)
            if chat_id is not None:
                reply_markup = (
                    support_webapp_reply_markup()
                    if command in {"/start", "/help"}
                    else None
                )
                await send_message(chat_id, response.reply, reply_markup=reply_markup)
        except Exception:
            await db.rollback()
            logger.exception("Failed to process Telegram update")
            if chat_id is not None:
                await send_message(
                    chat_id,
                    "Сейчас не получилось ответить. Попробуйте написать еще раз чуть позже.",
                )


@router.post("/webhook", response_model=MessageResponse)
async def telegram_webhook(
    update: dict[str, Any],
    db: DbSession,
) -> MessageResponse:
    return await build_telegram_response(update, db)


@router.post("/direct-webhook")
async def telegram_direct_webhook(
    update: dict[str, Any],
    background_tasks: BackgroundTasks,
    request: Request,
) -> dict[str, bool]:
    secret = settings.telegram_webhook_secret_token.strip()
    if secret and request.headers.get("X-Telegram-Bot-Api-Secret-Token") != secret:
        raise HTTPException(status_code=403, detail="Invalid Telegram webhook secret")
    background_tasks.add_task(process_direct_telegram_update, update)
    return {"ok": True}
