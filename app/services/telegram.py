from __future__ import annotations

import logging
from typing import Any

import httpx

from app.core.config import settings
from app.services.llm import clean_generated_text

logger = logging.getLogger(__name__)
MAX_TELEGRAM_TEXT = 3900
DEFAULT_TELEGRAM_COMMANDS = (
    {
        "command": "start",
        "description": "Запустить бота и начать диалог",
    },
    {
        "command": "consultation",
        "description": "Оставить заявку на консультацию",
    },
)


class TelegramApiError(RuntimeError):
    pass


async def telegram_api(method: str, payload: dict[str, Any]) -> dict[str, Any]:
    if not settings.telegram_bot_token:
        raise TelegramApiError("TELEGRAM_BOT_TOKEN is empty")

    url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/{method}"
    async with httpx.AsyncClient(timeout=45) as client:
        try:
            response = await client.post(url, json=payload)
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            logger.exception(
                "Telegram API %s failed with HTTP %s: %s",
                method,
                exc.response.status_code,
                exc.response.text,
            )
            raise
        except httpx.HTTPError:
            logger.exception("Telegram API %s request failed", method)
            raise
        data = response.json()
        if not data.get("ok"):
            logger.error("Telegram API %s returned error: %s", method, data)
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


async def send_message(
    chat_id: int | str,
    text: str,
    *,
    parse_mode: str | None = None,
    clean: bool = True,
) -> list[dict[str, Any]]:
    clean_text = clean_generated_text(text) if clean else text.strip()
    responses: list[dict[str, Any]] = []
    for chunk in split_telegram_text(clean_text):
        payload: dict[str, Any] = {
            "chat_id": chat_id,
            "text": chunk,
            "disable_web_page_preview": True,
        }
        if parse_mode:
            payload["parse_mode"] = parse_mode
        responses.append(await telegram_api("sendMessage", payload))
    return responses


def consultation_request_targets() -> list[int | str]:
    targets: list[int | str] = []
    username = settings.consultation_requests_chat_username.strip()
    chat_id = str(settings.consultation_requests_chat_id).strip()
    extra_chat_ids = [
        item.strip()
        for item in str(settings.consultation_requests_extra_chat_ids).split(",")
        if item.strip()
    ]

    if username:
        targets.append(username if username.startswith("@") else f"@{username}")
    if chat_id:
        if chat_id.lstrip("-").isdigit():
            targets.append(int(chat_id))
        else:
            targets.append(chat_id)
    for extra_chat_id in extra_chat_ids:
        if extra_chat_id.lstrip("-").isdigit():
            targets.append(int(extra_chat_id))
        else:
            targets.append(extra_chat_id)

    unique_targets: list[int | str] = []
    seen: set[str] = set()
    for target in targets:
        key = str(target)
        if key in seen:
            continue
        seen.add(key)
        unique_targets.append(target)
    return unique_targets


def build_consultation_request_text(
    *,
    full_name: str,
    phone: str,
    telegram_username: str | None,
    message: str,
) -> str:
    username = (
        f"@{telegram_username.strip()}"
        if telegram_username and telegram_username.strip()
        else "не указан"
    )
    return (
        f"Имя: {full_name.strip()}\n"
        f"Телефон: {phone.strip()}\n"
        f"Телеграм: {username}\n"
        f"Сообщение: {message.strip()}"
    )


async def send_consultation_request(
    *,
    full_name: str,
    phone: str,
    telegram_username: str | None,
    message: str,
) -> list[dict[str, Any]]:
    text = build_consultation_request_text(
        full_name=full_name,
        phone=phone,
        telegram_username=telegram_username,
        message=message,
    )
    responses: list[dict[str, Any]] = []
    errors: list[Exception] = []
    for target in consultation_request_targets():
        try:
            responses.extend(await send_message(target, text))
        except Exception as exc:
            errors.append(exc)
            logger.exception("Failed to deliver consultation request to Telegram target %s", target)
    if responses:
        return responses
    if errors:
        raise errors[-1]
    raise TelegramApiError("Consultation destination is not configured")


async def delete_message(chat_id: int, message_id: int) -> None:
    try:
        await telegram_api("deleteMessage", {"chat_id": chat_id, "message_id": message_id})
    except Exception:
        logger.exception("Failed to delete Telegram message %s in chat %s", message_id, chat_id)


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


async def sync_telegram_commands() -> str:
    data = await telegram_api("setMyCommands", {"commands": list(DEFAULT_TELEGRAM_COMMANDS)})
    return str(data.get("description") or "Команды бота обновлены.")
