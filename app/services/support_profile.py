from __future__ import annotations

import hashlib
from collections import Counter
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.memory import ImportantFact, KnownPerson, OpenTopic, UserMemory
from app.models.message import Message
from app.models.user import User

RECENT_MESSAGE_LIMIT = 120
LIFEHACK_CACHE_KEY = "_support_lifehacks_cache"
MANUAL_LIFEHACK_KEY = "_support_manual_lifehacks"
LIFEHACK_FEEDBACK_KEY = "_support_lifehack_feedback"
INSIGHT_CACHE_KEY = "_support_insights_cache"
MANUAL_DIARY_KEY = "_support_manual_diary"
SUPPORT_PROFILE_CACHE_VERSION = 2
LOW_CONTEXT_HINT = "Информации о вас пока мало"
LOW_CONTEXT_TONE = ("#eef2f6", "#aeb8c4")
DIARY_THEMES = {"agency", "empathy", "boundaries", "sensitivity", "clarity", "rationality"}
DIARY_COLOR_THEMES = {
    "mint",
    "peach",
    "violet",
    "sky",
    "blue",
    "rose",
    "coral",
    "lemon",
    "green",
}
DIARY_THEME_COLORS = {
    "agency": "mint",
    "empathy": "peach",
    "boundaries": "violet",
    "sensitivity": "sky",
    "clarity": "blue",
    "rationality": "rose",
}

DIMENSIONS = (
    {
        "key": "agency",
        "label": "Субъектность",
        "hint": (
            "Насколько вы чувствуете, что влияете на свою жизнь, "
            "принимаете решения сами и не живете в позиции вечной уступки "
            "или подчинения чужой воле."
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
            "Насколько вы чувствуете свои пределы, умеете обозначать их "
            "другим, говорить «нет» и замечать момент, когда на вас "
            "начинают заходить слишком далеко."
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

METRIC_BANDS: dict[str, list[tuple[int, str]]] = {
    "agency": [
        (
            20,
            "Сейчас у вас часто возникает ощущение, что курс жизни задают "
            "обстоятельства или другие люди, а на свои решения и выбор "
            "влиять получается не всегда.",
        ),
        (
            40,
            "Контроль над своей жизнью временами ускользает: вы можете "
            "понимать, чего хотите, но не всегда доводите это до собственного "
            "решения и действия.",
        ),
        (
            60,
            "Базовое чувство влияния на свою жизнь уже есть, но в сложных "
            "ситуациях вы все еще можете откатываться в уступку, сомнение "
            "или ожидание чужой воли.",
        ),
        (
            80,
            "Сейчас вы чаще сами задаете курс своей жизни и принимаете решения "
            "сами, не живете в позиции вечной уступки или подчинения чужой воле.",
        ),
        (
            100,
            "У вас сейчас сильное чувство авторства своей жизни: вы скорее "
            "влияете на происходящее сами, чем живете по чужому сценарию.",
        ),
    ],
    "empathy": [
        (
            20,
            "Чувства других людей пока считываются с трудом, и из-за этого "
            "можно не сразу замечать, что они переживают и как ваши слова "
            "или тон на них действуют.",
        ),
        (
            40,
            "Вы временами улавливаете эмоции других людей, но не всегда "
            "удерживаете их в поле внимания, особенно если сами напряжены.",
        ),
        (
            60,
            "Вы обычно замечаете состояние других людей и в целом понимаете, "
            "что они чувствуют, хотя в перегрузе можете упрощать их переживания.",
        ),
        (
            80,
            "Вы хорошо считываете эмоции и контекст других людей, поэтому "
            "обычно точнее понимаете, что с ними происходит, и мягче строите общение.",
        ),
        (
            100,
            "У вас очень сильная чувствительность к переживаниям других: "
            "вы тонко улавливаете эмоции, нюансы отношений и реакцию людей на ваши слова.",
        ),
    ],
    "boundaries": [
        (
            20,
            "Свои границы пока обозначаются слабо: есть риск долго терпеть, "
            "лишний раз соглашаться и поздно замечать, что на вас уже давят.",
        ),
        (
            40,
            "Вы уже чувствуете, когда вам что-то не подходит, но не всегда "
            "вовремя обозначаете это другим или отстаиваете до конца.",
        ),
        (
            60,
            "В понятных ситуациях вы умеете говорить \"нет\" и обозначать свои "
            "пределы, но в чувствительных темах границы еще могут шататься.",
        ),
        (
            80,
            "Вы в целом хорошо чувствуете свои пределы и умеете спокойно "
            "обозначать другим, что вам подходит, а что нет, без лишних оправданий.",
        ),
        (
            100,
            "У вас сейчас очень хорошее понимание своих границ: вы вовремя "
            "замечаете давление и уверенно обозначаете, что вам подходит, а что нет.",
        ),
    ],
    "sensitivity": [
        (
            20,
            "Сигналы тела и эмоций пока замечаются поздно: усталость, тревога "
            "или перегруз могут накапливаться раньше, чем вы успеваете это заметить.",
        ),
        (
            40,
            "Вы иногда считываете свое состояние, но часть важных сигналов "
            "тела и эмоций все еще проскальзывает мимо.",
        ),
        (
            60,
            "Контакт со своим состоянием уже есть: вы обычно замечаете "
            "усталость, тревогу, напряжение или перегруз, хотя не всегда сразу.",
        ),
        (
            80,
            "Вы хорошо чувствуете свое тело и эмоции, поэтому обычно раньше "
            "замечаете перегруз, напряжение и смену состояния.",
        ),
        (
            100,
            "У вас сейчас очень тонкий контакт с собой: вы быстро замечаете, "
            "что происходит с телом, эмоциями и уровнем внутреннего напряжения.",
        ),
    ],
    "clarity": [
        (
            20,
            "Сейчас в этой зоне много тумана: трудно отделять факты от обиды, "
            "фантазий, автоматических выводов и признавать свою часть происходящего.",
        ),
        (
            40,
            "Ясность временами появляется, но в сложных ситуациях вам все еще "
            "нелегко объективно увидеть свою роль, ошибки и мотивы других людей.",
        ),
        (
            60,
            "Вы уже умеете разбираться в происходящем и отделять факты от эмоций, "
            "хотя в заряженных темах вас еще может уносить в субъективность.",
        ),
        (
            80,
            "Вы довольно ясно видите картину: умеете замечать свою роль "
            "в ситуации, признавать ошибки и не так легко путаете факты с эмоциями.",
        ),
        (
            100,
            "Сейчас у вас очень сильная ясность: вы хорошо отличаете факты "
            "от интерпретаций и способны честно смотреть на себя и других.",
        ),
    ],
    "rationality": [
        (
            20,
            "Сейчас вы скорее опираетесь на впечатление, веру или интуитивное "
            "объяснение, чем на проверку фактов, доказательств и реальности.",
        ),
        (
            40,
            "Стремление к фактам у вас есть, но в уязвимых темах вы все еще "
            "можете принимать объяснение без достаточной проверки.",
        ),
        (
            60,
            "Вы в целом опираетесь на факты, проверку и здравый смысл, "
            "хотя в эмоциональных темах логика не всегда удерживает позицию.",
        ),
        (
            80,
            "Вы чаще ориентируетесь на реальность, проверку и доказуемость, "
            "а не на красивое, но неподтвержденное объяснение.",
        ),
        (
            100,
            "Сейчас вы очень сильно держитесь за факты, логику и проверяемость "
            "и редко верите во что-то без достаточных оснований.",
        ),
    ],
}

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
        "detail": None,
        "tone": LOW_CONTEXT_TONE,
        "order": index,
        "empty": True,
    }


def _metric_detail(key: str, value: int) -> str:
    for upper_bound, text in METRIC_BANDS.get(key, []):
        if value <= upper_bound:
            return text
    return METRIC_BANDS.get(key, [("", "")])[-1][1] if METRIC_BANDS.get(key) else ""


def _normalize_diary_theme(value: Any) -> str | None:
    theme = str(value or "").strip().lower()
    return theme if theme in DIARY_THEMES else None


def _normalize_diary_color_theme(value: Any) -> str | None:
    theme = str(value or "").strip().lower()
    return theme if theme in DIARY_COLOR_THEMES else None


def _lifehack_id(item: dict[str, Any]) -> str:
    explicit = _clip(item.get("id"), limit=80)
    if explicit:
        return explicit
    base = "|".join(
        [
            str(item.get("title") or "").strip(),
            str(item.get("text") or item.get("description") or "").strip(),
            str(item.get("action") or item.get("next_step") or "").strip(),
        ]
    )
    digest = hashlib.sha1(base.encode("utf-8")).hexdigest()[:16]
    return f"lh-{digest}"


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
                "detail": _metric_detail(key, scores[key]),
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
    for item in items[:12]:
        if not isinstance(item, dict):
            continue
        title = _clip(item.get("title"), limit=64)
        text = _clip(item.get("text") or item.get("description"), limit=190)
        action = _clip(item.get("action") or item.get("next_step"), limit=130)
        combined = f"{title} {text} {action}".lower()
        if any(word in combined for word in LIFEHACK_FORBIDDEN_WORDS):
            continue
        if title and text:
            card: dict[str, str] = {
                "id": _lifehack_id(item),
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
            theme = _normalize_diary_theme(item.get("theme"))
            insights.append({"title": title, "text": text, "tone": tone, "theme": theme})
    return insights


def _clean_manual_diary_items(items: Any) -> list[dict[str, str]]:
    if not isinstance(items, list):
        return []
    cleaned: list[dict[str, str]] = []
    for item in items[:24]:
        if not isinstance(item, dict):
            continue
        item_id = _clip(item.get("id"), limit=80)
        title = _clip(item.get("title"), limit=78)
        text = _clip(item.get("text") or item.get("description"), limit=240)
        theme = _normalize_diary_theme(item.get("theme")) or "clarity"
        color_theme = (
            _normalize_diary_color_theme(item.get("color_theme"))
            or DIARY_THEME_COLORS.get(theme)
            or "blue"
        )
        if not item_id or not title or not text:
            continue
        cleaned.append(
            {
                "id": item_id,
                "title": title,
                "text": text,
                "theme": theme,
                "color_theme": color_theme,
                "manual": True,
            }
        )
    return cleaned


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


def get_manual_lifehacks(user: User) -> list[dict[str, str]]:
    raw = (user.support_preferences or {}).get(MANUAL_LIFEHACK_KEY)
    if not isinstance(raw, list):
        return []
    return _clean_lifehacks(raw)


def get_lifehack_feedback(user: User) -> dict[str, str]:
    raw = (user.support_preferences or {}).get(LIFEHACK_FEEDBACK_KEY)
    if not isinstance(raw, dict):
        return {}
    clean: dict[str, str] = {}
    for key, value in raw.items():
        key_text = _clip(key, limit=80)
        value_text = str(value or "").strip().lower()
        if key_text and value_text in {"helped", "not_helped"}:
            clean[key_text] = value_text
    return clean


def set_lifehack_feedback(user: User, item_id: str, value: str) -> bool:
    item_key = _clip(item_id, limit=80)
    normalized = str(value or "").strip().lower()
    if not item_key or normalized not in {"helped", "not_helped"}:
        return False
    feedback = get_lifehack_feedback(user)
    feedback[item_key] = normalized
    preferences = user.support_preferences or {}
    user.support_preferences = {
        **preferences,
        LIFEHACK_FEEDBACK_KEY: feedback,
    }
    return True


def append_manual_lifehack(user: User, item: dict[str, Any]) -> dict[str, str] | None:
    cleaned = _clean_lifehacks([item])
    if not cleaned:
        return None
    lifehack = cleaned[0]
    items = [lifehack, *get_manual_lifehacks(user)]
    preferences = user.support_preferences or {}
    user.support_preferences = {
        **preferences,
        MANUAL_LIFEHACK_KEY: items[:8],
    }
    return lifehack


def get_manual_diary_items(user: User) -> list[dict[str, str]]:
    raw = (user.support_preferences or {}).get(MANUAL_DIARY_KEY)
    if not isinstance(raw, list):
        return []
    return _clean_manual_diary_items(raw)


def upsert_manual_diary_item(
    user: User,
    *,
    item_id: str | None,
    title: str,
    text: str,
    theme: str | None,
    color_theme: str | None = None,
) -> dict[str, str]:
    items = get_manual_diary_items(user)
    cleaned_item = {
        "id": item_id or str(uuid4()),
        "title": _clip(title, limit=78),
        "text": _clip(text, limit=240),
        "theme": _normalize_diary_theme(theme) or "clarity",
        "color_theme": _normalize_diary_color_theme(color_theme)
        or DIARY_THEME_COLORS.get(_normalize_diary_theme(theme) or "clarity")
        or "blue",
        "manual": True,
    }
    updated: list[dict[str, str]] = []
    replaced = False
    for existing in items:
        if existing["id"] == cleaned_item["id"]:
            updated.append(cleaned_item)
            replaced = True
        else:
            updated.append(existing)
    if not replaced:
        updated.insert(0, cleaned_item)
    preferences = user.support_preferences or {}
    user.support_preferences = {
        **preferences,
        MANUAL_DIARY_KEY: updated[:24],
    }
    return cleaned_item


def delete_manual_diary_item(user: User, item_id: str) -> bool:
    items = get_manual_diary_items(user)
    updated = [item for item in items if item.get("id") != item_id]
    if len(updated) == len(items):
        return False
    preferences = user.support_preferences or {}
    user.support_preferences = {
        **preferences,
        MANUAL_DIARY_KEY: updated,
    }
    return True


def _build_lifehacks(user: User, latest_update: datetime | None) -> list[dict[str, str]]:
    manual_lifehacks = get_manual_lifehacks(user)
    feedback = get_lifehack_feedback(user)
    cache = (user.support_preferences or {}).get(LIFEHACK_CACHE_KEY)
    if not _cache_is_fresh(cache, latest_update):
        return [{**item, "feedback": feedback.get(item["id"])} for item in manual_lifehacks]
    cached_cards = _clean_lifehacks(cache.get("items") if isinstance(cache, dict) else None)
    generated = cached_cards if len(cached_cards) == 3 else []
    return [
        {**item, "feedback": feedback.get(item["id"])}
        for item in [*manual_lifehacks, *generated][:11]
    ]


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
    manual_items = get_manual_diary_items(user)
    cache = (user.support_preferences or {}).get(INSIGHT_CACHE_KEY)
    if _cache_is_fresh(cache, latest_update):
        cached_insights = _clean_insights(cache.get("items") if isinstance(cache, dict) else None)
        if cached_insights:
            generated = [
                {**item, "manual": False}
                for item in cached_insights
            ]
            return [*manual_items, *generated][:10]

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
    generated = [{**item, "manual": False} for item in _clean_insights(insights)]
    return [*manual_items, *generated][:10]


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
