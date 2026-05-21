from __future__ import annotations

import json
import re
from typing import Any

import httpx

from app.core.config import settings


class LlmUnavailableError(RuntimeError):
    pass


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
    if not settings.openrouter_api_key:
        raise LlmUnavailableError("OPENROUTER_API_KEY is empty")

    headers = {
        "Authorization": f"Bearer {settings.openrouter_api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": settings.public_base_url,
    }
    payload = {
        "model": settings.openrouter_model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
        )
        response.raise_for_status()
        data = response.json()
        return clean_generated_text(str(data["choices"][0]["message"]["content"]))


def extract_json_object(text: str) -> dict[str, Any]:
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("No JSON object found")
    return json.loads(text[start : end + 1])

