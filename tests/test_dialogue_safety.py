from app.services.dialogue import (
    DOCTOR_CONTACT,
    build_system_prompt,
    detect_risk_level,
    ensure_risk_contact,
    reply_token_budget,
    should_use_detailed_reply,
    start_reply,
)


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

    assert "психиатрической навигацией" in reply
    assert "дополнительная психологическая" in reply
    assert "карта вашей личности" in reply
    assert len(reply) < 1200
