"""Google Gemini provider using the REST API (no extra SDK dependency)."""
from __future__ import annotations

import logging
import time
from typing import Any

import httpx

from app.services.llm.base import GenerationResult, LLMProvider

logger = logging.getLogger(__name__)

API_ROOT = "https://generativelanguage.googleapis.com/v1beta/models"


class GeminiProvider(LLMProvider):
    def __init__(self, api_key: str, model: str, *, timeout: float = 180.0) -> None:
        self.name = "gemini"
        self.api_key = api_key
        self.model = model
        self.timeout = timeout

    def is_configured(self) -> bool:
        return bool(self.api_key)

    def _generate_full(
        self,
        prompt: str,
        *,
        system: str | None,
        temperature: float,
        max_tokens: int | None,
        json_mode: bool,
    ) -> GenerationResult:
        payload: dict[str, Any] = {
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": temperature},
        }
        if system:
            payload["systemInstruction"] = {"parts": [{"text": system}]}
        if max_tokens:
            payload["generationConfig"]["maxOutputTokens"] = max_tokens
        if json_mode:
            payload["generationConfig"]["responseMimeType"] = "application/json"

        started = time.monotonic()
        with httpx.Client(timeout=self.timeout) as client:
            response = client.post(
                f"{API_ROOT}/{self.model}:generateContent",
                params={"key": self.api_key},
                json=payload,
            )
            if response.status_code >= 400:
                raise RuntimeError(f"HTTP {response.status_code} from Gemini: {response.text[:300]}")
            data = response.json()

        try:
            parts = data["candidates"][0]["content"]["parts"]
            content = "".join(part.get("text", "") for part in parts)
        except (KeyError, IndexError, TypeError) as exc:
            raise RuntimeError(f"Unexpected Gemini response shape: {str(data)[:200]}") from exc

        if not content:
            raise RuntimeError("Empty content from Gemini")

        usage = data.get("usageMetadata") or {}
        return GenerationResult(
            text=content,
            provider=self.name,
            model=self.model,
            prompt_tokens=usage.get("promptTokenCount"),
            completion_tokens=usage.get("candidatesTokenCount"),
            latency_ms=int((time.monotonic() - started) * 1000),
        )
