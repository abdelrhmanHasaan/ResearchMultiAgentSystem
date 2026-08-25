"""LLM provider registry and factory.

Usage::

    from app.services.llm import get_llm, describe_providers

    llm = get_llm()                       # auto-selects best configured provider
    llm = get_llm("groq")                 # force a specific provider
    text = llm.generate("...", json_mode=True)
"""
from __future__ import annotations

import logging
from functools import lru_cache
from typing import Any

from app.core.config import settings
from app.services.llm.base import LLMError, LLMProvider, extract_json  # noqa: F401 (re-exported)
from app.services.llm.gemini_provider import GeminiProvider
from app.services.llm.ollama_provider import OllamaProvider
from app.services.llm.openai_compatible import OpenAICompatibleProvider

logger = logging.getLogger(__name__)

_AUTO_PRIORITY = ("openrouter", "groq", "openai", "gemini", "ollama")


@lru_cache(maxsize=1)
def _build_providers() -> dict[str, LLMProvider]:
    providers: dict[str, LLMProvider] = {}
    for name, cfg in settings.provider_settings().items():
        providers[name] = OpenAICompatibleProvider(
            name=cfg.name,
            api_key=cfg.api_key,
            base_url=cfg.base_url,
            model=cfg.model,
            timeout=settings.llm_timeout_seconds,
            extra_headers=(
                # OpenRouter attribution headers (recommended, optional elsewhere).
                {"HTTP-Referer": "http://localhost:3000", "X-Title": "Autonomous Research Platform"}
                if name == "openrouter"
                else None
            ),
        )
    if settings.gemini_configured():
        providers["gemini"] = GeminiProvider(
            settings.gemini_api_key,
            settings.gemini_model,
            timeout=settings.llm_timeout_seconds,
        )
    else:
        providers.setdefault(
            "gemini",
            GeminiProvider("", settings.gemini_model, timeout=settings.llm_timeout_seconds),
        )
    return providers


def list_providers() -> dict[str, LLMProvider]:
    return _build_providers()


def resolve_provider_name(preferred: str | None = None) -> str:
    """Pick a usable provider: explicit choice > settings > first configured."""
    providers = _build_providers()
    wanted = (preferred or settings.llm_provider or "auto").lower()

    if wanted != "auto" and wanted in providers:
        if providers[wanted].is_configured():
            return wanted
        logger.warning("Requested provider '%s' is not available; falling back.", wanted)

    for candidate in [c for c in _AUTO_PRIORITY if c in providers]:
        if providers[candidate].is_configured():
            if wanted != "auto":
                logger.info("Falling back from '%s' to '%s'.", wanted, candidate)
            return candidate

    raise LLMError(
        "No LLM provider is available. Configure an API key (OPENROUTER_API_KEY, GROQ_API_KEY, "
        "OPENAI_API_KEY, GEMINI_API_KEY) in backend/.env or start Ollama locally."
    )


def get_llm(preferred: str | None = None) -> LLMProvider:
    """Return a ready-to-use provider instance."""
    name = resolve_provider_name(preferred)
    provider = _build_providers()[name]
    logger.debug("Using LLM provider: %s (%s)", provider.name, provider.model_name)
    return provider


def describe_providers() -> list[dict[str, Any]]:
    """Health-report friendly summary of every known provider."""
    result = []
    active = None
    try:
        active = resolve_provider_name()
    except LLMError:
        pass
    for name in _AUTO_PRIORITY:
        provider = _build_providers().get(name)
        if provider is None:
            continue
        info = provider.describe()
        info["active"] = name == active
        result.append(info)
    return result


def reset_registry() -> None:
    """Clear cached instances (used by tests)."""
    _build_providers.cache_clear()
