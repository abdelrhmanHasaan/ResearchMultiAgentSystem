"""Local Ollama provider (no API key required)."""
from __future__ import annotations

import logging
from typing import Any

import httpx

from app.services.llm.base import LLMProvider

logger = logging.getLogger(__name__)


class OllamaProvider(LLMProvider):
    def __init__(self, base_url: str, model: str, *, timeout: float = 300.0) -> None:
        self.name = "ollama"
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout

    def is_configured(self) -> bool:
        """Ollama counts as configured only when the daemon actually answers."""
        try:
            with httpx.Client(timeout=3.0) as client:
                response = client.get(f"{self.base_url}/api/tags")
                return response.status_code == 200
        except Exception:  # noqa: BLE001
            return False

    def _generate(
        self,
        prompt: str,
        *,
        system: str | None,
        temperature: float,
        max_tokens: int | None,
        json_mode: bool,
    ) -> str:
        messages: list[dict[str, str]] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        payload: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {"temperature": temperature},
        }
        if max_tokens:
            payload["options"]["num_predict"] = max_tokens
        if json_mode:
            payload["format"] = "json"

        with httpx.Client(timeout=self.timeout) as client:
            response = client.post(f"{self.base_url}/api/chat", json=payload)
            if response.status_code >= 400:
                raise RuntimeError(f"HTTP {response.status_code} from Ollama: {response.text[:300]}")
            data = response.json()

        content = data.get("message", {}).get("content", "")
        if not content:
            raise RuntimeError(f"Empty content from Ollama: {str(data)[:200]}")
        return content
