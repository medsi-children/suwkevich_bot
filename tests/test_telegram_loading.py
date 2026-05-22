from app.api.v1.telegram import pick_loading_message, should_show_loading_message


def test_loading_message_shows_for_regular_text() -> None:
    update = {
        "message": {
            "text": "Мне тревожно, помоги разобраться",
            "from": {"id": 123},
            "chat": {"id": 456},
        }
    }

    assert should_show_loading_message(update) is True


def test_loading_message_skips_commands() -> None:
    update = {
        "message": {
            "text": "/start",
            "from": {"id": 123},
            "chat": {"id": 456},
        }
    }

    assert should_show_loading_message(update) is False


def test_loading_message_uses_supported_variant() -> None:
    update = {
        "message": {
            "text": "Мне тревожно, помоги разобраться",
            "from": {"id": 123},
            "chat": {"id": 456},
        }
    }

    assert pick_loading_message(update) in {
        "<code>Анализируем...</code>",
        "<code>Одну минутку...</code>",
        "<code>Генерируем ответ...</code>",
    }
