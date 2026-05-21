from __future__ import annotations

import logging
from collections import Counter
from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.memory import ImportantFact, KnownPerson, OpenTopic, UserMemory
from app.models.message import Message
from app.models.user import User
from app.services.llm import extract_json_object, openrouter_chat

RECENT_MESSAGE_LIMIT = 120
LIFEHACK_CACHE_KEY = "_support_lifehacks_cache"
logger = logging.getLogger(__name__)

DIMENSIONS = (
    {
        "key": "agency",
        "label": "Субъектность",
        "hint": "Насколько в диалогах видны выбор, границы и следующие шаги",
        "tones": ("#8fd6c8", "#5bb8a9"),
    },
    {
        "key": "clarity",
        "label": "Ясность",
        "hint": "Сколько уже собрано понятных выводов и открытых тем",
        "tones": ("#a9c8ff", "#6f9fed"),
    },
    {
        "key": "support",
        "label": "Опора",
        "hint": "Люди, стратегии и привычки, которые могут поддерживать",
        "tones": ("#ffd6a6", "#f3ad61"),
    },
    {
        "key": "safety",
        "label": "Безопасность",
        "hint": "Ориентир осторожности по последним сообщениям и заметкам о рисках",
        "tones": ("#f5b8c8", "#df7f9a"),
    },
    {
        "key": "boundaries",
        "label": "Границы",
        "hint": "Насколько явно обозначены личные пределы и предпочтения",
        "tones": ("#c9b7ff", "#987de8"),
    },
    {
        "key": "self_compassion",
        "label": "Самосострадание",
        "hint": "Есть ли в профиле мягкие способы говорить с собой",
        "tones": ("#b8e9aa", "#79be68"),
    },
    {
        "key": "body_contact",
        "label": "Контакт с собой",
        "hint": "Упоминания чувств, тела, сна, усталости и состояния",
        "tones": ("#b7e6ff", "#67badc"),
    },
    {
        "key": "resource",
        "label": "Ресурс",
        "hint": "Бережная оценка энергии по последним диалогам",
        "tones": ("#ffe69e", "#e7bc45"),
    },
)

NEGATIVE_RESOURCE_WORDS = (
    "устал",
    "устала",
    "выгор",
    "не могу",
    "нет сил",
    "плохо",
    "тревож",
    "паник",
    "страш",
    "бессон",
    "не сплю",
)

BODY_STATE_WORDS = (
    "тело",
    "сон",
    "сплю",
    "дых",
    "сердц",
    "напряж",
    "устал",
    "чувств",
    "эмоц",
)

AGENCY_WORDS = ("хочу", "могу", "решил", "решила", "выбира", "границ", "план", "шаг")


def _clip(text: str | None, *, limit: int = 220) -> str:
    """Trim and clean text to a maximum length, adding an ellipsis if needed."""
    clean = " ".join((text or "").strip().split())
    if len(clean) <= limit:
        return clean
    return clean[: limit - 1].rstrip() + "…"


def _bounded(value: int) -> int:
    """Restrict a metric value to the 12–92 range."""
    return max(12, min(92, value))


def _contains_any(text: str, words: tuple[str, ...]) -> bool:
    lower = text.lower()
    return any(word in lower for word in words)


def _value_from_counts(base: int, *parts: int) -> int:
    return _bounded(base + sum(parts))


def _latest_dt(items: list[Any]) -> datetime | None:
    moments = [
        value
        for item in items
        for value in (
            getattr(item, "updated_at", None),
            getattr(item, "created_at", None),
            getattr(item, "last_mentioned_at", None),
        )
        if isinstance(value, datetime)
    ]
    return max(moments) if moments else None


def _date_label(value: datetime | None) -> str:
    if value is None:
        return "данных пока мало"
    return value.astimezone(UTC).strftime("%d.%m.%Y")


def _fact_items(facts: list[ImportantFact], *fact_types: str) -> list[ImportantFact]:
    allowed = set(fact_types)
    return [fact for fact in facts if fact.fact_type in allowed]


def _memory_items(memories: list[UserMemory], *memory_types: str) -> list[UserMemory]:
    allowed = set(memory_types)
    return [memory for memory in memories if memory.memory_type in allowed]


def _recent_user_text(messages: list[Message]) -> str:
    return "\n".join(message.content for message in messages if message.role == "user")


def _build_metrics(
    *,
    user: User,
    facts: list[ImportantFact],
    people: list[KnownPerson],
    topics: list[OpenTopic],
    memories: list[UserMemory],
    messages: list[Message],
) -> list[dict[str, Any]]:
    """
    Build a list of dimension metrics based on user data.

    Returns an empty list when there is no meaningful context (no facts,
    people, topics, memories and zero or one message), avoiding random
    baseline scores. This empty state can be detected by the UI to
    display a "no data" message.
    """
    # Early exit when there is insufficient context for meaningful metrics.
    # We require at least one non‑empty facts/topics/memories entry or a small
    # exchange of messages before attempting to compute scores. A single
    # `/start` or greeting from the bot should not generate arbitrary numbers.
    if not facts and not people and not topics and not memories and len(messages) < 3:
        return []

    recent_text = _recent_user_text(messages)
    crisis_like = _contains_any(
        recent_text,
        ("суицид", "самоуб", "не хочу жить", "навредить себе", "психоз", "112", "103"),
    )
    negative_hits = sum(1 for word in NEGATIVE_RESOURCE_WORDS if word in recent_text.lower())

    scores = {
        "agency": _value_from_counts(
            46,
            min(18, len(_fact_items(facts, "boundary", "preference")) * 4),
            min(14, len(_memory_items(memories, "goal", "insight")) * 3),
            8 if _contains_any(recent_text, AGENCY_WORDS) else 0,
        ),
        "clarity": _value_from_counts(
            42,
            10 if user.profile_summary else 0,
            min(20, len(topics) * 4),
            min(16, len(_memory_items(memories, "insight")) * 4),
        ),
        "support": _value_from_counts(
            40,
            min(16, len(people) * 4),
            min(18, len(_fact_items(facts, "coping", "preference")) * 4),
            min(16, len(_memory_items(memories, "support_strategy")) * 5),
        ),
        "safety": _value_from_counts(
            66,
            -24 if user.risk_notes else 0,
            -28 if crisis_like else 0,
            -min(18, negative_hits * 3),
            min(10, len(_fact_items(facts, "coping")) * 2),
        ),
        "boundaries": _value_from_counts(
            38,
            min(26, len(_fact_items(facts, "boundary")) * 7),
            min(12, len(_memory_items(memories, "preference")) * 3),
        ),
        "self_compassion": _value_from_counts(
            44,
            min(20, len(_memory_items(memories, "support_strategy")) * 5),
            min(12, len(_fact_items(facts, "coping")) * 3),
            5
            if any(not key.startswith("_") for key in (user.support_preferences or {}))
            else 0,
        ),
        "body_contact": _value_from_counts(
            40,
            min(
                30,
                sum(
                    1
                    for message in messages
                    if _contains_any(message.content, BODY_STATE_WORDS)
                )
                * 3,
            ),
        ),
        "resource": _value_from_counts(
            60,
            -min(30, negative_hits * 4),
            8 if _fact_items(facts, "coping") else 0,
        ),
    }

    metrics: list[dict[str, Any]] = []
    for index, dimension in enumerate(DIMENSIONS):
        key = dimension["key"]
        metrics.append(
            {
                "key": key,
                "label": dimension["label"],
                "value": scores[key],
                "hint": dimension["hint"],
                "tone": dimension["tones"],
                "order": index,
            }
        )
    return metrics


def _build_focus_cards(topics: list[OpenTopic], memories: list[UserMemory]) -> list[dict[str, str]]:
    cards: list[dict[str, str]] = []
    for topic in topics[:4]:
        cards.append(
            {
                "title": topic.title,
                "text": _clip(topic.summary, limit=260),
                "next_step": _clip(topic.next_step, limit=180)
                or "Можно вернуться к этому в чате и разложить на один ближайший шаг.",
                "source": "открытая тема",
            }
        )
    if len(cards) >= 4:
        return cards

    for memory in _memory_items(memories, "goal", "insight", "situation")[: 4 - len(cards)]:
        cards.append(
            {
                "title": memory.title,
                "text": _clip(memory.content, limit=260),
                "next_step": "Можно обсудить, что из этого сейчас важнее всего.",
                "source": "память диалогов",
            }
        )
    return cards


def _build_support_cards(
    facts: list[ImportantFact],
    memories: list[UserMemory],
    people: list[KnownPerson],
) -> list[dict[str, str]]:
    cards: list[dict[str, str]] = []
    for memory in _memory_items(memories, "support_strategy", "preference")[:4]:
        cards.append(
            {
                "title": memory.title,
                "text": _clip(memory.content, limit=220),
                "kind": "стратегия",
            }
        )
    for fact in _fact_items(facts, "coping", "preference", "boundary")[: 5 - len(cards)]:
        cards.append(
            {
                "title": fact.title,
                "text": _clip(fact.value, limit=220),
                "kind": "важный факт",
            }
        )
    if people and len(cards) < 5:
        names = ", ".join(person.name for person in people[:3])
        cards.append(
            {
                "title": "Люди рядом",
                "text": f"В профиле уже отмечены значимые люди: {names}.",
                "kind": "социальная опора",
            }
        )
    return cards


def _build_attention_cards(
    *,
    user: User,
    facts: list[ImportantFact],
    topics: list[OpenTopic],
) -> list[dict[str, str]]:
    cards: list[dict[str, str]] = []
    if user.risk_notes:
        cards.append(
            {
                "title": "Осторожность",
                "text": _clip(user.risk_notes, limit=240),
                "kind": "бережная заметка",
            }
        )
    for fact in _fact_items(facts, "trigger", "health", "medication")[: 4 - len(cards)]:
        cards.append(
            {
                "title": fact.title,
                "text": _clip(fact.value, limit=240),
                "kind": "на что обратить внимание",
            }
        )
    if topics and len(cards) < 4:
        topic = topics[0]
        cards.append(
            {
                "title": "Повторяющийся фокус",
                "text": _clip(topic.summary, limit=240),
                "kind": "тема для разговора",
            }
        )
    return cards


def _context_signature(
    *,
    user: User,
    facts: list[ImportantFact],
    topics: list[OpenTopic],
    memories: list[UserMemory],
    messages: list[Message],
) -> str:
    latest_update = _latest_dt([*facts, *topics, *memories, *messages])
    return "|".join(
        [
            _clip(user.profile_summary, limit=300),
            _clip(user.risk_notes, limit=160),
            str(latest_update.isoformat() if latest_update else ""),
            str(len(facts)),
            str(len(topics)),
            str(len(memories)),
            str(len(messages)),
        ]
    )


def _lifehack_context(
    *,
    user: User,
    facts: list[ImportantFact],
    topics: list[OpenTopic],
    memories: list[UserMemory],
    messages: list[Message],
) -> str:
    fact_lines = [f"- {fact.title}: {fact.value}" for fact in facts[:8]]
    topic_lines = [
        f"- {topic.title}: {topic.summary}"
        + (f" Следующий шаг: {topic.next_step}" if topic.next_step else "")
        for topic in topics[:6]
    ]
    memory_lines = [
        f"- {memory.memory_type}: {memory.title}. {memory.content}"
        for memory in memories[:8]
    ]
    recent_lines = [
        f"- {message.content}"
        for message in messages
        if message.role == "user"
    ][-8:]

    parts = [
        f"Имя: {user.first_name or 'не указано'}",
        f"Описание профиля: {user.profile_summary or 'пока пусто'}",
        f"Заметки о рисках: {user.risk_notes or 'нет'}",
    ]
    if fact_lines:
        parts.append("Важные факты:\n" + "\n".join(fact_lines))
    if topic_lines:
        parts.append("Открытые темы:\n" + "\n".join(topic_lines))
    if memory_lines:
        parts.append("Память:\n" + "\n".join(memory_lines))
    if recent_lines:
        parts.append("Последние сообщения пользователя:\n" + "\n".join(recent_lines))
    return "\n\n".join(parts)


def _clean_lifehacks(items: Any) -> list[dict[str, str]]:
    if not isinstance(items, list):
        return []
    cards: list[dict[str, str]] = []
    for item in items[:3]:
        if not isinstance(item, dict):
            continue
        title = _clip(item.get("title"), limit=80)
        text = _clip(item.get("text") or item.get("description"), limit=260)
        action = _clip(item.get("action") or item.get("next_step"), limit=220)
        kind = _clip(item.get("kind"), limit=80) or "персональный лайфхак"
        if title and text:
            cards.append(
                {
                    "title": title,
                    "text": text,
                    "next_step": action,
                    "kind": kind,
                }
            )
    return cards


def _fallback_lifehacks(
    facts: list[ImportantFact],
    topics: list[OpenTopic],
    memories: list[UserMemory],
) -> list[dict[str, str]]:
    topic = topics[0] if topics else None
    coping = _fact_items(facts, "coping", "preference", "boundary")
    insight = _memory_items(memories, "insight", "support_strategy", "goal")
    cards = [
        {
            # Encourage a small, doable step instead of a generic plan.
            "title": topic.title if topic else "Небольшой шаг",
            "text": (
                _clip(topic.summary, limit=240)
                if topic
                else "Подумайте, какое короткое действие (5–10 минут) может помочь снизить напряжение."
            ),
            "next_step": (
                _clip(topic.next_step, limit=200)
                if topic and topic.next_step
                else "Спросите себя: что я могу сделать прямо сейчас ради себя?"
            ),
            "kind": "фокус",
        },
        {
            # A simple grounding exercise when there are no coping facts.
            "title": coping[0].title if coping else "Быстрое заземление",
            "text": (
                _clip(coping[0].value, limit=240)
                if coping
                else "Осмотритесь и вслух назовите пять предметов вокруг, затем сделайте глубокий вдох и медленный выдох."
            ),
            "next_step": "Повторите это три раза, отмечая, как меняется ваше самочувствие.",
            "kind": "упражнение",
        },
        {
            # Invite the user to check their thoughts gently.
            "title": insight[0].title if insight else "Проверка мысли",
            "text": (
                _clip(insight[0].content, limit=240)
                if insight
                else "Попробуйте отделить факты от интерпретации: что произошло на самом деле, а что вы додумываете?"
            ),
            "next_step": "Запишите одну более нейтральную формулировку происходящего.",
            "kind": "идея",
        },
    ]
    return cards


async def _build_lifehacks(
    *,
    user: User,
    facts: list[ImportantFact],
    topics: list[OpenTopic],
    memories: list[UserMemory],
    messages: list[Message],
) -> list[dict[str, str]]:
    """
    Assemble up to three lifehack cards for the mini‑app.

    When there is no context (no facts, topics, memories and not enough
    messages), an empty list is returned. Otherwise, cached or generated
    lifehacks are used, falling back to generic suggestions when the
    generation fails. Generated cards are cached using a signature of the
    context to avoid unnecessary repeated calls.
    """
    # Early exit when user context is essentially empty. We require at least
    # one meaningful item (fact, topic, memory) or more than one message to
    # attempt generating lifehacks. Without this, fallback suggestions
    # would feel generic and unhelpful.
    # Consider the conversation too shallow for helpful advice if there are no
    # facts, topics or memories and fewer than three messages. This avoids
    # showing generic lifehacks immediately after a `/start` command.
    if not facts and not topics and not memories and len(messages) < 3:
        return []

    signature = _context_signature(
        user=user,
        facts=facts,
        topics=topics,
        memories=memories,
        messages=messages,
    )
    preferences = user.support_preferences or {}
    cache = preferences.get(LIFEHACK_CACHE_KEY)
    if isinstance(cache, dict) and cache.get("signature") == signature:
        cached_cards = _clean_lifehacks(cache.get("items"))
        if len(cached_cards) == 3:
            return cached_cards

    cards = _fallback_lifehacks(facts, topics, memories)
    if settings.openrouter_api_key:
        prompt = (
            "Ты создаешь три персональных лайфхака для mini-app психологической поддержки.\n"
            "Опирайся только на профиль и контекст пользователя. Не ставь диагнозы, не "
            "назначай лечение, не давай рискованных медицинских инструкций. Каждый лайфхак "
            "должен быть конкретным, мягким, выполнимым за 2-10 минут и связанным с темами "
            "пользователя.\n\n"
            "Верни только JSON без markdown:\n"
            "{\n"
            '  "lifehacks": [\n'
            '    {"title": "коротко", "kind": "идея|упражнение|фокус", '
            '"text": "смысл лайфхака", "action": "точный первый шаг"}\n'
            "  ]\n"
            "}\n\n"
            "Контекст пользователя:\n"
            + _lifehack_context(
                user=user,
                facts=facts,
                topics=topics,
                memories=memories,
                messages=messages,
            )
        )
        try:
            raw = await openrouter_chat(
                [{"role": "user", "content": prompt}],
                temperature=0.45,
                max_tokens=900,
            )
            generated_cards = _clean_lifehacks(extract_json_object(raw).get("lifehacks"))
            if len(generated_cards) == 3:
                cards = generated_cards
        except Exception:
            logger.exception("Failed to generate support lifehacks")

    user.support_preferences = {
        **preferences,
        LIFEHACK_CACHE_KEY: {
            "signature": signature,
            "items": cards,
            "generated_at": datetime.now(UTC).isoformat(),
        },
    }
    return cards


def _build_insights(memories: list[UserMemory], facts: list[ImportantFact]) -> list[dict[str, str]]:
    insights: list[dict[str, str]] = []
    for memory in _memory_items(memories, "insight", "goal", "profile")[:6]:
        insights.append(
            {
                "title": memory.title,
                "text": _clip(memory.content, limit=260),
                "date": _date_label(memory.updated_at or memory.created_at),
            }
        )
    if len(insights) >= 6:
        return insights
    for fact in _fact_items(facts, "important_event", "user_note")[: 6 - len(insights)]:
        insights.append(
            {
                "title": fact.title,
                "text": _clip(fact.value, limit=260),
                "date": _date_label(fact.updated_at or fact.created_at),
            }
        )
    return insights


def _build_activity(messages: list[Message]) -> list[dict[str, Any]]:
    today = datetime.now(UTC).date()
    days = [(today - timedelta(days=offset)) for offset in range(6, -1, -1)]
    counts = Counter(
        message.created_at.astimezone(UTC).date()
        for message in messages
        if isinstance(message.created_at, datetime)
    )
    max_count = max([counts[day] for day in days] + [1])
    return [
        {
            "label": day.strftime("%d.%m"),
            "count": counts[day],
            "value": round(counts[day] / max_count * 100),
        }
        for day in days
    ]


def _empty_focus_cards() -> list[dict[str, str]]:
    return [
        {
            "title": "Начать с текущего состояния",
            "text": "Пока данных немного. Можно написать в чат, что сейчас тяжелее всего.",
            "next_step": "Описать состояние одной фразой: тревожно, пусто, злюсь, устал.",
            "source": "стартовая подсказка",
        },
        {
            "title": "Отделить факты от чувств",
            "text": "Когда внутри шумно, полезно сначала назвать событие и эмоцию отдельно.",
            "next_step": "Попробовать формулу: произошло X, я чувствую Y, мне нужно Z.",
            "source": "бережная практика",
        },
    ]


def _empty_support_cards() -> list[dict[str, str]]:
    return [
        {
            "title": "Короткое заземление",
            "text": "Назовите 5 предметов вокруг, сделайте длинный выдох и проверьте опору стоп.",
            "kind": "быстрая практика",
        },
        {
            "title": "Один ближайший шаг",
            "text": "Выберите действие на 5 минут, которое чуть уменьшит напряжение прямо сейчас.",
            "kind": "микроплан",
        },
    ]


async def build_support_profile(db: AsyncSession, user: User) -> dict[str, Any]:
    facts_result = await db.execute(
        select(ImportantFact)
        .where(ImportantFact.user_id == user.id, ImportantFact.is_active.is_(True))
        .order_by(ImportantFact.importance.desc(), ImportantFact.last_mentioned_at.desc())
        .limit(80)
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
        .limit(30)
    )
    memories_result = await db.execute(
        select(UserMemory)
        .where(UserMemory.user_id == user.id)
        .order_by(UserMemory.importance.desc(), UserMemory.updated_at.desc())
        .limit(80)
    )
    messages_result = await db.execute(
        select(Message)
        .where(Message.user_id == user.id)
        .order_by(Message.created_at.desc())
        .limit(RECENT_MESSAGE_LIMIT)
    )
    facts = list(facts_result.scalars().all())
    people = list(people_result.scalars().all())
    topics = list(topics_result.scalars().all())
    memories = list(memories_result.scalars().all())
    messages = list(reversed(messages_result.scalars().all()))

    focus_cards = _build_focus_cards(topics, memories) or _empty_focus_cards()
    support_cards = _build_support_cards(facts, memories, people) or _empty_support_cards()
    lifehack_cards = await _build_lifehacks(
        user=user,
        facts=facts,
        topics=topics,
        memories=memories,
        messages=messages,
    )
    attention_cards = _build_attention_cards(user=user, facts=facts, topics=topics)
    insights = _build_insights(memories, facts)
    latest_update = _latest_dt([*facts, *people, *topics, *memories, *messages])

    return {
        "user": {
            "id": str(user.id),
            "telegram_id": user.telegram_id,
            "first_name": user.first_name,
            "username": user.username,
            "profile_summary": _clip(
                user.profile_summary,
                limit=540,
            )
            or (
                "Пока профиль знает о вас немного. Он будет становиться точнее по мере "
                "диалогов с ботом и сохраненных вами наблюдений."
            ),
            "support_preferences": {
                key: value
                for key, value in (user.support_preferences or {}).items()
                if not key.startswith("_")
            },
            "last_seen_at": user.last_seen_at.isoformat() if user.last_seen_at else None,
        },
        "metrics": _build_metrics(
            user=user,
            facts=facts,
            people=people,
            topics=topics,
            memories=memories,
            messages=messages,
        ),
        "summary": {
            "latest_update": _date_label(latest_update),
            "memory_count": len(memories) + len(facts),
            "open_topics_count": len(topics),
            "support_items_count": len(support_cards),
            "messages_count": len(messages),
        },
        "activity": _build_activity(messages),
        "lifehack_cards": lifehack_cards,
        "focus_cards": focus_cards,
        "support_cards": support_cards,
        "attention_cards": attention_cards,
        "insights": insights,
        "disclaimer": (
            "Перед вами карта вашей личности, на основе анализа Сушкевич Бота. "
            "Она будет становится точнее и точнее с каждым разговором с вами."
        ),
    }
