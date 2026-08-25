"""Model pricing registry and cost estimation.

Prices are USD per 1M tokens (input, output) and reflect public list pricing.
Free tiers (:free suffix on OpenRouter) and local Ollama models cost $0.

Override or extend per deployment via the ``PRICE_OVERRIDES_JSON`` env var::

    PRICE_OVERRIDES_JSON='{"my-model": {"input": 0.5, "output": 1.5}}'
"""
from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ModelPrice:
    input_per_million: float
    output_per_million: float


# Substring keys are matched against the model id (case-insensitive).
# More specific entries should be matched first - keep the list ordered.
MODEL_PRICES: list[tuple[str, ModelPrice]] = [
    # --- OpenAI ---
    ("gpt-4o-mini", ModelPrice(0.15, 0.60)),
    ("gpt-4o", ModelPrice(2.50, 10.00)),
    ("gpt-4-turbo", ModelPrice(10.00, 30.00)),
    ("gpt-4.1-mini", ModelPrice(0.40, 1.60)),
    ("gpt-4.1", ModelPrice(2.00, 8.00)),
    ("o3-mini", ModelPrice(1.10, 4.40)),
    ("o4-mini", ModelPrice(1.10, 4.40)),
    # --- Anthropic (via OpenRouter etc.) ---
    ("claude-3-5-sonnet", ModelPrice(3.00, 15.00)),
    ("claude-3-7-sonnet", ModelPrice(3.00, 15.00)),
    ("claude-sonnet-4", ModelPrice(3.00, 15.00)),
    ("claude-3-haiku", ModelPrice(0.25, 1.25)),
    ("claude-3-5-haiku", ModelPrice(0.80, 4.00)),
    ("claude-opus-4", ModelPrice(15.00, 75.00)),
    # --- Google Gemini ---
    ("gemini-2.0-flash-lite", ModelPrice(0.075, 0.30)),
    ("gemini-2.0-flash", ModelPrice(0.10, 0.40)),
    ("gemini-2.5-flash-lite", ModelPrice(0.10, 0.40)),
    ("gemini-2.5-flash", ModelPrice(0.30, 2.50)),
    ("gemini-2.5-pro", ModelPrice(1.25, 10.00)),
    ("gemini-1.5-flash", ModelPrice(0.075, 0.30)),
    ("gemini-1.5-pro", ModelPrice(1.25, 5.00)),
    # --- Meta Llama (hosted) ---
    ("llama-3.3-70b", ModelPrice(0.59, 0.79)),      # Groq list price
    ("llama-3.1-70b", ModelPrice(0.59, 0.79)),
    ("llama-3.1-8b", ModelPrice(0.05, 0.08)),
    ("llama-3.3-8b", ModelPrice(0.05, 0.08)),
    ("llama-4-scout", ModelPrice(0.11, 0.34)),
    ("llama-4-maverick", ModelPrice(0.17, 0.51)),
    # --- Mistral ---
    ("mistral-large", ModelPrice(2.00, 6.00)),
    ("mistral-small", ModelPrice(0.20, 0.60)),
    ("mixtral-8x7b", ModelPrice(0.54, 0.54)),
    # --- DeepSeek / Qwen ---
    ("deepseek-chat", ModelPrice(0.27, 1.10)),
    ("deepseek-r1", ModelPrice(0.55, 2.19)),
    ("qwen-2.5-72b", ModelPrice(0.35, 0.40)),
    ("qwen3-32b", ModelPrice(0.29, 0.59)),
]

# Local models never cost money regardless of name.
FREE_PROVIDER_HINTS = ("ollama",)


def _load_overrides() -> dict[str, ModelPrice]:
    raw = os.getenv("PRICE_OVERRIDES_JSON", "").strip()
    if not raw:
        return {}
    try:
        parsed = json.loads(raw)
        return {
            key.lower(): ModelPrice(entry["input"], entry["output"])
            for key, entry in parsed.items()
            if isinstance(entry, dict) and "input" in entry and "output" in entry
        }
    except (json.JSONDecodeError, KeyError, TypeError) as exc:
        logger.warning("Ignoring malformed PRICE_OVERRIDES_JSON: %s", exc)
        return {}


_OVERRIDES = _load_overrides()


def find_price(provider: str, model: str) -> ModelPrice | None:
    """Look up pricing for a model; returns None when unknown."""
    provider_lower = (provider or "").lower()
    model_lower = (model or "").lower()

    if any(hint in provider_lower for hint in FREE_PROVIDER_HINTS):
        return ModelPrice(0.0, 0.0)
    if ":free" in model_lower:
        return ModelPrice(0.0, 0.0)

    # Explicit overrides win first (exact key match).
    if model_lower in _OVERRIDES:
        return _OVERRIDES[model_lower]

    for key, price in MODEL_PRICES:
        if key in model_lower:
            return price
    return None


def estimate_cost(
    provider: str,
    model: str,
    prompt_tokens: int | None,
    completion_tokens: int | None,
) -> float | None:
    """Estimated USD cost of one call. None when the model price is unknown."""
    if not prompt_tokens and not completion_tokens:
        return None
    price = find_price(provider, model)
    if price is None:
        return None
    cost = (
        (prompt_tokens or 0) / 1_000_000 * price.input_per_million
        + (completion_tokens or 0) / 1_000_000 * price.output_per_million
    )
    return round(cost, 6)


def price_catalog() -> dict[str, dict[str, float]]:
    """Expose the known catalog (for docs/UI)."""
    catalog = {key: {"input": p.input_per_million, "output": p.output_per_million} for key, p in MODEL_PRICES}
    catalog.update({key: {"input": p.input_per_million, "output": p.output_per_million} for key, p in _OVERRIDES.items()})
    return dict(sorted(catalog.items()))
