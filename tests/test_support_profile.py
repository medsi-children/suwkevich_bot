import pytest

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


def test_metrics_get_scores_after_enough_dialogue() -> None:
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

    assert all(isinstance(metric["value"], int) for metric in metrics)
    assert all("empty" not in metric for metric in metrics)


@pytest.mark.asyncio
async def test_lifehacks_are_empty_when_context_is_too_small() -> None:
    cards = await support_profile._build_lifehacks(
        user=_user(),
        facts=[],
        topics=[],
        memories=[],
        messages=[],
    )

    assert cards == []


@pytest.mark.asyncio
async def test_lifehacks_do_not_use_generic_fallback_without_openrouter(monkeypatch) -> None:
    messages = [
        Message(role="user", content="Сегодня снова тяжело после разговора", message_metadata={})
        for _ in range(5)
    ]
    monkeypatch.setattr(support_profile.settings, "openrouter_api_key", "")

    cards = await support_profile._build_lifehacks(
        user=_user(),
        facts=[],
        topics=[],
        memories=[],
        messages=messages,
    )

    assert cards == []
