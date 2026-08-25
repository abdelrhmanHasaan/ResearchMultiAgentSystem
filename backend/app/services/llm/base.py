"""Provider-agnostic LLM abstraction.

Every agent talks to an ``LLMProvider`` and never to a vendor SDK directly,
so switching between local models (Ollama) and hosted APIs (OpenRouter,
Groq, OpenAI, Gemini) is purely configuration.
"""
from __future__ import annotations

import json
import logging
import random
import re
import time
from abc import ABC, abstractmethod
from typing import Any

logger = logging.getLogger(__name__)

_JSON_BLOCK_RE = re.compile(r"\{.*\}", re.DOTALL)


class LLMError(RuntimeError):
    """Raised when a provider fails after all retries."""


class LLMProvider(ABC):
    """A chat-completion source."""

    name: str = "base"

    @abstractmethod
    def is_configured(self) -> bool:
        """Whether this provider can currently be used."""

    @abstractmethod
    def _generate(
        self,
        prompt: str,
        *,
        system: str | None,
        temperature: float,
        max_tokens: int | None,
        json_mode: bool,
    ) -> str:
        """Single attempt at generation. Raises on failure."""

    @property
    def model_name(self) -> str:
        return getattr(self, "model", "unknown")

    def describe(self) -> dict[str, Any]:
        return {"provider": self.name, "model": self.model_name, "configured": self.is_configured()}

    # ------------------------------------------------------------------
    # Public API with retry/backoff shared by all providers.
    # ------------------------------------------------------------------
    def generate(
        self,
        prompt: str,
        *,
        system: str | None = None,
        temperature: float = 0.5,
        max_tokens: int | None = None,
        json_mode: bool = False,
        retries: int | None = None,
    ) -> str:
        attempts = retries if retries is not None else 2
        last_error: Exception | None = None
        for attempt in range(attempts + 1):
            try:
                return self._generate(
                    prompt,
                    system=system,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    json_mode=json_mode,
                )
            except Exception as exc:  # noqa: BLE001 - providers raise many types
                last_error = exc
                if attempt < attempts:
                    sleep_for = min(2**attempt + random.random(), 8.0)
                    logger.warning(
                        "%s failed (attempt %d/%d): %s - retrying in %.1fs",
                        self.name,
                        attempt + 1,
                        attempts + 1,
                        exc,
                        sleep_for,
                    )
                    time.sleep(sleep_for)
        raise LLMError(f"Provider '{self.name}' failed after {attempts + 1} attempts: {last_error}") from last_error


def extract_json(text: str) -> dict[str, Any]:
    """Robustly parse a JSON object out of a raw model response."""
    text = (text or "").strip()
    if not text:
        raise ValueError("Empty response")

    # Strip markdown code fences if present.
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)

    try:
        parsed = json.loads(text)
        if isinstance(parsed, dict):
            return parsed
    except json.JSONDecodeError:
        pass

    match = _JSON_BLOCK_RE.search(text)
    if match:
        try:
            parsed = json.loads(match.group(0))
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError:
            pass
    raise ValueError(f"No valid JSON object found in response: {text[:200]!r}")
