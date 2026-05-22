from app.services.memory import _detect_profile_refresh_sections


def test_detects_profile_refresh_sections() -> None:
    assert _detect_profile_refresh_sections("Подготовь мне лайфхаки в профиль") == {"lifehacks"}
    assert _detect_profile_refresh_sections("Обнови осознания в дневнике") == {"insights"}
    assert _detect_profile_refresh_sections("Скорректируй описание профиля") == {"profile_summary"}


def test_detects_full_profile_refresh_request() -> None:
    assert _detect_profile_refresh_sections("Обнови профиль") == {
        "profile_summary",
        "lifehacks",
        "insights",
    }
