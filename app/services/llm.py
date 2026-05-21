from __future__ import annotations

import json
import logging
import re
from typing import Any

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


class LlmUnavailableError(RuntimeError):
    pass


def _normalize_openrouter_api_key(value: str) -> str:
    clean = (value or "").strip().strip('"').strip("'").strip()
    if clean.lower().startswith("bearer "):
        clean = clean[7:].strip()
    return clean


def clean_generated_text(text: str) -> str:
    cleaned = str(text or "").replace("\r\n", "\n").replace("\r", "\n")
    cleaned = re.sub(r"[ \t]+", " ", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


async def openrouter_chat(
    messages: list[dict[str, str]],
    *,
    temperature: float = 0.45,
    max_tokens: int = 900,
) -> str:
    api_key = _normalize_openrouter_api_key(settings.openrouter_api_key)
    if not api_key:
        raise LlmUnavailableError("OPENROUTER_API_KEY is empty")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": settings.public_base_url,
        "X-Title": settings.app_name,
    }
    payload = {
        "model": settings.openrouter_model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
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
        logger.warning("OpenRouter request failed for model %s: %s", settings.openrouter_model, exc)
        raise LlmUnavailableError(f"OpenRouter request failed: {exc}") from exc
    except ValueError as exc:
        logger.warning("OpenRouter returned invalid JSON for model %s", settings.openrouter_model)
        raise LlmUnavailableError("OpenRouter returned invalid JSON") from exc

    try:
        content = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        logger.warning("OpenRouter response has unexpected shape: %s", data)
        raise LlmUnavailableError("OpenRouter response has unexpected shape") from exc

    cleaned = clean_generated_text(str(content))
    if not cleaned:
        logger.warning("OpenRouter returned empty content for model %s", settings.openrouter_model)
        raise LlmUnavailableError("OpenRouter returned empty content")
    return cleaned


def extract_json_object(text: str) -> dict[str, Any]:
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("No JSON object found")
    return json.loads(text[start : end + 1])
