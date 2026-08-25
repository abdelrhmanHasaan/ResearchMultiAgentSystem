"""Tests for the pricing registry and cost estimation."""
from __future__ import annotations

from app.services.pricing import estimate_cost, find_price, price_catalog


def test_known_openai_model() -> None:
    price = find_price("openai", "gpt-4o-mini")
    assert price is not None
    assert price.input_per_million == 0.15


def test_free_suffix_models_cost_zero() -> None:
    price = find_price("openrouter", "meta-llama/llama-3.3-70b-instruct:free")
    assert price == find_price("ollama", "anything")  # both free
    assert price is not None and price.input_per_million == 0.0


def test_ollama_always_free() -> None:
    assert find_price("ollama", "llama3.1:70b-weird-name").input_per_million == 0.0


def test_unknown_model_returns_none() -> None:
    assert find_price("acme-cloud", "totally-unknown-model-9000") is None
    assert estimate_cost("acme-cloud", "totally-unknown-model-9000", 1000, 100) is None


def test_estimate_cost_math() -> None:
    # gpt-4o-mini: $0.15 input / $0.60 output per 1M tokens.
    cost = estimate_cost("openai", "gpt-4o-mini", 1_000_000, 500_000)
    assert cost == round(0.15 + 0.30, 6)


def test_estimate_cost_none_without_tokens() -> None:
    assert estimate_cost("openai", "gpt-4o-mini", None, None) is None


def test_price_catalog_exposes_entries() -> None:
    catalog = price_catalog()
    assert "gpt-4o" in catalog
    assert catalog["gpt-4o"]["output"] > 0
