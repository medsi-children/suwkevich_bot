from __future__ import annotations

import logging
from typing import Any

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)
MAX_TELEGRAM_TEXT = 3900


class TelegramApiError(RuntimeError):
    pass


async def telegram_api(method: str, payload: dict[str, Any]) -> dict[str, Any]:
    if not settings.telegram_bot_token:
        raise TelegramApiError("TELEGRAM_BOT_TOKEN is empty")

    url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/{method}"
    async with httpx.AsyncClient(timeout=45) as client:
        response = await client.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        if not data.get("ok"):
            raise TelegramApiError(str(data))
        return data


def extract_message(update: dict[str, Any]) -> dict[str, Any]:
    return update.get("message") or update.get("edited_message") or {}


def extract_sender(update: dict[str, Any]) -> dict[str, Any]:
    message = extract_message(update)
    return message.get("from") or message.get("chat") or {}


def extract_chat_id(update: dict[str, Any]) -> int | None:
    message = extract_message(update)
    chat = message.get("chat") or {}
    chat_id = chat.get("id")
    return int(chat_id) if chat_id is not None else None


def split_telegram_text(text: str) -> list[str]:
    clean = text.strip()
    if not clean:
        return []
    chunks: list[str] = []
    remaining = clean
    while len(remaining) > MAX_TELEGRAM_TEXT:
        split_at = remaining.rfind("\n\n", 0, MAX_TELEGRAM_TEXT)
        if split_at < MAX_TELEGRAM_TEXT // 2:
            split_at = remaining.rfind("\n", 0, MAX_TELEGRAM_TEXT)
        if split_at < MAX_TELEGRAM_TEXT // 2:
            split_at = MAX_TELEGRAM_TEXT
        chunks.append(remaining[:split_at].strip())
        remaining = remaining[split_at:].strip()
    if remaining:
        chunks.append(remaining)
    return chunks


async def send_message(chat_id: int, text: str) -> None:
    for chunk in split_telegram_text(text):
        await telegram_api(
            "sendMessage",
            {
                "chat_id": chat_id,
                "text": chunk,
                "disable_web_page_preview": True,
            },
        )


async def sync_direct_telegram_webhook() -> str:
    webhook_url = settings.webhook_url
    if not webhook_url.startswith("https://"):
        return "Webhook не установлен: PUBLIC_BASE_URL должен быть публичным HTTPS URL."

    payload: dict[str, Any] = {
        "url": webhook_url,
        "allowed_updates": ["message", "edited_message"],
        "drop_pending_updates": False,
    }
    if settings.telegram_webhook_secret_token.strip():
        payload["secret_token"] = settings.telegram_webhook_secret_token.strip()

    data = await telegram_api("setWebhook", payload)
    return str(data.get("description") or "Webhook установлен.")

