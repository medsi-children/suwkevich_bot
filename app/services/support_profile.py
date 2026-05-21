from __future__ import annotations

from collections import Counter
from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.memory import ImportantFact, KnownPerson, OpenTopic, UserMemory
from app.models.message import Message
from app.models.user import User

RECENT_MESSAGE_LIMIT = 120

DIMENSIONS = (
    {
        "key": "agency",
        "label": "Субъектность",
        "hint": "насколько в диалогах видны выбор, границы и следующие шаги",
        "tones": ("#8fd6c8", "#5bb8a9"),
    },
    {
        "key": "clarity",
        "label": "Ясность",
        "hint": "сколько уже собрано понятных выводов и открытых тем",
        "tones": ("#a9c8ff", "#6f9fed"),
    },
    {
        "key": "support",
        "label": "Опора",
        "hint": "люди, стратегии и привычки, которые могут поддерживать",
        "tones": ("#ffd6a6", "#f3ad61"),
    },
    {
        "key": "safety",
        "label": "Безопасность",
        "hint": "ориентир осторожности по последним сообщениям и заметкам о рисках",
        "tones": ("#f5b8c8", "#df7f9a"),
    },
    {
        "key": "boundaries",
        "label": "Границы",
        "hint": "насколько явно обозначены личные пределы и предпочтения",
        "tones": ("#c9b7ff", "#987de8"),
    },
    {
        "key": "self_compassion",
        "label": "Самосострадание",
        "hint": "есть ли в карте мягкие способы говорить с собой",
        "tones": ("#b8e9aa", "#79be68"),
    },
    {
        "key": "body_contact",
        "label": "Контакт с собой",
        "hint": "упоминания чувств, тела, сна, усталости и состояния",
        "tones": ("#b7e6ff", "#67badc"),
    },
    {
        "key": "resource",
        "label": "Ресурс",
        "hint": "бережная оценка энергии по последним диалогам",
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
    clean = " ".join((text or "").strip().split())
    if len(clean) <= limit:
        return clean
    return clean[: limit - 1].rstrip() + "…"


def _bounded(value: int) -> int:
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
            5 if user.support_preferences else 0,
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

    metrics = []
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
                "text": f"В карте уже отмечены значимые люди: {names}.",
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
                "Пока карта знает о вас немного. Она будет становиться точнее по мере "
                "диалогов с ботом и сохраненных вами наблюдений."
            ),
            "support_preferences": user.support_preferences or {},
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
        "focus_cards": focus_cards,
        "support_cards": support_cards,
        "attention_cards": attention_cards,
        "insights": insights,
        "disclaimer": (
            "Это не диагноз и не оценка личности, а ориентировочная карта по сохраненным "
            "диалогам. Ее стоит использовать как повод для бережного разговора."
        ),
    }
