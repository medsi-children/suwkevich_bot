from app.services.dialogue import (
    DOCTOR_CONTACT,
    build_system_prompt,
    detect_risk_level,
    ensure_risk_contact,
    reply_token_budget,
    should_use_detailed_reply,
)


def test_detects_crisis_language() -> None:
    assert detect_risk_level("Я не хочу жить и думаю о самоубийстве") == "crisis"


def test_adds_doctor_contact_for_crisis() -> None:
    reply = ensure_risk_contact("Я рядом. Давайте сначала снизим риск.", "crisis")
    assert DOCTOR_CONTACT in reply
    assert "свяжитесь с врачом" in reply.lower()


def test_does_not_add_contact_for_regular_dialogue() -> None:
    reply = ensure_risk_contact("Похоже, вы устали.", "none")
    assert DOCTOR_CONTACT not in reply


def test_system_prompt_keeps_regular_replies_short() -> None:
    prompt = build_system_prompt()
    assert "2–3 коротких абзаца" in prompt
    assert "до 120 слов" in prompt


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
