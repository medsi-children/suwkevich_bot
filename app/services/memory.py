from __future__ import annotations

import logging
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.memory import UserMemory
from app.models.message import Message
from app.models.session import ConversationSession
from app.models.user import User
from app.services.llm import extract_json_object, openrouter_chat

logger = logging.getLogger(__name__)

MEMORY_TYPES = {
    "profile",
    "situation",
    "insight",
    "goal",
    "risk",
    "preference",
    "support_strategy",
}


async def get_relevant_memories(
    db: AsyncSession,
    user: User,
    *,
    limit: int = 10,
) -> list[UserMemory]:
    result = await db.execute(
        select(UserMemory)
        .where(UserMemory.user_id == user.id)
        .order_by(UserMemory.importance.desc(), UserMemory.updated_at.desc())
        .limit(limit)
    )
    return list(result.scalars().all())


def format_memory_context(user: User, memories: list[UserMemory]) -> str:
    parts: list[str] = []
    if user.profile_summary:
        parts.append(f"Краткий профиль пользователя: {user.profile_summary}")
    if user.risk_notes:
        parts.append(f"Важные риски и осторожность: {user.risk_notes}")
    if user.support_preferences:
        parts.append(f"Предпочтения поддержки: {user.support_preferences}")
    if memories:
        memory_lines = [
            f"- {memory.memory_type}: {memory.title}. {memory.content}"
            for memory in memories
        ]
        parts.append("Память о пользователе:\n" + "\n".join(memory_lines))
    return "\n\n".join(parts).strip()


def _normalize_importance(value: Any) -> int:
    try:
        importance = int(value)
    except (TypeError, ValueError):
        return 3
    return max(1, min(5, importance))


async def store_memory_updates(
    db: AsyncSession,
    *,
    user: User,
    session: ConversationSession,
    source_message: Message,
    user_text: str,
    assistant_reply: str,
) -> None:
    if not settings.memory_extraction_enabled:
        return
    if not settings.openrouter_api_key:
        return
    if user_text.strip().startswith("/"):
        return

    prompt = (
        "Ты извлекаешь долговременную память для терапевтически ориентированного бота.\n"
        "Не ставь диагнозы и не делай медицинских выводов. Сохраняй только то, что поможет "
        "будущему диалогу быть живым, бережным и конкретным.\n\n"
        "Верни только JSON без markdown:\n"
        "{\n"
        '  "profile_summary": "обновленное краткое описание пользователя или null",\n'
        '  "session_summary": "краткий вывод по текущему диалогу или null",\n'
        '  "risk_notes": "важные риски без диагноза или null",\n'
        '  "support_preferences": {"tone": "если пользователь явно показал предпочтение"},\n'
        '  "memories": [\n'
        "    {\n"
        '      "memory_type": "profile|situation|insight|goal|risk|preference|support_strategy",\n'
        '      "title": "короткое название",\n'
        '      "content": "что важно вспомнить позже",\n'
        '      "importance": 1\n'
        "    }\n"
        "  ]\n"
        "}\n\n"
        f"Текущее описание пользователя: {user.profile_summary or 'пока пусто'}\n"
        f"Текущий вывод по сессии: {session.summary or 'пока пусто'}\n\n"
        f"Сообщение пользователя:\n{user_text}\n\n"
        f"Ответ бота:\n{assistant_reply}"
    )

    try:
        raw = await openrouter_chat(
            [{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=650,
        )
        data = extract_json_object(raw)
    except Exception:
        logger.exception("Failed to extract memory updates")
        return

    profile_summary = data.get("profile_summary")
    if isinstance(profile_summary, str) and profile_summary.strip():
        user.profile_summary = profile_summary.strip()[:4000]

    session_summary = data.get("session_summary")
    if isinstance(session_summary, str) and session_summary.strip():
        session.summary = session_summary.strip()[:4000]

    risk_notes = data.get("risk_notes")
    if isinstance(risk_notes, str) and risk_notes.strip():
        user.risk_notes = risk_notes.strip()[:4000]

    support_preferences = data.get("support_preferences")
    if isinstance(support_preferences, dict):
        user.support_preferences = {**(user.support_preferences or {}), **support_preferences}

    memories = data.get("memories")
    if not isinstance(memories, list):
        await db.flush()
        return

    for item in memories[:5]:
        if not isinstance(item, dict):
            continue
        memory_type = str(item.get("memory_type") or "").strip()
        title = str(item.get("title") or "").strip()
        content = str(item.get("content") or "").strip()
        if memory_type not in MEMORY_TYPES or not title or not content:
            continue
        db.add(
            UserMemory(
                user_id=user.id,
                session_id=session.id,
                source_message_id=source_message.id,
                memory_type=memory_type,
                title=title[:240],
                content=content[:3000],
                importance=_normalize_importance(item.get("importance")),
                memory_metadata={},
            )
        )

    await db.flush()
