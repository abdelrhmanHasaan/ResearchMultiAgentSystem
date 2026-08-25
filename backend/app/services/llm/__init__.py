"""LLM provider registry, per-stage routing and failover orchestration.

Usage::

    from app.services.llm import generate_with_failover

    result = generate_with_failover(prompt, stage="writer", json_mode=True)
    text   = result.text          # the completion
    result.provider / result.model / result.prompt_tokens ...

Routing rules (all optional via .env):
    LLM_PROVIDER=auto            global default
    PLANNER_PROVIDER=groq        cheap/fast model for planning
    WRITER_PROVIDER=openrouter   strong model for drafting
    CRITIC_PROVIDER=ollama       free local model for evaluation

If the routed provider errors after its retries, the next configured provider
in fallback order is tried automatically (failover).
"""
from __future__ import annotations

import logging
from functools import lru_cache
from typing import Any

from app.core.config import settings
from app.services.llm.base import (  # noqa: F401 (re-exported)
    GenerationResult,
    LLMError,
    LLMProvider,
    extract_json,
)
from app.services.llm.gemini_provider import GeminiProvider
from app.services.llm.ollama_provider import OllamaProvider
from app.services.llm.openai_compatible import OpenAICompatibleProvider
from app.services.usage import record_failure, record_usage

logger = logging.getLogger(__name__)

_AUTO_PRIORITY = ("openrouter", "groq", "openai", "gemini", "ollama")
_STAGE_ROUTES = {"planner": settings.planner_provider,
                 "writer": settings.writer_provider,
                 "critic": settings.critic_provider}


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
    providers["gemini"] = GeminiProvider(
        settings.gemini_api_key or "",
        settings.gemini_model,
        timeout=settings.llm_timeout_seconds,
    )
    return providers


def list_providers() -> dict[str, LLMProvider]:
    return _build_providers()


def resolve_provider_name(preferred: str | None = None, stage: str | None = None) -> str:
    """Pick a usable provider: stage route > explicit choice > settings > first configured."""
    providers = _build_providers()
    wanted = (
        preferred
        or (_STAGE_ROUTES.get(stage.lower()) if stage else None)
        or settings.llm_provider
        or "auto"
    ).lower()

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


def get_llm(preferred: str | None = None, stage: str | None = None) -> LLMProvider:
    """Return a ready-to-use provider instance."""
    name = resolve_provider_name(preferred, stage)
    provider = _build_providers()[name]
    logger.debug("Using LLM provider: %s (%s)", provider.name, provider.model_name)
    return provider


def _failover_chain(stage: str | None) -> list[LLMProvider]:
    """Ordered list of configured providers: routed one first."""
    chain: list[LLMProvider] = []
    seen: set[str] = set()
    try:
        primary = resolve_provider_name(stage=stage)
        chain.append(_build_providers()[primary])
        seen.add(primary)
    except LLMError:
        pass  # no configured provider at all -> empty chain, caller raises
    for candidate in _AUTO_PRIORITY:
        if candidate not in seen and candidate in _build_providers():
            provider = _build_providers()[candidate]
            if provider.is_configured():
                chain.append(provider)
    return chain


def generate_with_failover(
    prompt: str,
    *,
    stage: str | None = None,
    system: str | None = None,
    temperature: float = 0.5,
    max_tokens: int | None = None,
    json_mode: bool = False,
) -> GenerationResult:
    """Generate with retries inside each provider AND failover across providers.

    Every attempt (success or failure) is recorded into usage accounting.
    """
    chain = _failover_chain(stage)
    if not chain:
        raise LLMError(
            "No LLM provider is available. Configure an API key (OPENROUTER_API_KEY, GROQ_API_KEY, "
            "OPENAI_API_KEY, GEMINI_API_KEY) in backend/.env or start Ollama locally."
        )

    errors: list[str] = []
    for index, provider in enumerate(chain):
        last_chance = index == len(chain) - 1
        try:
            result = provider.generate(
                prompt,
                system=system,
                temperature=temperature,
                max_tokens=max_tokens,
                json_mode=json_mode,
                stage=stage,
                # Keep in-provider retries low when more providers can be tried.
                retries=settings.llm_max_retries if last_chance else min(settings.llm_max_retries, 1),
            )
            cost = record_usage(result)
            if cost is not None:
                logger.info("[%s/%s] cost estimate: $%.6f", provider.name, provider.model, cost)
            return result
        except LLMError as exc:
            errors.append(f"{provider.name}: {exc}")
            record_failure(provider.name, provider.model_name, stage or "unknown", str(exc))
            logger.warning("Failover from '%s' after exhausted retries.", provider.name)

    raise LLMError("All providers failed. Attempts: " + " | ".join(errors))


def describe_providers() -> list[dict[str, Any]]:
    """Health-report friendly summary of every known provider."""
    result = []
    active_by_stage = {stage: _safe_active(route) for stage, route in _STAGE_ROUTES.items()}
    for name in _AUTO_PRIORITY:
        provider = _build_providers().get(name)
        if provider is None:
            continue
        info = provider.describe()
        info["active"] = any(active == name for active in active_by_stage.values())
        info["routed_stages"] = [stage for stage, active in active_by_stage.items() if active == name]
        result.append(info)
    return result


def _safe_active(route: str | None) -> str | None:
    try:
        return resolve_provider_name(route)
    except LLMError:
        return None


def reset_registry() -> None:
    """Clear cached instances (used by tests)."""
    _build_providers.cache_clear()
