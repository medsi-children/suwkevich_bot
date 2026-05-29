from app.services import telegram
from app.services.telegram import DEFAULT_TELEGRAM_COMMANDS, consultation_request_targets


def test_default_telegram_commands_include_start_and_consultation() -> None:
    assert list(DEFAULT_TELEGRAM_COMMANDS) == [
        {
            "command": "start",
            "description": "Запустить бота и начать диалог",
        },
        {
            "command": "consultation",
            "description": "Оставить заявку на консультацию",
        },
    ]


def test_consultation_request_targets_include_primary_and_extra_targets(monkeypatch) -> None:
    monkeypatch.setattr(telegram.settings, "consultation_requests_chat_username", "@medsi_children")
    monkeypatch.setattr(telegram.settings, "consultation_requests_chat_id", "7659888703")
    monkeypatch.setattr(telegram.settings, "consultation_requests_extra_chat_ids", "1148863826")

    assert consultation_request_targets() == ["@medsi_children", 7659888703, 1148863826]


def test_consultation_request_targets_deduplicate_same_string_target(monkeypatch) -> None:
    monkeypatch.setattr(telegram.settings, "consultation_requests_chat_username", "medsi_children")
    monkeypatch.setattr(telegram.settings, "consultation_requests_chat_id", "@medsi_children")
    monkeypatch.setattr(telegram.settings, "consultation_requests_extra_chat_ids", "")

    assert consultation_request_targets() == ["@medsi_children"]
