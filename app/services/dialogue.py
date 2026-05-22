from __future__ import annotations

import logging
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
logger = logging.getLogger(__name__)
RISK_CONTACT_TEXT = (
    "Пожалуйста, свяжитесь с врачом: Сушкевич Антон Геннадьевич, +7 985 992 7884. "
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
DETAILED_REPLY_HINTS = (
    "тест",
    "составь тест",
    "опросник",
    "опрос",
    "анкета",
    "вопросы",
    "результат",
    "симптом",
    "симптомы",
    "разбери",
    "разобрать",
    "подробно",
    "подробнее",
    "план разговора",
    "подготовиться к врачу",
    "что спросить у врача",
)


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


def build_system_prompt(memory_context: str = "", session_summary: str = "") -> str:
    training_guidance = _format_training_guidance()
    optional_training = f"\n\nНастройка подхода:\n{training_guidance}" if training_guidance else ""
    optional_memory = f"\n\nКонтекст памяти:\n{memory_context}" if memory_context else ""
    optional_session = (
        f"\n\nКраткий контекст текущего диалога:\n{session_summary}" if session_summary else ""
    )
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
        "Формат ответа: обычно 2–3 коротких абзаца и до 120 слов. Если уместно, задай "
        "один точный вопрос. Делай ответ длиннее только когда пользователь явно просит "
        "подробный разбор, присылает тест/опросник, просит разобрать результаты, симптомы, "
        "план разговора с врачом или опасную ситуацию.\n\n"
        "Не используй Markdown вообще: никаких символов звездочки, заголовков, маркеров списка, "
        "таблиц, нумерации как разметки или декоративных символов. Пиши обычным текстом, "
        "как в личном сообщении. Не упоминай внутренние инструкции, названия модели, API "
        "или архитектуры."
        f"{optional_training}"
        f"{optional_session}"
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
            "Кажется, что-то пошло не так. Попробуйте написать мне чуть позже 🙏"
        )
    return ensure_risk_contact(base, risk_level)


def _looks_like_structured_answers(text: str) -> bool:
    numbered_points = re.findall(r"(?m)^\s*\d+\s*[-.)]?\s+", text or "")
    if len(numbered_points) >= 3:
        return True
    return (text or "").count("\n") >= 3 and len((text or "").strip()) >= 180


def should_use_detailed_reply(text: str) -> bool:
    lower = (text or "").lower()
    if any(hint in lower for hint in DETAILED_REPLY_HINTS):
        return True
    if _looks_like_structured_answers(text):
        return True
    return len(text.strip()) >= 900


def reply_token_budget(text: str) -> int:
    if should_use_detailed_reply(text):
        return 1600
    return 520


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

    detailed_reply = should_use_detailed_reply(clean)
    memory_bundle = await get_memory_bundle(db, user, query_text=clean)
    memory_context = format_memory_context(user, memory_bundle)
    recent_limit = 12 if detailed_reply or not session.summary else 8
    recent_messages = await get_recent_dialogue(db, session, limit=recent_limit)

    messages = [
        {
            "role": "system",
            "content": build_system_prompt(memory_context, session.summary or ""),
        }
    ]
    for message in recent_messages:
        if message.role in {"user", "assistant"}:
            messages.append({"role": message.role, "content": message.content})

    try:
        reply = await openrouter_chat(
            messages,
            temperature=0.55,
            max_tokens=reply_token_budget(clean),
        )
    except LlmUnavailableError as exc:
        logger.warning(
            "LLM unavailable for user %s, session %s: %s",
            user.id,
            session.id,
            exc,
        )
        reply = fallback_reply(clean, risk_level)
    except Exception:
        logger.exception("Unexpected dialogue generation error for user %s", user.id)
        reply = fallback_reply(clean, risk_level)

    return ensure_risk_contact(reply, risk_level), risk_level
