"""Tests for provider adapters without external network calls."""

from types import SimpleNamespace

import pytest

from core import providers


def test_openai_provider(monkeypatch):
    response = SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content="answer"))],
        usage=SimpleNamespace(prompt_tokens=3, completion_tokens=2, total_tokens=5),
    )
    completions = SimpleNamespace(create=lambda **_kwargs: response)
    client = SimpleNamespace(chat=SimpleNamespace(completions=completions))
    monkeypatch.setattr("openai.OpenAI", lambda **_kwargs: client)

    result = providers.OpenAIProvider().generate("question", "gpt-4.1-mini")

    assert result["content"] == "answer"
    assert result["token_usage"]["total_tokens"] == 5


def test_anthropic_provider_ignores_non_text_blocks(monkeypatch):
    response = SimpleNamespace(
        content=[SimpleNamespace(thinking="hidden"), SimpleNamespace(text="answer")],
        usage=SimpleNamespace(input_tokens=3, output_tokens=2),
    )
    client = SimpleNamespace(messages=SimpleNamespace(create=lambda **_kwargs: response))
    monkeypatch.setattr("anthropic.Anthropic", lambda **_kwargs: client)

    result = providers.AnthropicProvider().generate("question", "claude-sonnet-5")

    assert result["content"] == "answer"
    assert result["token_usage"]["total_tokens"] == 5


def test_ollama_provider(monkeypatch):
    class Response:
        def raise_for_status(self):
            return None

        def json(self):
            return {
                "message": {"content": "answer"},
                "prompt_eval_count": 3,
                "eval_count": 2,
            }

    class Client:
        def __init__(self, **_kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return None

        def post(self, *_args, **_kwargs):
            return Response()

    monkeypatch.setattr(providers.httpx, "Client", Client)

    result = providers.OllamaProvider().generate("question", "llama3.2")

    assert result["content"] == "answer"
    assert result["token_usage"]["total_tokens"] == 5


def test_gemini_provider(monkeypatch):
    from google import genai

    response = SimpleNamespace(
        text="answer",
        usage_metadata=SimpleNamespace(prompt_token_count=3, candidates_token_count=2),
    )
    client = SimpleNamespace(models=SimpleNamespace(generate_content=lambda **_kwargs: response))
    monkeypatch.setattr(genai, "Client", lambda **_kwargs: client)

    result = providers.GeminiProvider().generate("question", "gemini-2.5-flash")

    assert result["content"] == "answer"
    assert result["token_usage"]["total_tokens"] == 5


@pytest.mark.parametrize(
    ("name", "provider_type"),
    [
        ("openai", providers.OpenAIProvider),
        ("anthropic", providers.AnthropicProvider),
        ("ollama", providers.OllamaProvider),
        ("gemini", providers.GeminiProvider),
    ],
)
def test_get_provider(name, provider_type):
    assert isinstance(providers.get_provider(name), provider_type)


def test_get_provider_rejects_unknown_provider():
    with pytest.raises(ValueError, match="Unknown provider"):
        providers.get_provider("unknown")
