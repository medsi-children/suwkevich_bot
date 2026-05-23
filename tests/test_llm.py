import httpx
import pytest

from app.services import llm


def test_normalizes_openrouter_key_with_bearer_prefix() -> None:
    assert llm._normalize_openrouter_api_key("  Bearer sk-test  ") == "sk-test"
    assert llm._normalize_openrouter_api_key('"sk-test"') == "sk-test"


def test_header_title_is_ascii_safe() -> None:
    assert llm._ascii_header_value("Сушкевич Бот", fallback="Sushkevich Bot") == "Sushkevich Bot"


def test_clean_generated_text_removes_markdown_artifacts() -> None:
    text = llm.clean_generated_text("**Как использовать**\n- **Важно:** ответ без звездочек")

    assert "**" not in text
    assert text == "Как использовать\nВажно: ответ без звездочек"


@pytest.mark.asyncio
async def test_openrouter_chat_uses_normalized_key_and_reports_http_error(monkeypatch) -> None:
    captured_headers: dict[str, str] = {}

    class FakeClient:
        def __init__(self, *, timeout: int) -> None:
            self.timeout = timeout

        async def __aenter__(self) -> "FakeClient":
            return self

        async def __aexit__(self, *args: object) -> None:
            return None

        async def post(
            self,
            url: str,
            *,
            headers: dict[str, str],
            json: dict,
        ) -> httpx.Response:
            captured_headers.update(headers)
            request = httpx.Request("POST", url)
            return httpx.Response(401, json={"error": "bad key"}, request=request)

    monkeypatch.setattr(llm.settings, "openrouter_api_key", "Bearer sk-test")
    monkeypatch.setattr(llm.httpx, "AsyncClient", FakeClient)

    with pytest.raises(llm.LlmUnavailableError, match="OpenRouter HTTP 401"):
        await llm.openrouter_chat([{"role": "user", "content": "Привет"}])

    assert captured_headers["Authorization"] == "Bearer sk-test"
    assert captured_headers["X-Title"] == "Sushkevich Bot"


@pytest.mark.asyncio
async def test_openrouter_chat_continues_when_model_hits_length_limit(monkeypatch) -> None:
    requests: list[dict] = []

    class FakeResponse:
        def __init__(self, payload: dict) -> None:
            self._payload = payload

        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict:
            return self._payload

    class FakeClient:
        def __init__(self, *, timeout: int, http2: bool | None = None) -> None:
            self.timeout = timeout
            self.http2 = http2

        async def post(
            self,
            url: str,
            *,
            headers: dict[str, str],
            json: dict,
        ) -> FakeResponse:
            requests.append(json)
            if len(requests) == 1:
                return FakeResponse(
                    {
                        "choices": [
                            {
                                "message": {"content": "Первый фрагмент ответа"},
                                "finish_reason": "length",
                            }
                        ]
                    }
                )
            return FakeResponse(
                {
                    "choices": [
                        {
                            "message": {"content": "второй фрагмент без повтора."},
                            "finish_reason": "stop",
                        }
                    ]
                }
            )

    llm._OPENROUTER_CLIENT = None
    monkeypatch.setattr(llm.settings, "openrouter_api_key", "sk-test")
    monkeypatch.setattr(llm.httpx, "AsyncClient", FakeClient)

    reply = await llm.openrouter_chat(
        [{"role": "user", "content": "Привет"}],
        continue_on_length=True,
        max_continuations=1,
    )

    assert reply == "Первый фрагмент ответа\n\nвторой фрагмент без повтора."
    assert len(requests) == 2
    assert requests[1]["messages"][-1]["content"] == llm.CONTINUATION_PROMPT
