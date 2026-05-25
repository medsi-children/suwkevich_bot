from __future__ import annotations

import logging
import re
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.message import Message
from app.models.session import ConversationSession
from app.models.user import User
from app.services.clinical_knowledge import get_clinical_knowledge_context
from app.services.diagnostic_domains import analyze_clinical_domains, format_domain_context
from app.services.llm import LlmUnavailableError, openrouter_chat
from app.services.memory import format_memory_context, get_memory_bundle
from app.services.telegram import send_consultation_request

DOCTOR_CONTACT = "Сушкевич Антон Геннадьевич, +7 985 992 7884"
AWAITING_NAME_STATE = "awaiting_name"
APPOINTMENT_NAME_STATE = "appointment_name"
APPOINTMENT_PHONE_STATE = "appointment_phone"
APPOINTMENT_SUMMARY_STATE = "appointment_summary"
APPOINTMENT_DRAFT_KEY = "_consultation_request"
logger = logging.getLogger(__name__)
EMERGENCY_SAFETY_TEXT = (
    "Если есть немедленная опасность для жизни, рекомендую связаться с врачом "
    "или экстренной помощью: 112 или 103 прямо сейчас."
)
DOCTOR_CONTACT_TEXT = (
    f"Контакт врача: {DOCTOR_CONTACT}. Если есть немедленная опасность для жизни, "
    "звоните 112 или 103 прямо сейчас."
)
CONSULTATION_INVITE_TEXT = (
    "Если хотите, я могу помочь записаться на консультацию к психиатру. "
    "Напишите: хочу записаться на консультацию."
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
    r"убью (?:себя|его|е[её]|их|кого-нибудь|кого-то)",
    r"убить (?:себя|его|е[её]|их|кого-нибудь|кого-то)",
    r"зарежу",
    r"причинить вред (?:себе|ему|ей|им|кому-нибудь|кому-то)",
    r"голоса .*приказыва",
)
CRISIS_RE = re.compile("|".join(CRISIS_PATTERNS), re.IGNORECASE)
DOCTOR_CONTACT_REQUEST_RE = re.compile(
    "|".join(
        (
            r"контакт(?:ы)? врач",
            r"номер врач",
            r"телефон врач",
            r"как связаться с врач",
            r"как записаться",
            r"дай(?:те)? контакт",
            r"нуж(?:ен|на|ны) контакт",
            r"сушкевич",
            r"антон геннадьевич",
        )
    ),
    re.IGNORECASE,
)
HELP_REQUEST_RE = re.compile(
    "|".join(
        (
            r"мне нужн[аы]? помощь",
            r"помогите(?: мне)?",
            r"помоги(?: мне)?",
            r"нужн[аы]? помощь с",
            r"куда обратиться",
            r"что мне делать",
            r"не справляюсь",
        )
    ),
    re.IGNORECASE,
)
CONSULTATION_REQUEST_RE = re.compile(
    "|".join(
        (
            r"\bхочу\s+запис(?:ать|аться)\b",
            r"\bхочу\s+на\s+консультаци",
            r"\bзапишите\s+меня\b",
            r"\bзаписаться\s+к\s+(?:врачу|психиатру|доктору)\b",
            r"\bкак\s+записаться\b",
            r"\bзапись\s+на\s+консультаци",
            r"\bнужна\s+консультаци(?:я|ю)\b",
            r"\bхочу\s+к\s+психиатру\b",
            r"\bможно\s+записаться\b",
        )
    ),
    re.IGNORECASE,
)

GREETING_INTENT_RE = re.compile(
    "|".join(
        (
            r"^\s*(?:привет|здравствуй(?:те)?|добрый день|доброе утро|добрый вечер|хай|hi|hello)\s*[!.?]*\s*$",
            r"^\s*(?:привет|здравствуй(?:те)?|добрый день|доброе утро|добрый вечер)[,\s]*(?:как дела|как вы|как ты)?\s*[!.?]*\s*$",
        )
    ),
    re.IGNORECASE,
)

ABOUT_BOT_INTENT_RE = re.compile(
    "|".join(
        (
            r"^\s*(?:кто ты|что ты делаешь|что ты умеешь|что ты можешь|расскажи о себе|расскажи про себя|представься|чем ты можешь помочь|как ты можешь помочь|как ты работаешь|как ты устроен|что это за бот|зачем ты нужен|для чего ты|зачем ты здесь|в чем твоя задача|какая у тебя задача|какие у тебя функции|что с тобой можно делать|как с тобой работать|объясни что ты|объясни кто ты)\s*[!.?]*\s*$",
            r"^\s*(?:привет|здравствуй(?:те)?|добрый день|доброе утро|добрый вечер)[,\s]+(?:кто ты|что ты делаешь|что ты умеешь|что ты можешь|расскажи о себе|расскажи про себя|представься|чем ты можешь помочь|как ты можешь помочь|как ты работаешь|как ты устроен|что это за бот|зачем ты нужен|для чего ты|зачем ты здесь|в чем твоя задача|какая у тебя задача|какие у тебя функции|что с тобой можно делать|как с тобой работать|объясни что ты|объясни кто ты)\s*[!.?]*\s*$",
            r"^\s*(?:а\s+)?(?:можешь|можете)\s+(?:объяснить|рассказать|сказать)[,\s]+(?:кто ты|что ты|для чего ты|зачем ты|что ты умеешь|что ты можешь|как ты работаешь|как ты устроен|чем ты можешь помочь)\s*[!.?]*\s*$",
            r"^\s*(?:и\s+)?(?:что|чем|как)\s+(?:ты|вы)\s+(?:можешь|можете|умеешь|умеете)\s*(?:помочь|делать)?\s*[!.?]*\s*$",
            r"^\s*(?:для чего|зачем)\s+(?:ты|вы)\s+(?:вообще\s+)?(?:тут|здесь|нужен|нужны)?\s*[!.?]*\s*$",
        )
    ),
    re.IGNORECASE,
)


def _clean_intent_text(text: str) -> str:
    return " ".join((text or "").split()).strip()


def is_greeting_intent(text: str) -> bool:
    clean = _clean_intent_text(text)
    if not clean or len(clean) > 120:
        return False
    return bool(GREETING_INTENT_RE.search(clean))


def is_about_bot_intent(text: str) -> bool:
    clean = _clean_intent_text(text)
    if not clean or len(clean) > 240:
        return False
    return bool(ABOUT_BOT_INTENT_RE.search(clean))


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


def wants_doctor_contact(text: str) -> bool:
    return bool(DOCTOR_CONTACT_REQUEST_RE.search(text or ""))


def wants_help_with_crisis(text: str, risk_level: str) -> bool:
    return risk_level == "crisis" and bool(HELP_REQUEST_RE.search(text or ""))


def wants_consultation_booking(text: str) -> bool:
    return bool(CONSULTATION_REQUEST_RE.search(text or ""))


def ensure_risk_contact(reply: str, risk_level: str, user_text: str = "") -> str:
    if wants_doctor_contact(user_text):
        if DOCTOR_CONTACT in reply:
            return reply
        return f"{reply.rstrip()}\n\n{DOCTOR_CONTACT_TEXT}"

    if risk_level != "crisis":
        return reply

    if wants_help_with_crisis(user_text, risk_level):
        if DOCTOR_CONTACT in reply:
            return reply
        return f"{reply.rstrip()}\n\n{DOCTOR_CONTACT_TEXT}"

    if "112" in reply or "103" in reply or "экстренной помощью" in reply.lower():
        base_reply = reply
    else:
        base_reply = f"{reply.rstrip()}\n\n{EMERGENCY_SAFETY_TEXT}"

    if CONSULTATION_INVITE_TEXT.lower() in base_reply.lower():
        return base_reply
    return f"{base_reply.rstrip()}\n\n{CONSULTATION_INVITE_TEXT}"


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


def build_system_prompt(
    memory_context: str = "",
    session_summary: str = "",
    clinical_knowledge_context: str = "",
    clinical_domain_context: str = "",
) -> str:
    optional_domains = (
        f"\n\nВнутренние клинические домены для проверки:\n{clinical_domain_context}"
        if clinical_domain_context
        else ""
    )
    optional_knowledge = (
        "\n\nВнутренняя клиническая база, релевантная текущему запросу:\n"
        f"{clinical_knowledge_context}"
        if clinical_knowledge_context
        else ""
    )
    optional_memory = f"\n\nКонтекст памяти:\n{memory_context}" if memory_context else ""
    optional_session = (
        f"\n\nКраткий контекст текущего диалога:\n{session_summary}" if session_summary else ""
    )
    return (
        "Ты — Сушкевич Бот: русскоязычный клинически ориентированный помощник "
        "по психиатрическому ориентированию, раннему выявлению рисков и подготовке "
        "к очной помощи. Ты не виртуальный психиатр и не психологический коуч. "
        "Твоя основная роль — помогать пользователю описать состояние, увидеть "
        "динамику, красные флаги, уровень срочности и безопасные следующие шаги.\n\n"
        "Думай не ярлыками, а клиническими гипотезами и уровнем риска. Не говори "
        "«у вас шизофрения», «это БАР», «это ПРЛ», «это точно анорексия» или "
        "«это не психоз». Используй осторожные формулы: «по описанию есть признаки, "
        "которые иногда встречаются при...», «это не диагноз по переписке, но повод "
        "для очной оценки», «здесь важно исключить...», «данных пока мало, но "
        "настораживает...». Различай гипотезу, риск, красный флаг, очную оценку "
        "и экстренную ситуацию.\n\n"
        "Каждый ответ внутренне проверяй по карте: срочность и безопасность; "
        "суицидальность и самоповреждение; психоз и сохранность критики; мания, "
        "сон и расторможенность; депрессия и ангедония; тревога, паника и ОКР; "
        "диссоциация и эмоциональная дисрегуляция; РПП, вес, еда и очищение; "
        "ПАВ, лекарства и соматические причины; социальное функционирование; "
        "динамика во времени; 1-3 ключевых уточняющих вопроса.\n\n"
        "Один симптом не равен диагнозу. Оценивай синдром, длительность, начало, "
        "ухудшение, эпизодичность, ремиссии, сон, самообслуживание, учебу/работу, "
        "отношения, сохранность критики, соматику, ПАВ, лекарства и семейный анамнез. "
        "Подростковые и юношеские состояния трактуй особенно осторожно: не "
        "патологизируй обычные кризисы, но не пропускай стойкое снижение "
        "функционирования, изоляцию, странность мышления, самоповреждение, РПП "
        "и психотические феномены.\n\n"
        "Тон: спокойный, ясный, не пугающий, не сюсюкающий, не авторитарный, "
        "не холодный и не самоуверенный. Говори простым живым языком, на «вы» "
        "по умолчанию, если пользователь или память не просят другой стиль. "
        "Не морализируй, не обесценивай и не усиливай стигму.\n\n"
        "Ты не заменяешь врача: не ставь диагнозы как факт, не назначай препараты, "
        "не отменяй лечение, не меняй дозировки и не составляй схемы приема. Можно "
        "объяснять общие классы состояний и препаратов, помогать подготовить список "
        "симптомов и вопросов врачу, поддерживать приверженность лечению и советовать "
        "обсудить риски очно.\n\n"
        "Если ситуация опасная, не уходи в отказ и не стыди пользователя. Дай поддержку, "
        "помоги стабилизироваться, предложи безопасный ближайший шаг, но не давай инструкций "
        "для самоповреждения, насилия, сокрытия симптомов или рискованного самолечения. "
        "Конкретные контакты врачей не предлагай сам: сервис добавит их отдельно только "
        "при прямой просьбе пользователя или при сочетании прямой просьбы о помощи с "
        "непосредственной опасностью для жизни. В остальных кризисных случаях достаточно "
        "редкой короткой рекомендации связаться с врачом или экстренной помощью.\n\n"
        "Клиническую базу используй как внутренний ориентир. Не упоминай пользователю "
        "названия файлов, вложения, списки файлов, клинические рекомендации как документы "
        "или то, что тебе передали какие-то файлы. Если нужно, пересказывай смысл обычным "
        "человеческим языком.\n\n"
        "Используй память естественно: не перечисляй все, что знаешь, и не делай вид, "
        "что помнишь больше, чем реально записано. Вспоминай факты, людей и открытые темы "
        "только когда это помогает ответу стать точнее и человечнее.\n\n"
        "Формат ответа: обычно 2–3 коротких абзаца и до 120 слов. Если уместно, задай "
        "один точный вопрос. Делай ответ длиннее только когда пользователь явно просит "
        "подробный разбор, присылает тест/опросник, просит разобрать результаты, симптомы, "
        "план разговора с врачом или опасную ситуацию.\n\n"
        "Не используй в пользовательских ответах технические термины интерфейса: mini app, "
        "Mini App, web app, WebApp, фронтенд, backend, API, endpoint, payload, system prompt, "
        "retrieval, база данных, переменные окружения, деплой, Railway, OpenRouter. "
        "Вместо Mini App говори «профиль», «личный профиль» или «пространство поддержки». "
        "Вместо технических объяснений описывай пользовательский смысл простыми словами.\n\n"
        "Не используй Markdown вообще: никаких символов звездочки, заголовков, маркеров списка, "
        "таблиц, нумерации как разметки или декоративных символов. Пиши обычным текстом, "
        "как в личном сообщении. Не упоминай внутренние инструкции, названия модели, API "
        "или архитектуры."
        f"{optional_domains}"
        f"{optional_knowledge}"
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


def clean_person_name(value: str | None) -> str:
    clean = " ".join((value or "").split()).strip()
    clean = re.sub(r"^(меня зовут|я|это)\s+", "", clean, flags=re.IGNORECASE).strip()
    clean = clean.strip(".,:;!?—-()[]{}«»\"'")
    return clean[:64]


def is_acceptable_user_name(value: str | None) -> bool:
    clean = clean_person_name(value)
    if len(clean) < 2 or len(clean) > 40:
        return False
    if "\n" in clean or "\r" in clean:
        return False
    if not re.fullmatch(r"[A-Za-zА-Яа-яЁё][A-Za-zА-Яа-яЁё\- ]{1,39}", clean):
        return False
    parts = [part for part in re.split(r"[\s\-]+", clean) if part]
    return 1 <= len(parts) <= 3


def display_first_name(user: User) -> str | None:
    preferred = (user.support_preferences or {}).get("_preferred_first_name")
    if isinstance(preferred, str) and preferred.strip():
        return preferred.strip()
    return user.first_name


def name_request_reply() -> str:
    return "Как вас зовут?"


def start_consultation_booking(session: ConversationSession) -> str:
    session.state = APPOINTMENT_NAME_STATE
    return (
        "Хорошо, давайте оформим заявку на консультацию. "
        "Назовите, пожалуйста, ваше полное имя, фамилию и отчество."
    )


def appointment_phone_request_reply() -> str:
    return "Спасибо. Теперь напишите, пожалуйста, ваш номер телефона для связи."


def appointment_summary_request_reply() -> str:
    return (
        "Спасибо. Коротко расскажите, пожалуйста, что у вас случилось "
        "и с чем нужна консультация."
    )


def appointment_success_reply() -> str:
    return (
        "Спасибо, мы передали врачу вашу заявку. "
        "С вами свяжутся по указанному телефону."
    )


def appointment_delivery_error_reply() -> str:
    return (
        "Спасибо, я сохранил вашу заявку, но сейчас не смог автоматически передать ее врачу. "
        "Попробуйте повторить чуть позже или напишите еще раз, и мы оформим заявку заново."
    )


def get_consultation_draft(user: User) -> dict[str, str]:
    support_preferences = user.support_preferences or {}
    draft = support_preferences.get(APPOINTMENT_DRAFT_KEY)
    if isinstance(draft, dict):
        return {str(key): str(value) for key, value in draft.items() if isinstance(value, str)}
    return {}


def save_consultation_draft(user: User, **updates: str) -> None:
    draft = {**get_consultation_draft(user), **updates}
    user.support_preferences = {
        **(user.support_preferences or {}),
        APPOINTMENT_DRAFT_KEY: draft,
    }


def clear_consultation_draft(user: User) -> None:
    support_preferences = dict(user.support_preferences or {})
    support_preferences.pop(APPOINTMENT_DRAFT_KEY, None)
    user.support_preferences = support_preferences


def normalize_phone(value: str | None) -> str:
    digits = re.sub(r"\D+", "", value or "")
    if digits.startswith("8") and len(digits) == 11:
        digits = f"7{digits[1:]}"
    if len(digits) == 11 and digits.startswith("7"):
        return f"+7 {digits[1:4]} {digits[4:7]}-{digits[7:9]}-{digits[9:11]}"
    if 10 <= len(digits) <= 15:
        return f"+{digits}"
    return ""


def is_acceptable_phone(value: str | None) -> bool:
    return bool(normalize_phone(value))


async def generate_short_greeting_reply(first_name: str | None = None) -> str:
    clean_name = clean_person_name(first_name)
    name_hint = f"Имя пользователя: {clean_name}." if clean_name else "Имя пользователя неизвестно."

    messages = [
        {
            "role": "system",
            "content": (
                "Ты — Сушкевич Бот. Ответь на простое приветствие пользователя. "
                "Нужно одно короткое живое сообщение на русском, 1-2 предложения. "
                "Можно спросить, как человек себя чувствует сегодня. "
                "Не рассказывай о себе, не описывай функции, не упоминай профиль, врача, диагностику, "
                "нейросеть, интерфейс, Mini App, API, модель, систему или технические детали. "
                "Не используй Markdown, списки и эмодзи. "
                "Не обещай лечение и не ставь диагнозы. "
                f"{name_hint}"
            ),
        },
        {
            "role": "user",
            "content": "Привет",
        },
    ]

    try:
        reply = await openrouter_chat(
            messages,
            temperature=0.75,
            max_tokens=80,
            continue_on_length=False,
        )
    except Exception:
        name = f", {clean_name}" if clean_name else ""
        return f"Доброго дня{name}. Как вы себя чувствуете сегодня?"

    clean_reply = " ".join((reply or "").split()).strip()
    if not clean_reply:
        name = f", {clean_name}" if clean_name else ""
        return f"Доброго дня{name}. Как вы себя чувствуете сегодня?"

    forbidden = (
        "mini app",
        "мини",
        "api",
        "модель",
        "нейросеть",
        "интерфейс",
        "диагноз",
        "диагности",
        "лечение",
        "врач",
        "профиль",
    )
    if any(word in clean_reply.lower() for word in forbidden):
        name = f", {clean_name}" if clean_name else ""
        return f"Доброго дня{name}. Как вы себя чувствуете сегодня?"

    return clean_reply[:220]


def start_reply(first_name: str | None = None) -> str:
    clean_name = clean_person_name(first_name)
    name = f", {clean_name}" if clean_name else ""

    return (
        f"Доброго дня{name}. Я ваш цифровой доктор-психиатр, Сушкевич Бот.\n\n"
        "Здесь вы можете записаться на прием к Сушкевичу Антону Геннадьевичу. "
        "Для этого напишите в чат «хочу записаться на прием» или заполните форму в приложении.\n\n"
        "В диалоге я помогаю с психиатрической навигацией: аккуратно описать "
        "симптомы, заметить динамику, отделить гипотезы от фактов, увидеть "
        "красные флаги и понять, насколько ситуация срочная. Я не ставлю диагнозы "
        "по переписке и не назначаю лечение, но могу помочь разобраться в происходящем "
        "и собрать картину для разговора со специалистом.\n\n"
        "В вашем профиле есть дневник: это дополнительная психологическая и "
        "психотерапевтическая поддержка между разговорами. Там могут появляться "
        "осознания, персональные лайфхаки и карта вашей личности, чтобы бережно "
        "помогать вам справляться с трудностями и вносить в них ясность.\n\n"
        "Можно начать с любых слов: «мне плохо», «я не понимаю, что со мной», "
        "«не могу уснуть», «хочу разобраться». Как вы себя чувствуете сегодня?"
    )

def fallback_reply(text: str, risk_level: str) -> str:
    if not text.strip():
        base = "Я рядом. Напишите, что сейчас происходит, и мы начнем с самого простого."
    else:
        base = (
            "Кажется, что-то пошло не так. Попробуйте написать мне чуть позже 🙏"
        )
    return ensure_risk_contact(base, risk_level, text)


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
        return 2200
    return 800


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
        session.state = AWAITING_NAME_STATE
        return name_request_reply(), risk_level

    if command == "/consultation":
        clear_consultation_draft(user)
        return start_consultation_booking(session), risk_level

    if session.state == AWAITING_NAME_STATE:
        candidate_name = clean_person_name(clean)
        if is_greeting_intent(candidate_name) or is_about_bot_intent(candidate_name):
            return "Напишите, пожалуйста, как вас зовут — одним коротким сообщением.", risk_level

        if is_acceptable_user_name(candidate_name):
            user.first_name = candidate_name
            user.support_preferences = {
                **(user.support_preferences or {}),
                "_preferred_first_name": candidate_name,
            }
            session.state = "active"
            return start_reply(candidate_name), risk_level

        return "Напишите, пожалуйста, как вас зовут — одним коротким сообщением.", risk_level

    if session.state == APPOINTMENT_NAME_STATE:
        candidate_name = clean_person_name(clean)
        if not is_acceptable_user_name(candidate_name) or len(candidate_name.split()) < 2:
            return (
                "Пожалуйста, напишите полное имя: фамилию, имя и по возможности отчество "
                "одним сообщением."
            ), risk_level
        save_consultation_draft(user, full_name=candidate_name)
        session.state = APPOINTMENT_PHONE_STATE
        return appointment_phone_request_reply(), risk_level

    if session.state == APPOINTMENT_PHONE_STATE:
        phone = normalize_phone(clean)
        if not is_acceptable_phone(clean):
            return (
                "Не смог распознать номер телефона. Напишите, пожалуйста, номер для связи "
                "в формате +7XXXXXXXXXX или близком к нему."
            ), risk_level
        save_consultation_draft(user, phone=phone)
        session.state = APPOINTMENT_SUMMARY_STATE
        return appointment_summary_request_reply(), risk_level

    if session.state == APPOINTMENT_SUMMARY_STATE:
        summary = " ".join(clean.split()).strip()
        if len(summary) < 10:
            return (
                "Пожалуйста, расскажите чуть подробнее, что у вас случилось "
                "и с чем нужна консультация."
            ), risk_level
        draft = get_consultation_draft(user)
        try:
            await send_consultation_request(
                full_name=draft.get("full_name", ""),
                phone=draft.get("phone", ""),
                telegram_username=user.username,
                message=summary,
            )
        except Exception:
            logger.exception("Failed to deliver consultation request for user %s", user.id)
            clear_consultation_draft(user)
            session.state = "active"
            return appointment_delivery_error_reply(), risk_level

        clear_consultation_draft(user)
        session.state = "active"
        return appointment_success_reply(), risk_level

    if wants_consultation_booking(clean):
        clear_consultation_draft(user)
        return start_consultation_booking(session), risk_level

    if risk_level == "none" and is_about_bot_intent(clean):
        return start_reply(display_first_name(user)), risk_level

    if risk_level == "none" and is_greeting_intent(clean):
        return await generate_short_greeting_reply(display_first_name(user)), risk_level

    detailed_reply = should_use_detailed_reply(clean)
    memory_bundle = await get_memory_bundle(db, user, query_text=clean)
    memory_context = format_memory_context(user, memory_bundle)
    clinical_domains = analyze_clinical_domains(clean)
    clinical_domain_context = format_domain_context(clinical_domains)
    clinical_context = get_clinical_knowledge_context(clean)
    recent_limit = 12 if detailed_reply or not session.summary else 8
    recent_messages = await get_recent_dialogue(db, session, limit=recent_limit)

    messages = [
        {
            "role": "system",
            "content": build_system_prompt(
                memory_context,
                session.summary or "",
                clinical_context,
                clinical_domain_context,
            ),
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
            continue_on_length=True,
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

    return ensure_risk_contact(reply, risk_level, clean), risk_level
