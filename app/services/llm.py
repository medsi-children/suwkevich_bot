from __future__ import annotations

import json
import logging
import re
from typing import Any

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)
_OPENROUTER_CLIENT: httpx.AsyncClient | None = None
CONTINUATION_PROMPT = (
    "Продолжи с того места, где остановился. Не начинай заново, "
    "не повторяй уже сказанное и закончи мысль целиком."
)


class LlmUnavailableError(RuntimeError):
    pass


def _normalize_openrouter_api_key(value: str) -> str:
    clean = (value or "").strip().strip('"').strip("'").strip()
    if clean.lower().startswith("bearer "):
        clean = clean[7:].strip()
    return clean


def _ascii_header_value(value: str, *, fallback: str = "") -> str:
    clean = " ".join((value or "").strip().split())
    encoded = clean.encode("ascii", "ignore").decode("ascii").strip()
    return encoded or fallback


def strip_markdown_artifacts(text: str) -> str:
    cleaned = text.replace("**", "").replace("__", "").replace("`", "")
    cleaned = re.sub(r"(?m)^\s{0,3}#{1,6}\s*", "", cleaned)
    cleaned = re.sub(r"(?m)^\s*[-*]\s+(?=\S)", "", cleaned)
    return cleaned


def clean_generated_text(text: str) -> str:
    cleaned = str(text or "").replace("\r\n", "\n").replace("\r", "\n")
    cleaned = strip_markdown_artifacts(cleaned)
    cleaned = re.sub(r"[ \t]+", " ", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


def _create_openrouter_client() -> httpx.AsyncClient:
    try:
        return httpx.AsyncClient(timeout=60, http2=True)
    except ImportError:
        logger.info("HTTP/2 is unavailable because the 'h2' package is not installed; falling back")
        return httpx.AsyncClient(timeout=60)
    except TypeError:
        return httpx.AsyncClient(timeout=60)


async def openrouter_chat(
    messages: list[dict[str, str]],
    *,
    temperature: float = 0.45,
    max_tokens: int = 900,
    continue_on_length: bool = False,
    max_continuations: int = 2,
) -> str:
    api_key = _normalize_openrouter_api_key(settings.openrouter_api_key)
    if not api_key:
        raise LlmUnavailableError("OPENROUTER_API_KEY is empty")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "X-Title": _ascii_header_value(settings.app_name, fallback="Sushkevich Bot"),
    }
    referer = _ascii_header_value(settings.public_base_url)
    if referer:
        headers["HTTP-Referer"] = referer

    attempt_messages = list(messages)
    raw_parts: list[str] = []
    finish_reason = None

    for attempt in range(max_continuations + 1):
        payload = {
            "model": settings.openrouter_model,
            "messages": attempt_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        try:
            global _OPENROUTER_CLIENT
            if _OPENROUTER_CLIENT is None:
                _OPENROUTER_CLIENT = _create_openrouter_client()
            response = await _OPENROUTER_CLIENT.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            body = exc.response.text[:1200]
            logger.warning(
                "OpenRouter returned HTTP %s for model %s: %s",
                exc.response.status_code,
                settings.openrouter_model,
                body,
            )
            raise LlmUnavailableError(
                f"OpenRouter HTTP {exc.response.status_code}: {body[:300]}"
            ) from exc
        except httpx.RequestError as exc:
            logger.warning(
                "OpenRouter request failed for model %s: %s",
                settings.openrouter_model,
                exc,
            )
            raise LlmUnavailableError(f"OpenRouter request failed: {exc}") from exc
        except UnicodeError as exc:
            logger.warning(
                "OpenRouter header encoding failed for model %s: %s",
                settings.openrouter_model,
                exc,
            )
            raise LlmUnavailableError(f"OpenRouter header encoding failed: {exc}") from exc

        try:
            data = response.json()
        except ValueError as exc:
            logger.warning(
                "OpenRouter returned invalid JSON for model %s",
                settings.openrouter_model,
            )
            raise LlmUnavailableError("OpenRouter returned invalid JSON") from exc

        try:
            choice = data["choices"][0]
            content = choice["message"]["content"]
            finish_reason = choice.get("finish_reason")
        except (KeyError, IndexError, TypeError) as exc:
            logger.warning("OpenRouter response has unexpected shape: %s", data)
            raise LlmUnavailableError("OpenRouter response has unexpected shape") from exc

        raw_part = str(content or "").strip()
        if raw_part:
            raw_parts.append(raw_part)
        if not continue_on_length or finish_reason != "length" or attempt >= max_continuations:
            break

        attempt_messages = [
            *messages,
            {"role": "assistant", "content": "\n\n".join(raw_parts)},
            {"role": "user", "content": CONTINUATION_PROMPT},
        ]

    cleaned = clean_generated_text("\n\n".join(part for part in raw_parts if part))
    if not cleaned:
        logger.warning("OpenRouter returned empty content for model %s", settings.openrouter_model)
        raise LlmUnavailableError("OpenRouter returned empty content")
    if continue_on_length and finish_reason == "length":
        logger.warning(
            "OpenRouter response for model %s still ended with length after continuations",
            settings.openrouter_model,
        )
    return cleaned


def extract_json_object(text: str) -> dict[str, Any]:
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("No JSON object found")
    return json.loads(text[start : end + 1])
