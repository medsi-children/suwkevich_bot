from __future__ import annotations

import logging
import re
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.memory import ImportantFact, KnownPerson, OpenTopic, UserMemory
from app.models.message import Message
from app.models.session import ConversationSession
from app.models.user import User
from app.services.llm import extract_json_object, openrouter_chat
from app.services.support_profile import cache_support_profile_items

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
FACT_TYPES = {
    "name",
    "age",
    "city",
    "work",
    "study",
    "family",
    "relationship",
    "health",
    "medication",
    "trigger",
    "coping",
    "preference",
    "boundary",
    "important_event",
    "user_note",
}
STYLE_KEYS = {
    "address_form",
    "answer_length",
    "directness",
    "warmth",
    "structure",
    "humor",
    "medical_language",
    "questions",
}
STOPWORDS = {
    "это",
    "как",
    "что",
    "или",
    "если",
    "для",
    "меня",
    "мне",
    "мой",
    "моя",
    "мои",
    "она",
    "они",
    "его",
    "ему",
    "про",
    "при",
    "без",
    "уже",
    "еще",
    "очень",
    "сейчас",
    "потом",
    "когда",
    "почему",
    "котор",
    "the",
    "and",
    "with",
}
WORD_RE = re.compile(r"[a-zA-Zа-яА-ЯёЁ0-9]{3,}")


def _clean_text(value: Any, *, limit: int = 3000) -> str:
    text = str(value or "").strip()
    text = re.sub(r"\s+", " ", text)
    return text[:limit]


def _normalize_score(value: Any, *, default: int = 3) -> int:
    try:
        score = int(value)
    except (TypeError, ValueError):
        return default
    return max(1, min(5, score))


def _keywords(text: str) -> set[str]:
    return {
        word.lower()
        for word in WORD_RE.findall(text or "")
        if word.lower() not in STOPWORDS
    }


def _score_text(text: str, keywords: set[str]) -> int:
    if not keywords:
        return 0
    haystack = (text or "").lower()
    return sum(1 for word in keywords if word in haystack)


def _rank(items: list[Any], keywords: set[str], formatter) -> list[Any]:
    return sorted(
        items,
        key=lambda item: (
            _score_text(formatter(item), keywords),
            int(getattr(item, "importance", 3) or 3),
            getattr(item, "updated_at", None) or getattr(item, "created_at", None),
        ),
        reverse=True,
    )


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


async def get_memory_bundle(
    db: AsyncSession,
    user: User,
    *,
    query_text: str,
) -> dict[str, list[Any]]:
    keywords = _keywords(query_text)

    facts_result = await db.execute(
        select(ImportantFact)
        .where(ImportantFact.user_id == user.id, ImportantFact.is_active.is_(True))
        .order_by(ImportantFact.importance.desc(), ImportantFact.last_mentioned_at.desc())
        .limit(50)
    )
    people_result = await db.execute(
        select(KnownPerson)
        .where(KnownPerson.user_id == user.id, KnownPerson.is_active.is_(True))
        .order_by(KnownPerson.importance.desc(), KnownPerson.last_mentioned_at.desc())
        .limit(40)
    )
    topics_result = await db.execute(
        select(OpenTopic)
        .where(OpenTopic.user_id == user.id, OpenTopic.status == "open")
        .order_by(OpenTopic.priority.desc(), OpenTopic.last_mentioned_at.desc())
        .limit(20)
    )
    memories = await get_relevant_memories(db, user, limit=30)

    facts = _rank(
        list(facts_result.scalars().all()),
        keywords,
        lambda item: f"{item.fact_type} {item.title} {item.value}",
    )[:10]
    people = _rank(
        list(people_result.scalars().all()),
        keywords,
        lambda item: (
            f"{item.name} {item.role or ''} "
            f"{item.relation_summary or ''} {item.emotional_context or ''}"
        ),
    )[:8]
    topics = _rank(
        list(topics_result.scalars().all()),
        keywords,
        lambda item: f"{item.title} {item.summary} {item.next_step or ''}",
    )[:8]
    memories = _rank(
        memories,
        keywords,
        lambda item: f"{item.memory_type} {item.title} {item.content}",
    )[:10]

    now = datetime.now(UTC)
    for memory in memories:
        memory.last_recalled_at = now
    return {"facts": facts, "people": people, "topics": topics, "memories": memories}


def format_memory_context(user: User, bundle_or_memories: dict | list[UserMemory]) -> str:
    parts: list[str] = []
    if user.profile_summary:
        parts.append(f"Краткий профиль пользователя: {user.profile_summary}")
    if user.risk_notes:
        parts.append(f"Важные риски и осторожность: {user.risk_notes}")
    style_preferences = {
        key: value
        for key, value in (user.support_preferences or {}).items()
        if key in STYLE_KEYS
    }
    if style_preferences:
        parts.append(f"Стиль общения и предпочтения: {style_preferences}")

    if isinstance(bundle_or_memories, dict):
        facts = bundle_or_memories.get("facts") or []
        people = bundle_or_memories.get("people") or []
        topics = bundle_or_memories.get("topics") or []
        memories = bundle_or_memories.get("memories") or []
    else:
        facts, people, topics, memories = [], [], [], bundle_or_memories

    if facts:
        lines = [
            f"- {fact.fact_type}: {fact.title} — {fact.value}"
            for fact in facts
            if fact.is_active
        ]
        parts.append("Важные факты:\n" + "\n".join(lines))

    if people:
        lines = []
        for person in people:
            role = f" ({person.role})" if person.role else ""
            summary = person.relation_summary or "важный человек в контексте пользователя"
            emotional = (
                f" Эмоциональный контекст: {person.emotional_context}"
                if person.emotional_context
                else ""
            )
            lines.append(f"- {person.name}{role}: {summary}.{emotional}")
        parts.append("Люди из жизни пользователя:\n" + "\n".join(lines))

    if topics:
        lines = [
            f"- {topic.title}: {topic.summary}"
            + (f" Следующий шаг: {topic.next_step}" if topic.next_step else "")
            for topic in topics
        ]
        parts.append("Открытые темы, к которым можно бережно вернуться:\n" + "\n".join(lines))

    if memories:
        lines = [
            f"- {memory.memory_type}: {memory.title}. {memory.content}"
            for memory in memories
        ]
        parts.append("Общая долговременная память:\n" + "\n".join(lines))

    return "\n\n".join(parts).strip()


def _merge_support_preferences(user: User, preferences: dict[str, Any]) -> None:
    clean: dict[str, str] = {}
    for key, value in preferences.items():
        if key not in STYLE_KEYS:
            continue
        text = _clean_text(value, limit=160)
        if text:
            clean[key] = text
    if clean:
        user.support_preferences = {**(user.support_preferences or {}), **clean}


async def consolidate_user_memory(db: AsyncSession, user: User) -> None:
    result = await db.execute(
        select(UserMemory)
        .where(UserMemory.user_id == user.id)
        .order_by(UserMemory.importance.desc(), UserMemory.updated_at.desc())
        .limit(220)
    )
    memories = list(result.scalars().all())
    seen: set[tuple[str, str]] = set()
    kept = 0

    for memory in memories:
        key = (memory.memory_type, memory.title.strip().lower())
        if key in seen:
            await db.delete(memory)
            continue
        seen.add(key)
        kept += 1
        if kept > 140 and memory.importance <= 3:
            await db.delete(memory)

    topics_result = await db.execute(
        select(OpenTopic)
        .where(OpenTopic.user_id == user.id, OpenTopic.status == "open")
        .order_by(OpenTopic.priority.desc(), OpenTopic.last_mentioned_at.desc())
        .limit(80)
    )
    for index, topic in enumerate(topics_result.scalars().all(), start=1):
        if index > 30 and topic.priority <= 3:
            topic.status = "paused"


async def _upsert_important_fact(
    db: AsyncSession,
    *,
    user: User,
    source_message: Message | None,
    item: dict[str, Any],
) -> None:
    fact_type = _clean_text(item.get("fact_type"), limit=64)
    title = _clean_text(item.get("title"), limit=240)
    value = _clean_text(item.get("value") or item.get("content"), limit=3000)
    if fact_type not in FACT_TYPES or not title or not value:
        return

    existing_result = await db.execute(
        select(ImportantFact)
        .where(
            ImportantFact.user_id == user.id,
            ImportantFact.is_active.is_(True),
            ImportantFact.fact_type == fact_type,
            func.lower(ImportantFact.title) == title.lower(),
        )
        .limit(1)
    )
    fact = existing_result.scalar_one_or_none()
    now = datetime.now(UTC)
    if fact is None:
        db.add(
            ImportantFact(
                user_id=user.id,
                source_message_id=source_message.id if source_message else None,
                fact_type=fact_type,
                title=title,
                value=value,
                confidence=_normalize_score(item.get("confidence")),
                importance=_normalize_score(item.get("importance")),
                sensitivity=_clean_text(item.get("sensitivity"), limit=32) or "normal",
                fact_metadata={},
                first_mentioned_at=now,
                last_mentioned_at=now,
            )
        )
        return

    fact.value = value
    fact.confidence = max(fact.confidence, _normalize_score(item.get("confidence")))
    fact.importance = max(fact.importance, _normalize_score(item.get("importance")))
    fact.sensitivity = _clean_text(item.get("sensitivity"), limit=32) or fact.sensitivity
    fact.last_mentioned_at = now


async def _upsert_known_person(
    db: AsyncSession,
    *,
    user: User,
    source_message: Message | None,
    item: dict[str, Any],
) -> None:
    name = _clean_text(item.get("name"), limit=160)
    if not name:
        return
    existing_result = await db.execute(
        select(KnownPerson)
        .where(
            KnownPerson.user_id == user.id,
            KnownPerson.is_active.is_(True),
            func.lower(KnownPerson.name) == name.lower(),
        )
        .limit(1)
    )
    person = existing_result.scalar_one_or_none()
    role = _clean_text(item.get("role"), limit=120) or None
    relation_summary = _clean_text(item.get("relation_summary"), limit=3000) or None
    emotional_context = _clean_text(item.get("emotional_context"), limit=3000) or None
    now = datetime.now(UTC)
    if person is None:
        db.add(
            KnownPerson(
                user_id=user.id,
                source_message_id=source_message.id if source_message else None,
                name=name,
                role=role,
                relation_summary=relation_summary,
                emotional_context=emotional_context,
                importance=_normalize_score(item.get("importance")),
                person_metadata={},
                first_mentioned_at=now,
                last_mentioned_at=now,
            )
        )
        return

    person.role = role or person.role
    person.relation_summary = relation_summary or person.relation_summary
    person.emotional_context = emotional_context or person.emotional_context
    person.importance = max(person.importance, _normalize_score(item.get("importance")))
    person.last_mentioned_at = now


async def _upsert_open_topic(
    db: AsyncSession,
    *,
    user: User,
    session: ConversationSession,
    source_message: Message | None,
    item: dict[str, Any],
) -> None:
    title = _clean_text(item.get("title"), limit=240)
    summary = _clean_text(item.get("summary"), limit=3000)
    if not title or not summary:
        return
    existing_result = await db.execute(
        select(OpenTopic)
        .where(
            OpenTopic.user_id == user.id,
            OpenTopic.status == "open",
            func.lower(OpenTopic.title) == title.lower(),
        )
        .limit(1)
    )
    topic = existing_result.scalar_one_or_none()
    now = datetime.now(UTC)
    if topic is None:
        db.add(
            OpenTopic(
                user_id=user.id,
                session_id=session.id,
                source_message_id=source_message.id if source_message else None,
                title=title,
                summary=summary,
                status=_clean_text(item.get("status"), limit=32) or "open",
                priority=_normalize_score(item.get("priority")),
                next_step=_clean_text(item.get("next_step"), limit=2000) or None,
                topic_metadata={},
                last_mentioned_at=now,
            )
        )
        return

    topic.summary = summary
    topic.priority = max(topic.priority, _normalize_score(item.get("priority")))
    topic.next_step = _clean_text(item.get("next_step"), limit=2000) or topic.next_step
    topic.last_mentioned_at = now


async def _store_general_memory(
    db: AsyncSession,
    *,
    user: User,
    session: ConversationSession,
    source_message: Message,
    item: dict[str, Any],
) -> None:
    memory_type = _clean_text(item.get("memory_type"), limit=64)
    title = _clean_text(item.get("title"), limit=240)
    content = _clean_text(item.get("content"), limit=3000)
    if memory_type not in MEMORY_TYPES or not title or not content:
        return
    db.add(
        UserMemory(
            user_id=user.id,
            session_id=session.id,
            source_message_id=source_message.id,
            memory_type=memory_type,
            title=title,
            content=content,
            importance=_normalize_score(item.get("importance")),
            memory_metadata={},
        )
    )


async def apply_memory_control(
    db: AsyncSession,
    *,
    user: User,
    session: ConversationSession,
    source_message: Message,
    text: str,
) -> str | None:
    clean = text.strip()
    lower = clean.lower()

    style_updates: dict[str, str] = {}
    if any(phrase in lower for phrase in ("говори на ты", "давай на ты", "обращайся на ты")):
        style_updates["address_form"] = "ты"
    if any(phrase in lower for phrase in ("говорите на вы", "давай на вы", "обращайся на вы")):
        style_updates["address_form"] = "вы"
    if any(phrase in lower for phrase in ("говори короче", "пиши короче", "ответы короче")):
        style_updates["answer_length"] = "short"
    if any(phrase in lower for phrase in ("отвечай подробнее", "пиши подробнее", "больше деталей")):
        style_updates["answer_length"] = "detailed"
    if any(phrase in lower for phrase in ("будь мягче", "помягче", "бережнее")):
        style_updates["directness"] = "gentle"
        style_updates["warmth"] = "high"
    if any(phrase in lower for phrase in ("будь прямее", "говори прямо", "без сюсюканья")):
        style_updates["directness"] = "direct"
    if any(phrase in lower for phrase in ("без списков", "не списком")):
        style_updates["structure"] = "prose"
    if any(phrase in lower for phrase in ("по шагам", "структурно", "списком")):
        style_updates["structure"] = "steps"

    remember_match = re.match(r"(?is)^\s*(запомни|запиши|сохрани)\s*[:,\-]?\s*(.+)$", clean)
    if remember_match:
        content = _clean_text(remember_match.group(2), limit=3000)
        await _upsert_important_fact(
            db,
            user=user,
            source_message=source_message,
            item={
                "fact_type": "user_note",
                "title": content[:80],
                "value": content,
                "importance": 5,
                "confidence": 5,
            },
        )
        await db.flush()
        return "Запомнил. Буду учитывать это в следующих ответах."

    if re.match(r"(?is)^\s*(не запоминай|не сохраняй)\b", clean):
        return "Хорошо, не буду сохранять это в долговременную память."

    forget_match = re.match(r"(?is)^\s*(забудь|удали из памяти|не помни)\s*[:,\-]?\s*(.+)$", clean)
    if forget_match:
        needle = _clean_text(forget_match.group(2), limit=240).lower()
        if needle:
            facts_result = await db.execute(
                select(ImportantFact)
                .where(ImportantFact.user_id == user.id, ImportantFact.is_active.is_(True))
                .limit(100)
            )
            people_result = await db.execute(
                select(KnownPerson)
                .where(KnownPerson.user_id == user.id, KnownPerson.is_active.is_(True))
                .limit(100)
            )
            memories_result = await db.execute(
                select(UserMemory)
                .where(UserMemory.user_id == user.id)
                .limit(150)
            )
            topics_result = await db.execute(
                select(OpenTopic)
                .where(OpenTopic.user_id == user.id, OpenTopic.status == "open")
                .limit(80)
            )
            changed = 0
            for fact in facts_result.scalars().all():
                if needle in fact.title.lower() or needle in fact.value.lower():
                    fact.is_active = False
                    changed += 1
            for person in people_result.scalars().all():
                fields = " ".join(
                    [
                        person.name,
                        person.role or "",
                        person.relation_summary or "",
                        person.emotional_context or "",
                    ]
                ).lower()
                if needle in fields:
                    person.is_active = False
                    changed += 1
            for memory in memories_result.scalars().all():
                fields = f"{memory.title} {memory.content}".lower()
                if needle in fields:
                    await db.delete(memory)
                    changed += 1
            for topic in topics_result.scalars().all():
                fields = f"{topic.title} {topic.summary} {topic.next_step or ''}".lower()
                if needle in fields:
                    topic.status = "paused"
                    changed += 1
            await db.flush()
            if changed:
                return "Хорошо, убрал это из активной памяти."
        return "Я не нашел такого факта в активной памяти, но дальше не буду на этом настаивать."

    if style_updates:
        _merge_support_preferences(user, style_updates)
        await db.flush()
        return "Хорошо, подстроюсь под этот стиль общения."

    return None


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
        "Особенно важно сохранять: имя пользователя, важные факты биографии, работу, "
        "отношения, имена значимых людей, повторяющиеся триггеры, способы самопомощи, "
        "цели, открытые темы, выводы пользователя и явные просьбы о стиле общения.\n\n"
        "Верни только JSON без markdown:\n"
        "{\n"
        '  "profile_summary": "обновленное краткое описание пользователя или null",\n'
        '  "session_summary": "краткий вывод по текущему диалогу или null",\n'
        '  "risk_notes": "важные риски без диагноза или null",\n'
        '  "support_preferences": {\n'
        '    "address_form": "ты|вы|null",\n'
        '    "answer_length": "short|medium|detailed|null",\n'
        '    "directness": "gentle|balanced|direct|null",\n'
        '    "warmth": "low|medium|high|null",\n'
        '    "structure": "prose|steps|mixed|null",\n'
        '    "humor": "none|light|null",\n'
        '    "medical_language": "simple|professional|null",\n'
        '    "questions": "few|normal|more|null"\n'
        "  },\n"
        '  "important_facts": [\n'
        "    {\n"
        '      "fact_type": "name|age|city|work|study|family|relationship|health|'
        'medication|trigger|coping|preference|boundary|important_event|user_note",\n'
        '      "title": "короткое название",\n'
        '      "value": "сам факт",\n'
        '      "importance": 1,\n'
        '      "confidence": 1,\n'
        '      "sensitivity": "normal|sensitive|private"\n'
        "    }\n"
        "  ],\n"
        '  "people": [\n'
        "    {\n"
        '      "name": "имя человека",\n'
        '      "role": "девушка|партнер|мама|друг|коллега|врач|...",\n'
        '      "relation_summary": "кто это для пользователя",\n'
        '      "emotional_context": "какие чувства/конфликт связаны с человеком",\n'
        '      "importance": 1\n'
        "    }\n"
        "  ],\n"
        '  "open_topics": [\n'
        "    {\n"
        '      "title": "тема, к которой стоит вернуться",\n'
        '      "summary": "что осталось важным или незавершенным",\n'
        '      "priority": 1,\n'
        '      "next_step": "что мягко спросить или проверить позже",\n'
        '      "status": "open"\n'
        "    }\n"
        "  ],\n"
        '  "memories": [\n'
        "    {\n"
        '      "memory_type": "profile|situation|insight|goal|risk|preference|support_strategy",\n'
        '      "title": "короткое название",\n'
        '      "content": "что важно вспомнить позже",\n'
        '      "importance": 1\n'
        "    }\n"
        "  ],\n"
        '  "miniapp_lifehacks": [\n'
        '    {"title": "до 5 слов", "text": "коротко, без общих советов", '
        '"action": "один конкретный шаг"}\n'
        "  ],\n"
        '  "miniapp_insights": [\n'
        '    {"title": "до 6 слов, без совета", '
        '"text": "осознание или динамика пользователя, не рекомендация", '
        '"tone": "growth|attention|resource|calm"}\n'
        "  ]\n"
        "}\n\n"
        "Для miniapp_lifehacks верни ровно 3 коротких персональных пункта только если "
        "контекста достаточно; иначе пустой массив. Эти лайфхаки всегда должны быть про "
        "эмоциональное состояние, саморегуляцию, границы, отдых, разговор или ближайшую "
        "жизненную опору пользователя. Не превращай профессию, роль, хобби или фразу "
        "пользователя в буквальное техническое задание. Даже если пользователь говорит, "
        "что он разработчик, не предлагай писать код, создавать файлы, открывать IDE, "
        "делать debug, массивы, мемы или комментарии в проекте. Пиши как для человека, "
        "а не как для его работы.\n\n"
        "Для miniapp_insights верни только моменты осознания самого пользователя, "
        "изменения паттернов или динамику состояния, если это прямо видно из сообщений. "
        "Это не вкладка советов: не пиши рекомендации, упражнения, инструкции, вопросы, "
        "следующие шаги или фразы в повелительном наклонении. Не используй формулировки "
        '"попробуйте", "запишите", "спросите себя", "нужно", "стоит", "можно". '
        'Пиши от второго лица и только как наблюдение: "Вы заметили...", '
        '"Вы стали...", "Вы чаще...", "Стало видно...". '
        "Не превращай инсайты в историю сообщений, даты, заметки о фактах или список событий. "
        "Если есть только факт вроде профессии/роли или слишком мало контекста, "
        "верни пустой массив.\n\n"
        f"Текущее описание пользователя: {user.profile_summary or 'пока пусто'}\n"
        f"Текущий стиль общения: {user.support_preferences or {}}\n"
        f"Текущий вывод по сессии: {session.summary or 'пока пусто'}\n\n"
        f"Сообщение пользователя:\n{user_text}\n\n"
        f"Ответ бота:\n{assistant_reply}"
    )

    try:
        raw = await openrouter_chat(
            [{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=1200,
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
        _merge_support_preferences(user, support_preferences)

    cache_support_profile_items(
        user,
        lifehacks=data.get("miniapp_lifehacks"),
        insights=data.get("miniapp_insights"),
    )

    for item in (data.get("important_facts") or [])[:8]:
        if isinstance(item, dict):
            await _upsert_important_fact(
                db,
                user=user,
                source_message=source_message,
                item=item,
            )

    for item in (data.get("people") or [])[:6]:
        if isinstance(item, dict):
            await _upsert_known_person(
                db,
                user=user,
                source_message=source_message,
                item=item,
            )

    for item in (data.get("open_topics") or [])[:5]:
        if isinstance(item, dict):
            await _upsert_open_topic(
                db,
                user=user,
                session=session,
                source_message=source_message,
                item=item,
            )

    for item in (data.get("memories") or [])[:5]:
        if isinstance(item, dict):
            await _store_general_memory(
                db,
                user=user,
                session=session,
                source_message=source_message,
                item=item,
            )

    await consolidate_user_memory(db, user)
    await db.flush()
