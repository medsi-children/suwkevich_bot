from app.services.telegram import DEFAULT_TELEGRAM_COMMANDS


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
