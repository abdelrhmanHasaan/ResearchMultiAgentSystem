"""Tests for usage accounting persistence."""
from __future__ import annotations

from app.core.database import get_connection
from app.services.llm.base import GenerationResult
from app.services.usage import record_failure, record_usage, usage_since, usage_summary


def _result(**overrides) -> GenerationResult:
    defaults = dict(
        text="hello", provider="openai", model="gpt-4o-mini",
        prompt_tokens=1000, completion_tokens=500, latency_ms=250, stage="writer",
    )
    defaults.update(overrides)
    return GenerationResult(**defaults)


def test_record_usage_persists_and_prices(temp_settings) -> None:
    cost = record_usage(_result())
    # gpt-4o-mini: 0.001 * 0.15 + 0.0005 * 0.60 = 0.00045 USD
    assert cost == 0.00045

    summary = usage_summary()
    assert summary["totals"]["calls"] == 1
    assert summary["totals"]["total_cost_usd"] == 0.00045
    assert summary["by_provider"][0]["model"] == "gpt-4o-mini"
    assert summary["by_stage"][0]["stage"] == "writer"


def test_record_usage_local_model_is_free(temp_settings) -> None:
    cost = record_usage(_result(provider="ollama", model="llama3.1:8b"))
    assert cost == 0.0


def test_unknown_model_records_null_cost(temp_settings) -> None:
    cost = record_usage(_result(provider="acme", model="unknown-x", prompt_tokens=10, completion_tokens=5))
    assert cost is None
    summary = usage_summary()
    assert summary["totals"]["calls"] == 1
    assert summary["recent"][0]["cost_usd"] is None


def test_record_failure_and_error_counting(temp_settings) -> None:
    record_failure("groq", "llama-3.3-70b-versatile", "critic", "HTTP 429")
    summary = usage_summary()
    assert summary["totals"]["errors"] == 1
    assert summary["recent"][0]["status"] == "error"


def test_usage_since_window_filters_old_rows(temp_settings) -> None:
    record_usage(_result())
    # Timestamp far in the past should still include the row; far future excludes it.
    past = usage_since("2000-01-01 00:00:00")
    future = usage_since("2999-01-01 00:00:00")
    assert past["calls"] == 1
    assert future["calls"] == 0
