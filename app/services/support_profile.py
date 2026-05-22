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
LIFEHACK_CACHE_KEY = "_support_lifehacks_cache"
INSIGHT_CACHE_KEY = "_support_insights_cache"
SUPPORT_PROFILE_CACHE_VERSION = 2
LOW_CONTEXT_HINT = "Информации о вас пока мало"
LOW_CONTEXT_TONE = ("#eef2f6", "#aeb8c4")

DIMENSIONS = (
    {
        "key": "agency",
        "label": "Субъектность",
        "hint": (
            "Насколько вы защищаете свои границы и отстаиваете себя. "
            "Низкое значение часто означает привычку уступать "
            "и жить по чужим решениям."
        ),
        "tones": ("#8fd6c8", "#5bb8a9"),
    },
    {
        "key": "empathy",
        "label": "Эмпатия",
        "hint": (
            "Насколько вы замечаете чувства других людей "
            "и понимаете, как ваши слова и поступки на них влияют."
        ),
        "tones": ("#ffd6a6", "#f3ad61"),
    },
    {
        "key": "boundaries",
        "label": "Границы",
        "hint": (
            "Насколько вы умеете говорить «нет», обозначать свои пределы "
            "и не брать на себя лишнее."
        ),
        "tones": ("#c9b7ff", "#987de8"),
    },
    {
        "key": "sensitivity",
        "label": "Чувствительность",
        "hint": (
            "Насколько вы замечаете сигналы своего тела и эмоций: "
            "усталость, напряжение, тревогу, перегруз, спокойствие."
        ),
        "tones": ("#b7e6ff", "#67badc"),
    },
    {
        "key": "clarity",
        "label": "Ясность",
        "hint": (
            "Насколько вы способны честно видеть свою роль в ситуации, "
            "признавать ошибки и отделять факты от обиды или фантазий."
        ),
        "tones": ("#a9c8ff", "#6f9fed"),
    },
    {
        "key": "rationality",
        "label": "Рациональность",
        "hint": (
            "Насколько для вас важны проверка, доказательства и факты, "
            "а не вера на слово, магическое объяснение или чужая уверенность."
        ),
        "tones": ("#f5b8c8", "#df7f9a"),
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
BOUNDARY_WORDS = ("границ", "не хочу", "не готов", "нельзя", "мне важно", "отказ")
EMPATHY_WORDS = ("чувств", "пережива", "обид", "поддерж", "другому", "ему", "ей", "людям")
CLARITY_WORDS = ("ошиб", "призн", "объектив", "по факту", "ясно", "понима", "моя роль")
RATIONALITY_WORDS = ("доказ", "факт", "провер", "реальн", "логич", "правда", "аргумент")
MAGICAL_THINKING_WORDS = (
    "эзотер",
    "астрол",
    "таро",
    "энергии",
    "знаки вселенной",
    "сглаз",
    "порча",
    "ретроград",
    "чакр",
    "магич",
)
LIFEHACK_FORBIDDEN_WORDS = (
    "ide",
    "debug",
    "javascript",
    "typescript",
    "python",
    "эмодзи",
    "мем",
    "комментарий",
    "код",
    "массив",
    "редактор",
    "репозитор",
    "проект",
    "файл",
    "заметк",
    "приложени",
    "внутренний голос",
    "скажи себе",
    "громко",
    "аффирма",
    "мантр",
    "цитат",
)
INSIGHT_ADVICE_WORDS = (
    "попробуй",
    "попробуйте",
    "сделай",
    "сделайте",
    "запиши",
    "запишите",
    "спроси",
    "спросите",
    "поставь",
    "поставьте",
    "открой",
    "откройте",
    "закрой",
    "закройте",
    "выбери",
    "выберите",
    "возьми",
    "возьмите",
    "сформулируй",
    "сформулируйте",
    "стоит ",
    "нужно ",
    "лучше ",
    "можно ",
    "важно ",
)
INSIGHT_REALIZATION_WORDS = (
    "вы заметили",
    "вы поняли",
    "вы осознали",
    "вы стали",
    "вы начали",
    "вы чаще",
    "вы меньше",
    "вы больше",
    "появилось понимание",
    "стало видно",
    "становится видно",
    "прослеживается",
    "повторяется",
)


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


def _has_enough_context(
    *,
    facts: list[ImportantFact],
    topics: list[OpenTopic],
    memories: list[UserMemory],
    messages: list[Message],
    people: list[KnownPerson] | None = None,
) -> bool:
    return bool(facts or people or topics or memories) or len(messages) >= 5


def _placeholder_metrics() -> list[dict[str, Any]]:
    return [
        {
            "key": dimension["key"],
            "label": dimension["label"],
            "value": None,
            "hint": LOW_CONTEXT_HINT,
            "tone": LOW_CONTEXT_TONE,
            "order": index,
            "empty": True,
        }
        for index, dimension in enumerate(DIMENSIONS)
    ]


def _placeholder_metric(dimension: dict[str, Any], index: int) -> dict[str, Any]:
    return {
        "key": dimension["key"],
        "label": dimension["label"],
        "value": None,
        "hint": LOW_CONTEXT_HINT,
        "tone": LOW_CONTEXT_TONE,
        "order": index,
        "empty": True,
    }


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


def _parse_cached_datetime(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def _cache_is_fresh(cache: Any, latest_update: datetime | None) -> bool:
    if not isinstance(cache, dict):
        return False
    if cache.get("version") != SUPPORT_PROFILE_CACHE_VERSION:
        return False
    generated_at = _parse_cached_datetime(cache.get("generated_at"))
    if latest_update is None:
        return generated_at is not None
    if generated_at is None:
        return False
    return generated_at >= latest_update.astimezone(UTC) - timedelta(seconds=10)


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
    if not _has_enough_context(
        facts=facts,
        people=people,
        topics=topics,
        memories=memories,
        messages=messages,
    ):
        return _placeholder_metrics()

    recent_text = _recent_user_text(messages)
    lower_text = recent_text.lower()
    negative_hits = sum(1 for word in NEGATIVE_RESOURCE_WORDS if word in lower_text)
    body_mentions = sum(
        1 for message in messages if _contains_any(message.content, BODY_STATE_WORDS)
    )
    empathy_hits = sum(1 for word in EMPATHY_WORDS if word in lower_text)
    clarity_hits = sum(1 for word in CLARITY_WORDS if word in lower_text)
    rationality_hits = sum(1 for word in RATIONALITY_WORDS if word in lower_text)
    magical_hits = sum(1 for word in MAGICAL_THINKING_WORDS if word in lower_text)

    boundary_facts = _fact_items(facts, "boundary")
    preference_facts = _fact_items(facts, "preference")
    insight_memories = _memory_items(memories, "insight")
    goal_memories = _memory_items(memories, "goal")
    preference_memories = _memory_items(memories, "preference")

    evidence = {
        "agency": bool(boundary_facts or preference_facts or goal_memories)
        or _contains_any(recent_text, AGENCY_WORDS),
        "empathy": bool(people or insight_memories or empathy_hits),
        "boundaries": bool(boundary_facts or preference_memories)
        or _contains_any(recent_text, BOUNDARY_WORDS),
        "sensitivity": bool(body_mentions),
        "clarity": bool(user.profile_summary or topics or insight_memories or clarity_hits),
        "rationality": bool(rationality_hits or magical_hits),
    }

    scores = {
        "agency": _value_from_counts(
            46,
            min(18, len([*boundary_facts, *preference_facts]) * 4),
            min(14, len([*goal_memories, *insight_memories]) * 3),
            8 if _contains_any(recent_text, AGENCY_WORDS) else 0,
        ),
        "empathy": _value_from_counts(
            42,
            min(18, len(people) * 4),
            min(16, len(insight_memories) * 4),
            min(12, empathy_hits * 3),
        ),
        "boundaries": _value_from_counts(
            38,
            min(26, len(boundary_facts) * 7),
            min(12, len(preference_memories) * 3),
            6 if _contains_any(recent_text, BOUNDARY_WORDS) else 0,
        ),
        "sensitivity": _value_from_counts(
            40,
            min(30, body_mentions * 3),
            -min(10, negative_hits * 2),
        ),
        "clarity": _value_from_counts(
            42,
            10 if user.profile_summary else 0,
            min(20, len(topics) * 4),
            min(16, len(insight_memories) * 4),
            min(10, clarity_hits * 2),
        ),
        "rationality": _value_from_counts(
            54,
            min(18, rationality_hits * 4),
            -min(24, magical_hits * 6),
        ),
    }

    metrics: list[dict[str, Any]] = []
    for index, dimension in enumerate(DIMENSIONS):
        key = dimension["key"]
        if not evidence[key]:
            metrics.append(_placeholder_metric(dimension, index))
            continue
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


def _clean_lifehacks(items: Any) -> list[dict[str, str]]:
    if not isinstance(items, list):
        return []
    cards: list[dict[str, str]] = []
    for item in items[:3]:
        if not isinstance(item, dict):
            continue
        title = _clip(item.get("title"), limit=64)
        text = _clip(item.get("text") or item.get("description"), limit=145)
        action = _clip(item.get("action") or item.get("next_step"), limit=110)
        combined = f"{title} {text} {action}".lower()
        if any(word in combined for word in LIFEHACK_FORBIDDEN_WORDS):
            continue
        if title and text:
            card: dict[str, str] = {
                "title": title,
                "text": text,
                "next_step": action,
            }
            cards.append(card)
    return cards


def _clean_insights(items: Any) -> list[dict[str, str]]:
    if not isinstance(items, list):
        return []
    allowed_tones = {"growth", "attention", "resource", "calm"}
    insights: list[dict[str, str]] = []
    for item in items[:5]:
        if not isinstance(item, dict):
            continue
        title = _clip(item.get("title"), limit=78)
        text = _clip(item.get("text") or item.get("description"), limit=210)
        tone = str(item.get("tone") or "calm").strip().lower()
        combined = f"{title} {text}".lower()
        if any(word in combined for word in LIFEHACK_FORBIDDEN_WORDS):
            continue
        if any(word in combined for word in INSIGHT_ADVICE_WORDS):
            continue
        if not any(word in combined for word in INSIGHT_REALIZATION_WORDS):
            continue
        if tone not in allowed_tones:
            tone = "calm"
        if title and text:
            insights.append({"title": title, "text": text, "tone": tone})
    return insights


def cache_support_profile_items(
    user: User,
    *,
    lifehacks: Any,
    insights: Any,
) -> None:
    cards = _clean_lifehacks(lifehacks)
    insight_cards = _clean_insights(insights)
    if not cards and not insight_cards:
        return

    preferences = user.support_preferences or {}
    updated_preferences = {**preferences}
    generated_at = datetime.now(UTC).isoformat()
    if len(cards) == 3:
        updated_preferences[LIFEHACK_CACHE_KEY] = {
            "version": SUPPORT_PROFILE_CACHE_VERSION,
            "items": cards,
            "generated_at": generated_at,
        }
    if insight_cards:
        updated_preferences[INSIGHT_CACHE_KEY] = {
            "version": SUPPORT_PROFILE_CACHE_VERSION,
            "items": insight_cards,
            "generated_at": generated_at,
        }
    user.support_preferences = updated_preferences


def _build_lifehacks(user: User, latest_update: datetime | None) -> list[dict[str, str]]:
    cache = (user.support_preferences or {}).get(LIFEHACK_CACHE_KEY)
    if not _cache_is_fresh(cache, latest_update):
        return []
    cached_cards = _clean_lifehacks(cache.get("items") if isinstance(cache, dict) else None)
    return cached_cards if len(cached_cards) == 3 else []


def _insight_tone(text: str) -> str:
    lower = text.lower()
    if any(word in lower for word in ("риск", "сон", "тревог", "устал", "напряж", "опас")):
        return "attention"
    if any(word in lower for word in ("опор", "сил", "ресурс", "помог", "легче")):
        return "resource"
    if any(word in lower for word in ("границ", "шаг", "выбор", "понял", "получ")):
        return "growth"
    return "calm"


def _build_insights(
    *,
    user: User,
    memories: list[UserMemory],
    latest_update: datetime | None,
) -> list[dict[str, str]]:
    cache = (user.support_preferences or {}).get(INSIGHT_CACHE_KEY)
    if _cache_is_fresh(cache, latest_update):
        cached_insights = _clean_insights(cache.get("items") if isinstance(cache, dict) else None)
        if cached_insights:
            return cached_insights

    insights: list[dict[str, str]] = []
    for memory in _memory_items(memories, "insight")[:5]:
        text = _clip(memory.content, limit=210)
        insights.append(
            {
                "title": _clip(memory.title, limit=78),
                "text": text,
                "tone": _insight_tone(f"{memory.title} {text}"),
            }
        )
    return _clean_insights(insights)


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
            "text": (
                "Пока данных немного. Можно написать в чат, что сейчас происходит "
                "и где тяжелее всего."
            ),
            "next_step": "Начните с одной честной фразы без подбора правильных слов.",
            "source": "стартовая подсказка",
        },
        {
            "title": "Сузить тему",
            "text": (
                "Если всего слишком много, выберите один эпизод, к которому хочется "
                "вернуться первым."
            ),
            "next_step": "Напишите, что случилось, кто был рядом и что задело сильнее всего.",
            "source": "стартовая подсказка",
        },
    ]


def _empty_support_cards() -> list[dict[str, str]]:
    return [
        {
            "title": "Пауза перед ответом",
            "text": (
                "Если разговор задевает, отложите ответ на несколько минут "
                "и вернитесь к нему спокойнее."
            ),
            "kind": "опора",
        },
        {
            "title": "Место для восстановления",
            "text": (
                "Отметьте, после чего сегодня стало хоть немного легче, "
                "и сохраните это как рабочую опору."
            ),
            "kind": "опора",
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
    latest_update = _latest_dt([*facts, *people, *topics, *memories, *messages])

    focus_cards = _build_focus_cards(topics, memories) or _empty_focus_cards()
    support_cards = _build_support_cards(facts, memories, people) or _empty_support_cards()
    lifehack_cards = _build_lifehacks(user, latest_update)
    attention_cards = _build_attention_cards(user=user, facts=facts, topics=topics)
    insights = _build_insights(user=user, memories=memories, latest_update=latest_update)

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
