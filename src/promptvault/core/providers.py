"""LLM provider adapters for evaluation."""

import time
from abc import ABC, abstractmethod

import httpx

from promptvault.config import settings


class LLMProvider(ABC):
    """Base class for LLM providers."""

    @abstractmethod
    def generate(
        self,
        prompt: str,
        model: str,
        temperature: float = 0.0,
        max_tokens: int = 512,
    ) -> dict:
        """Generate a response from the LLM.

        Returns:
            dict with keys: content, token_usage, latency_ms
        """
        pass


class OpenAIProvider(LLMProvider):
    """OpenAI API provider."""

    def generate(
        self,
        prompt: str,
        model: str = "gpt-4o-mini",
        temperature: float = 0.0,
        max_tokens: int = 512,
    ) -> dict:
        from openai import OpenAI

        client = OpenAI(api_key=settings.openai_api_key)
        start_time = time.time()

        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens,
        )

        latency_ms = int((time.time() - start_time) * 1000)
        usage = response.usage

        return {
            "content": response.choices[0].message.content or "",
            "token_usage": {
                "prompt_tokens": usage.prompt_tokens if usage else 0,
                "completion_tokens": usage.completion_tokens if usage else 0,
                "total_tokens": usage.total_tokens if usage else 0,
            },
            "latency_ms": latency_ms,
        }


class AnthropicProvider(LLMProvider):
    """Anthropic API provider."""

    def generate(
        self,
        prompt: str,
        model: str = "claude-3-5-sonnet-20241022",
        temperature: float = 0.0,
        max_tokens: int = 512,
    ) -> dict:
        from anthropic import Anthropic

        client = Anthropic(api_key=settings.anthropic_api_key)
        start_time = time.time()

        response = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[{"role": "user", "content": prompt}],
        )

        latency_ms = int((time.time() - start_time) * 1000)

        return {
            "content": response.content[0].text if response.content else "",
            "token_usage": {
                "prompt_tokens": response.usage.input_tokens,
                "completion_tokens": response.usage.output_tokens,
                "total_tokens": response.usage.input_tokens
                + response.usage.output_tokens,
            },
            "latency_ms": latency_ms,
        }


class OllamaProvider(LLMProvider):
    """Ollama-compatible local endpoint provider."""

    def generate(
        self,
        prompt: str,
        model: str = "llama3.2",
        temperature: float = 0.0,
        max_tokens: int = 512,
    ) -> dict:
        base_url = settings.ollama_base_url
        start_time = time.time()

        with httpx.Client(timeout=120.0) as client:
            response = client.post(
                f"{base_url}/api/chat",
                json={
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                    "stream": False,
                    "options": {"temperature": temperature, "num_predict": max_tokens},
                },
            )
            response.raise_for_status()
            data = response.json()

        latency_ms = int((time.time() - start_time) * 1000)

        return {
            "content": data.get("message", {}).get("content", ""),
            "token_usage": {
                "prompt_tokens": data.get("prompt_eval_count", 0),
                "completion_tokens": data.get("eval_count", 0),
                "total_tokens": data.get("prompt_eval_count", 0)
                + data.get("eval_count", 0),
            },
            "latency_ms": latency_ms,
        }


def get_provider(provider_name: str) -> LLMProvider:
    """Get an LLM provider by name."""
    providers = {
        "openai": OpenAIProvider,
        "anthropic": AnthropicProvider,
        "ollama": OllamaProvider,
    }
    provider_class = providers.get(provider_name)
    if not provider_class:
        raise ValueError(
            f"Unknown provider: {provider_name}. "
            f"Available: {', '.join(providers.keys())}"
        )
    return provider_class()
