from app.services.dialogue import DOCTOR_CONTACT, detect_risk_level, ensure_risk_contact


def test_detects_crisis_language() -> None:
    assert detect_risk_level("Я не хочу жить и думаю о самоубийстве") == "crisis"


def test_adds_doctor_contact_for_crisis() -> None:
    reply = ensure_risk_contact("Я рядом. Давайте сначала снизим риск.", "crisis")
    assert DOCTOR_CONTACT in reply
    assert "свяжитесь с врачом" in reply.lower()


def test_does_not_add_contact_for_regular_dialogue() -> None:
    reply = ensure_risk_contact("Похоже, вы устали.", "none")
    assert DOCTOR_CONTACT not in reply
