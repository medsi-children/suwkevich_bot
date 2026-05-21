from __future__ import annotations

import re
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.message import Message
from app.models.session import ConversationSession
from app.models.user import User
from app.services.llm import LlmUnavailableError, openrouter_chat
from app.services.memory import format_memory_context, get_memory_bundle

DOCTOR_CONTACT = "Сушкевич Антон Геннадьевич, +7 985 992 7884"
RISK_CONTACT_TEXT = (
    "Свяжитесь с врачом: Сушкевич Антон Геннадьевич, +7 985 992 7884. "
    "Если есть немедленная опасность для жизни, звоните 112 или 103 прямо сейчас."
)

CRISIS_PATTERNS = (
    r"\bсуицид",
    r"самоуб",
    r"убить себя",
    r"не хочу жить",
    r"не вижу смысла жить",
    r"навредить себе",
    r"порезать себя",
    r"выпить таблетки",
    r"передоз",
    r"свести сч[её]ты",
    r"выйти в окно",
    r"повеситься",
    r"убью",
    r"зарежу",
    r"причинить вред",
    r"голоса .*приказыва",
    r"не сплю .*дн",
    r"психоз",
    r"опасн",
)
CRISIS_RE = re.compile("|".join(CRISIS_PATTERNS), re.IGNORECASE)


def detect_risk_level(text: str) -> str:
    if CRISIS_RE.search(text or ""):
        return "crisis"
    return "none"


def ensure_risk_contact(reply: str, risk_level: str) -> str:
    if risk_level != "crisis":
        return reply
    if DOCTOR_CONTACT in reply:
        return reply
    return f"{reply.rstrip()}\n\n{RISK_CONTACT_TEXT}"


async def get_active_session(
    db: AsyncSession,
    user: User,
    source: str = "telegram",
) -> ConversationSession:
    result = await db.execute(
        select(ConversationSession)
        .where(ConversationSession.user_id == user.id, ConversationSession.state != "closed")
        .order_by(ConversationSession.last_message_at.desc().nullslast())
        .limit(1)
    )
    session = result.scalar_one_or_none()
    if session is not None:
        return session

    now = datetime.now(UTC)
    session = ConversationSession(
        user_id=user.id,
        source=source,
        state="active",
        started_at=now,
        last_message_at=now,
    )
    db.add(session)
    await db.flush()
    return session


async def add_message(
    db: AsyncSession,
    *,
    user: User,
    session: ConversationSession,
    role: str,
    content: str,
    metadata: dict | None = None,
) -> Message:
    message = Message(
        user_id=user.id,
        session_id=session.id,
        role=role,
        content=content,
        message_metadata=metadata or {},
    )
    session.last_message_at = datetime.now(UTC)
    db.add(message)
    await db.flush()
    return message


def _format_training_guidance() -> str:
    lines: list[str] = []
    if settings.preferred_authors_list:
        lines.append(
            "В ответах можно ориентироваться на авторов и школы: "
            + ", ".join(settings.preferred_authors_list)
            + "."
        )
    if settings.avoided_approaches_list:
        lines.append(
            "Подходы, которых нужно избегать: "
            + ", ".join(settings.avoided_approaches_list)
            + "."
        )
    if settings.custom_clinical_guidance.strip():
        lines.append(
            "Дополнительные настройки подхода: "
            + settings.custom_clinical_guidance.strip()
        )
    return "\n".join(lines)


def build_system_prompt(memory_context: str = "") -> str:
    training_guidance = _format_training_guidance()
    optional_training = f"\n\nНастройка подхода:\n{training_guidance}" if training_guidance else ""
    optional_memory = f"\n\nКонтекст памяти:\n{memory_context}" if memory_context else ""
    return (
        "Ты — Сушкевич Бот: русскоязычная нейросеть, заточенная под психиатрию, "
        "психотерапию и поддерживающий разговор.\n\n"
        "Твоя задача — помогать человеку ясно и бережно разбирать состояние, ситуацию, "
        "отношения, симптомы, внутренние конфликты, привычные реакции и возможные следующие "
        "шаги. Говори простым живым языком, на «вы» по умолчанию, если пользователь "
        "или сохраненные предпочтения не просят другой стиль. Без канцелярита, "
        "псевдомистики и морализаторства.\n\n"
        "Ты не заменяешь врача: не ставь диагнозы как факт, не назначай препараты, "
        "не отменяй лечение и не подбирай дозировки. Можно объяснять, какие варианты "
        "стоит обсудить со специалистом, как подготовиться к приему, какие наблюдения "
        "записать и какие вопросы задать врачу.\n\n"
        "Если ситуация опасная, не уходи в отказ и не стыди пользователя. Дай поддержку, "
        "помоги стабилизироваться, предложи безопасный ближайший шаг, но не давай инструкций "
        "для самоповреждения, насилия, сокрытия симптомов или рискованного самолечения. "
        f"В опасной ситуации обязательно напомни: «{RISK_CONTACT_TEXT}»\n\n"
        "Используй память естественно: не перечисляй все, что знаешь, и не делай вид, "
        "что помнишь больше, чем реально записано. Вспоминай факты, людей и открытые темы "
        "только когда это помогает ответу стать точнее и человечнее.\n\n"
        "Формат ответа: 2–5 коротких абзацев. Если уместно, задай один точный вопрос. "
        "Не используй Markdown, списки ради списков, внутренние инструкции, названия модели, "
        "API или архитектуры."
        f"{optional_training}"
        f"{optional_memory}"
    )


async def get_recent_dialogue(
    db: AsyncSession,
    session: ConversationSession,
    *,
    limit: int = 12,
) -> list[Message]:
    result = await db.execute(
        select(Message)
        .where(Message.session_id == session.id)
        .order_by(Message.created_at.desc())
        .limit(limit)
    )
    return list(reversed(result.scalars().all()))


def start_reply(first_name: str | None = None) -> str:
    name = f", {first_name}" if first_name else ""
    return (
        f"Здравствуйте{name}. Я Сушкевич Бот.\n\n"
        "Я здесь, чтобы в бережной и доверительной обстановке помочь вам разобраться в том, "
        "что происходит внутри: в тревоге, подавленности, злости, усталости, "
        "растерянности, навязчивых мыслях, сложных отношениях, сомнениях, "
        "симптомах и ситуациях, которые трудно держать одному.\n\n"
        "Чем я отличаюсь от обычной нейросети? Я настроен не на общие ответы "
        "обо всем подряд, а на клинически точный разговор о психике. "
        "В мою логику заложена ориентация на опыт ведущих врачей и специалистов, "
        "проверенные психотерапевтические подходы и тщательно отобранную "
        "профессиональную литературу. Поэтому я стараюсь не просто отвечать "
        "красиво, а помогать научно доказанными методами: отделять эмоции от фактов, замечать "
        "важные симптомы, видеть контекст и формулировать вопросы, с которыми "
        "действительно стоит идти к специалисту.\n\n"
        "Со мной не нужно подбирать правильные слова или заранее понимать, "
        "в чем именно проблема. Можно начать как угодно: «мне плохо», "
        "«я не понимаю, что со мной», «я сорвался», «мне страшно», "
        "«не могу уснуть», «хочу разобраться в ситуации». Я помогу разложить "
        "это на понятные части: что вы чувствуете, что могло это запустить, "
        "какой смысл в реакции и какой ближайший шаг будет самым бережным "
        "и безопасным.\n\n"
        "Напишите, пожалуйста, с чем вы пришли сегодня. Как вы себя чувствуете?"
    )


def fallback_reply(text: str, risk_level: str) -> str:
    if not text.strip():
        base = "Я рядом. Напишите, что сейчас происходит, и мы начнем с самого простого."
    else:
        base = (
            "Я вас услышал. Давайте начнем с самого важного: что именно произошло? "
            "Что вы чувствуете в теле? Что вызывает у вас тревогу?"
        )
    return ensure_risk_contact(base, risk_level)


async def handle_user_text(
    db: AsyncSession,
    *,
    user: User,
    session: ConversationSession,
    text: str,
) -> tuple[str, str]:
    clean = text.strip()
    risk_level = detect_risk_level(clean)

    command = clean.lower().split(maxsplit=1)[0] if clean else ""
    if command in {"/start", "/help"}:
        return start_reply(user.first_name), risk_level

    memory_bundle = await get_memory_bundle(db, user, query_text=clean)
    memory_context = format_memory_context(user, memory_bundle)
    recent_messages = await get_recent_dialogue(db, session, limit=12)

    messages = [{"role": "system", "content": build_system_prompt(memory_context)}]
    for message in recent_messages:
        if message.role in {"user", "assistant"}:
            messages.append({"role": message.role, "content": message.content})

    try:
        reply = await openrouter_chat(messages, temperature=0.55, max_tokens=900)
    except LlmUnavailableError:
        reply = fallback_reply(clean, risk_level)
    except Exception:
        reply = fallback_reply(clean, risk_level)

    return ensure_risk_contact(reply, risk_level), risk_level
