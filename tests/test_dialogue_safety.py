import pytest

from app.models.session import ConversationSession
from app.models.user import User
from app.services.dialogue import (
    APPOINTMENT_NAME_STATE,
    APPOINTMENT_PHONE_STATE,
    APPOINTMENT_SUMMARY_STATE,
    DOCTOR_CONTACT,
    build_system_prompt,
    detect_risk_level,
    ensure_risk_contact,
    handle_user_text,
    normalize_phone,
    reply_token_budget,
    should_use_detailed_reply,
    start_reply,
    wants_consultation_booking,
)
from app.services.telegram import build_consultation_request_text


def test_detects_crisis_language() -> None:
    assert detect_risk_level("Я не хочу жить и думаю о самоубийстве") == "crisis"


def test_adds_general_safety_line_for_crisis_without_contact() -> None:
    reply = ensure_risk_contact(
        "Я рядом. Давайте сначала снизим риск.",
        "crisis",
        "Я не хочу жить",
    )
    assert DOCTOR_CONTACT not in reply
    assert "112" in reply
    assert "хочу записаться на консультацию" in reply.lower()


def test_adds_doctor_contact_when_user_asks_for_contact() -> None:
    reply = ensure_risk_contact(
        "Можно обсудить это со специалистом.",
        "none",
        "Дайте контакт врача",
    )
    assert DOCTOR_CONTACT in reply


def test_adds_doctor_contact_for_crisis_help_request() -> None:
    reply = ensure_risk_contact(
        "Я рядом. Давайте сначала снизим риск.",
        "crisis",
        "Мне нужна помощь, я думаю о самоубийстве",
    )
    assert DOCTOR_CONTACT in reply


def test_does_not_add_contact_for_regular_dialogue() -> None:
    reply = ensure_risk_contact("Похоже, вы устали.", "none", "Мне тревожно")
    assert DOCTOR_CONTACT not in reply


def test_system_prompt_keeps_regular_replies_short() -> None:
    prompt = build_system_prompt()
    assert "2–3 коротких абзаца" in prompt
    assert "до 120 слов" in prompt
    assert "названия файлов" in prompt
    assert "не диагноз по переписке" in prompt
    assert "суицидальность и самоповреждение" in prompt


def test_detailed_reply_detection_for_tests_and_symptoms() -> None:
    assert should_use_detailed_reply("Помоги разобрать результаты теста на тревогу") is True
    assert should_use_detailed_reply("Мне тревожно и одиноко") is False


def test_detailed_reply_detection_for_structured_answers() -> None:
    text = (
        "1 - странный вопрос. правильнее спросить, насколько часто "
        "вы чувствуете, что не контролируете жизнь.\n"
        "2 - в целом да\n"
        "3 - порой да и сильно\n"
        "4 - да, но иногда эмоции сильнее\n"
        "5 - да, но с недавних пор"
    )
    assert should_use_detailed_reply(text) is True


def test_reply_token_budget_depends_on_request_shape() -> None:
    assert reply_token_budget("Мне тревожно и одиноко") == 800
    assert reply_token_budget("Помоги составить тест по этим метрикам") == 2200


def test_start_reply_trims_user_name_spacing() -> None:
    reply = start_reply("  Денис ")

    assert "Доброго дня, Денис. Я Сушкевич Бот." in reply
    assert "Доброго дня,   Денис" not in reply


def test_start_reply_separates_navigation_and_diary_support() -> None:
    reply = start_reply()

    assert "записаться на прием к Сушкевичу Антону Геннадьевичу" in reply
    assert "психиатрической навигацией" in reply
    assert "дополнительная психологическая" in reply
    assert "карта вашей личности" in reply
    assert len(reply) < 1200


def test_detects_consultation_booking_intent() -> None:
    assert wants_consultation_booking("Хочу записаться на консультацию") is True
    assert wants_consultation_booking("Можно записаться к психиатру?") is True
    assert wants_consultation_booking("Как записаться?") is True
    assert wants_consultation_booking("Мне тревожно") is False


def test_normalize_phone_formats_russian_number() -> None:
    assert normalize_phone("8 (999) 123-45-67") == "+7 999 123-45-67"


def test_build_consultation_request_text_uses_expected_format() -> None:
    text = build_consultation_request_text(
        full_name="Иванов Иван Иванович",
        phone="+7 999 123-45-67",
        telegram_username="demo_user",
        message="Сильная тревога и бессонница",
    )
    assert "Имя: Иванов Иван Иванович" in text
    assert "Телефон: +7 999 123-45-67" in text
    assert "Телеграм: @demo_user" in text
    assert "Сообщение: Сильная тревога и бессонница" in text


@pytest.mark.asyncio
async def test_handle_user_text_starts_consultation_flow() -> None:
    user = User(first_name="Анна", support_preferences={})
    session = ConversationSession(state="active", source="telegram")

    reply, risk_level = await handle_user_text(
        None,
        user=user,
        session=session,
        text="Хочу записаться на консультацию",
    )

    assert risk_level == "none"
    assert session.state == APPOINTMENT_NAME_STATE
    assert "полное имя" in reply.lower()


@pytest.mark.asyncio
async def test_consultation_command_starts_consultation_flow() -> None:
    user = User(first_name="Анна", support_preferences={})
    session = ConversationSession(state="active", source="telegram")

    reply, risk_level = await handle_user_text(
        None,
        user=user,
        session=session,
        text="/consultation",
    )

    assert risk_level == "none"
    assert session.state == APPOINTMENT_NAME_STATE
    assert "оформим заявку" in reply.lower()


@pytest.mark.asyncio
async def test_handle_user_text_completes_consultation_flow(monkeypatch) -> None:
    deliveries: list[dict[str, str | None]] = []

    async def fake_send_consultation_request(
        *,
        full_name: str,
        phone: str,
        telegram_username: str | None,
        message: str,
    ) -> list[dict[str, object]]:
        deliveries.append(
            {
                "full_name": full_name,
                "phone": phone,
                "telegram_username": telegram_username,
                "message": message,
            }
        )
        return []

    monkeypatch.setattr(
        "app.services.dialogue.send_consultation_request",
        fake_send_consultation_request,
    )

    user = User(username="help_me", support_preferences={})
    session = ConversationSession(state=APPOINTMENT_NAME_STATE, source="telegram")

    reply, _ = await handle_user_text(None, user=user, session=session, text="Иванов Иван Иванович")
    assert session.state == APPOINTMENT_PHONE_STATE
    assert "номер телефона" in reply.lower()

    reply, _ = await handle_user_text(None, user=user, session=session, text="8 (999) 123-45-67")
    assert session.state == APPOINTMENT_SUMMARY_STATE
    assert "что у вас случилось" in reply.lower()

    reply, _ = await handle_user_text(
        None,
        user=user,
        session=session,
        text="У меня усилилась тревога, почти не сплю и нужна консультация.",
    )
    assert session.state == "active"
    assert "передали врачу вашу заявку" in reply.lower()
    assert deliveries == [
        {
            "full_name": "Иванов Иван Иванович",
            "phone": "+7 999 123-45-67",
            "telegram_username": "help_me",
            "message": "У меня усилилась тревога, почти не сплю и нужна консультация.",
        }
    ]
