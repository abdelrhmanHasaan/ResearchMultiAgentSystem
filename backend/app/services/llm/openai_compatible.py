"""OpenAI-compatible chat provider.

Covers OpenRouter, Groq, OpenAI, Together, DeepSeek, LM Studio, vLLM and
any other endpoint exposing ``/chat/completions``.
"""
from __future__ import annotations

import logging
import time
from typing import Any

import httpx

from app.services.llm.base import GenerationResult, LLMProvider

logger = logging.getLogger(__name__)

JSON_SUPPORTED_HINTS = ("openai", "gpt", "llama-3", "mistral", "qwen", "deepseek")


class OpenAICompatibleProvider(LLMProvider):
    def __init__(
        self,
        name: str,
        api_key: str,
        base_url: str,
        model: str,
        *,
        timeout: float = 180.0,
        extra_headers: dict[str, str] | None = None,
    ) -> None:
        self.name = name
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout
        self.extra_headers = extra_headers or {}

    def is_configured(self) -> bool:
        return bool(self.api_key) and bool(self.base_url) and bool(self.model)

    def _generate_full(
        self,
        prompt: str,
        *,
        system: str | None,
        temperature: float,
        max_tokens: int | None,
        json_mode: bool,
    ) -> GenerationResult:
        messages: list[dict[str, str]] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        payload: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
        }
        if max_tokens:
            payload["max_tokens"] = max_tokens
        if json_mode and any(hint in self.model.lower() for hint in JSON_SUPPORTED_HINTS):
            payload["response_format"] = {"type": "json_object"}

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            **self.extra_headers,
        }

        started = time.monotonic()
        with httpx.Client(timeout=self.timeout) as client:
            response = client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
            )
            if response.status_code >= 400:
                snippet = response.text[:300]
                raise RuntimeError(f"HTTP {response.status_code} from {self.name}: {snippet}")
            data = response.json()

        try:
            content = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise RuntimeError(f"Unexpected response shape from {self.name}: {data}") from exc

        usage = data.get("usage") or {}
        latency_ms = int((time.monotonic() - started) * 1000)
        logger.info(
            "[%s] model=%s prompt_tokens=%s completion_tokens=%s latency=%dms",
            self.name,
            self.model,
            usage.get("prompt_tokens", "?"),
            usage.get("completion_tokens", "?"),
            latency_ms,
        )
        return GenerationResult(
            text=content or "",
            provider=self.name,
            model=self.model,
            prompt_tokens=usage.get("prompt_tokens"),
            completion_tokens=usage.get("completion_tokens"),
            latency_ms=latency_ms,
        )
