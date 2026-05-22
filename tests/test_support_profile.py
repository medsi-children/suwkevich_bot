from app.models.message import Message
from app.models.user import User
from app.services import support_profile


def _user() -> User:
    return User(telegram_id=123, first_name="Антон", support_preferences={})


def test_low_context_metrics_are_empty_placeholders() -> None:
    metrics = support_profile._build_metrics(
        user=_user(),
        facts=[],
        people=[],
        topics=[],
        memories=[],
        messages=[],
    )

    assert len(metrics) == len(support_profile.DIMENSIONS)
    assert {metric["value"] for metric in metrics} == {None}
    assert all(metric["empty"] is True for metric in metrics)
    assert all(metric["hint"] == support_profile.LOW_CONTEXT_HINT for metric in metrics)


def test_metrics_fill_only_dimensions_with_evidence() -> None:
    messages = [
        Message(role="user", content="Я хочу понять следующий шаг", message_metadata={})
        for _ in range(5)
    ]

    metrics = support_profile._build_metrics(
        user=_user(),
        facts=[],
        people=[],
        topics=[],
        memories=[],
        messages=messages,
    )
    by_key = {metric["key"]: metric for metric in metrics}

    assert isinstance(by_key["agency"]["value"], int)
    assert by_key["body_contact"]["value"] is None
    assert by_key["body_contact"]["empty"] is True


def test_lifehacks_are_empty_when_context_is_too_small() -> None:
    cards = support_profile._build_lifehacks(_user(), latest_update=None)

    assert cards == []


def test_lifehacks_are_read_from_cache_only() -> None:
    user = _user()
    support_profile.cache_support_profile_items(
        user,
        lifehacks=[
            {"title": "Пауза", "text": "Не отвечать сразу.", "action": "Вернуться позже."},
            {"title": "Сон", "text": "Отметить время сна.", "action": "Записать утром."},
            {"title": "Граница", "text": "Назвать одну просьбу.", "action": "Сказать коротко."},
        ],
        insights=[],
    )

    cards = support_profile._build_lifehacks(user, latest_update=None)

    assert len(cards) == 3
    assert cards[0]["title"] == "Пауза"


def test_lifehacks_reject_technical_roleplay() -> None:
    user = _user()
    support_profile.cache_support_profile_items(
        user,
        lifehacks=[
            {"title": "IDE-пинг", "text": "Открой редактор.", "action": "Создай файл."},
            {"title": "Debug", "text": "Напиши JS-массив.", "action": "Проверь код."},
            {"title": "Мем", "text": "Сделай комментарий.", "action": "Вставь в проект."},
        ],
        insights=[],
    )

    assert support_profile._build_lifehacks(user, latest_update=None) == []


def test_insights_ignore_event_history_when_no_cache_or_insight_memories() -> None:
    insights = support_profile._build_insights(
        user=_user(),
        memories=[],
        latest_update=None,
    )

    assert insights == []


def test_insights_reject_advice_cards() -> None:
    cleaned = support_profile._clean_insights(
        [
            {
                "title": "Пауза перед ответом",
                "text": "Попробуйте записать одну нейтральную формулировку.",
                "tone": "growth",
            }
        ]
    )

    assert cleaned == []


def test_insights_accept_user_realizations() -> None:
    cleaned = support_profile._clean_insights(
        [
            {
                "title": "Меньше автоматизма",
                "text": "Вы заметили, что чаще отделяете свою реакцию от ожиданий других людей.",
                "tone": "growth",
            }
        ]
    )

    assert cleaned == [
        {
            "title": "Меньше автоматизма",
            "text": "Вы заметили, что чаще отделяете свою реакцию от ожиданий других людей.",
            "tone": "growth",
        }
    ]
