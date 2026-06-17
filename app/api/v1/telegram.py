from __future__ import annotations

import asyncio
import json
import logging
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import AsyncSessionLocal, get_db
from app.schemas.message import MessageResponse
from app.schemas.user import UserCreate
from app.services.dialogue import add_message, get_active_session, handle_user_text
from app.services.memory import apply_memory_control, store_memory_updates_deferred
from app.services.telegram import (
    delete_message,
    extract_chat_id,
    extract_message,
    extract_sender,
    send_message,
    split_telegram_text,
)
from app.services.users import get_or_create_user

router = APIRouter()
logger = logging.getLogger(__name__)
DbSession = Annotated[AsyncSession, Depends(get_db)]
LOADING_MESSAGE_VARIANTS = (
    "<code>Анализируем...</code>",
    "<code>Одну минутку...</code>",
    "<code>Генерируем ответ...</code>",
)


def _telegram_webhook_message(chat_id: int, text: str) -> dict[str, Any]:
    chunks = split_telegram_text(text)
    return {
        "method": "sendMessage",
        "chat_id": chat_id,
        "text": chunks[0] if chunks else "Готово.",
        "disable_web_page_preview": True,
    }


def _extract_text_from_update(update: dict[str, Any]) -> str:
    message = extract_message(update)
    text = message.get("text")
    web_app_data = message.get("web_app_data") or {}
    if not text and web_app_data.get("data"):
        try:
            payload = json.loads(str(web_app_data["data"]))
        except json.JSONDecodeError:
            payload = {}
        if isinstance(payload, dict) and isinstance(payload.get("text"), str):
            text = payload["text"]
    return str(text or "").strip()


def should_show_loading_message(update: dict[str, Any]) -> bool:
    text = _extract_text_from_update(update)
    return bool(text) and not text.startswith("/")


def pick_loading_message(update: dict[str, Any]) -> str:
    text = _extract_text_from_update(update)
    if not text:
        return LOADING_MESSAGE_VARIANTS[0]
    index = sum(ord(char) for char in text) % len(LOADING_MESSAGE_VARIANTS)
    return LOADING_MESSAGE_VARIANTS[index]


async def build_telegram_response(update: dict[str, Any], db: AsyncSession) -> MessageResponse:
    message = extract_message(update)
    sender = extract_sender(update)
    text = _extract_text_from_update(update)
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
    user_id = user.id
    session_id = session.id
    source_message_id = user_message.id
    await db.commit()
    asyncio.create_task(
        store_memory_updates_deferred(
            user_id=user_id,
            session_id=session_id,
            source_message_id=source_message_id,
            user_text=text,
            assistant_reply=reply,
        )
    )
    return MessageResponse(
        user_id=user.id,
        session_id=session.id,
        reply=reply,
        risk_level=risk_level,
    )


async def process_direct_telegram_update(update: dict[str, Any]) -> None:
    chat_id = extract_chat_id(update)
    loading_message_id: int | None = None
    if chat_id is not None and _extract_text_from_update(update).casefold() == "/ping":
        try:
            await send_message(chat_id, "pong")
        except Exception:
            logger.exception("Failed to send Telegram ping response")
        return
    async with AsyncSessionLocal() as db:
        try:
            if chat_id is not None and should_show_loading_message(update):
                loading_responses = await send_message(
                    chat_id,
                    pick_loading_message(update),
                    parse_mode="HTML",
                    clean=False,
                )
                loading_result = (
                    (loading_responses[0].get("result") or {}) if loading_responses else {}
                )
                loading_message_id = loading_result.get("message_id")
            response = await build_telegram_response(update, db)
            if chat_id is not None and loading_message_id is not None:
                await delete_message(chat_id, loading_message_id)
            if chat_id is not None:
                await send_message(chat_id, response.reply)
        except Exception:
            await db.rollback()
            logger.exception("Failed to process Telegram update")
            if chat_id is not None:
                if loading_message_id is not None:
                    await delete_message(chat_id, loading_message_id)
                await send_message(
                    chat_id,
                    "Кажется, что-то пошло не так. Попробуйте написать мне чуть позже 🙏",
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
    request: Request,
) -> dict[str, Any]:
    secret = settings.telegram_webhook_secret_token.strip()
    if secret and request.headers.get("X-Telegram-Bot-Api-Secret-Token") != secret:
        raise HTTPException(status_code=403, detail="Invalid Telegram webhook secret")
    chat_id = extract_chat_id(update)
    if chat_id is None:
        asyncio.create_task(process_direct_telegram_update(update))
        return {"ok": True}
    if _extract_text_from_update(update).casefold() == "/ping":
        return _telegram_webhook_message(chat_id, "pong")

    async with AsyncSessionLocal() as db:
        try:
            response = await build_telegram_response(update, db)
        except Exception:
            await db.rollback()
            logger.exception("Failed to process Telegram update")
            return _telegram_webhook_message(
                chat_id,
                "Кажется, что-то пошло не так. Попробуйте написать мне чуть позже 🙏",
            )

    return _telegram_webhook_message(chat_id, response.reply)
