"""LLM usage accounting: every call is persisted with its estimated cost.

Deliberately imports nothing from ``app.services.llm`` to avoid a circular
dependency - callers pass any object exposing ``provider/model/stage/
prompt_tokens/completion_tokens/latency_ms`` attributes.
"""
from __future__ import annotations

import logging
from typing import Any

from app.core.database import get_connection, init_db
from app.services.pricing import estimate_cost

logger = logging.getLogger(__name__)


def record_usage(result: GenerationResult, *, status: str = "ok") -> float | None:
    """Persist one LLM call. Returns the estimated USD cost (None if unknown)."""
    cost = estimate_cost(
        result.provider, result.model, result.prompt_tokens, result.completion_tokens
    )
    try:
        init_db()
        with get_connection() as conn:
            conn.execute(
                """INSERT INTO usage_log
                   (provider, model, stage, prompt_tokens, completion_tokens,
                    total_tokens, cost_usd, latency_ms, status)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    result.provider,
                    result.model,
                    result.stage or "unknown",
                    result.prompt_tokens,
                    result.completion_tokens,
                    result.total_tokens or None,
                    cost,
                    result.latency_ms,
                    status,
                ),
            )
    except Exception:  # noqa: BLE001 - accounting must never break the pipeline
        logger.exception("Failed to record LLM usage")
    return cost


def record_failure(provider: str, model: str, stage: str, error: str) -> None:
    """Record a failed call so dashboards show provider reliability too."""
    try:
        init_db()
        with get_connection() as conn:
            conn.execute(
                """INSERT INTO usage_log
                   (provider, model, stage, prompt_tokens, completion_tokens,
                    total_tokens, cost_usd, latency_ms, status, error)
                   VALUES (?, ?, ?, NULL, NULL, NULL, NULL, NULL, 'error', ?)""",
                (provider, model, stage, error[:500]),
            )
    except Exception:  # noqa: BLE001
        logger.exception("Failed to record LLM failure")


def usage_summary(limit_calls: int = 25) -> dict[str, Any]:
    """Aggregate spend/tokens for the dashboard."""
    init_db()
    with get_connection() as conn:
        totals = conn.execute(
            """SELECT COUNT(*) AS calls,
                      COALESCE(SUM(prompt_tokens), 0) AS prompt_tokens,
                      COALESCE(SUM(completion_tokens), 0) AS completion_tokens,
                      COALESCE(SUM(total_tokens), 0) AS total_tokens,
                      COALESCE(SUM(cost_usd), 0) AS total_cost_usd,
                      COALESCE(AVG(latency_ms), 0) AS avg_latency_ms,
                      SUM(CASE WHEN status = 'error' THEN 1 ELSE 0 END) AS errors
               FROM usage_log"""
        ).fetchone()

        by_provider = conn.execute(
            """SELECT provider, model,
                      COUNT(*) AS calls,
                      COALESCE(SUM(total_tokens), 0) AS total_tokens,
                      COALESCE(SUM(prompt_tokens), 0) AS prompt_tokens,
                      COALESCE(SUM(completion_tokens), 0) AS completion_tokens,
                      COALESCE(SUM(cost_usd), 0) AS total_cost_usd,
                      COALESCE(AVG(latency_ms), 0) AS avg_latency_ms
               FROM usage_log
               GROUP BY provider, model
               ORDER BY total_cost_usd DESC, calls DESC"""
        ).fetchall()

        by_stage = conn.execute(
            """SELECT stage,
                      COUNT(*) AS calls,
                      COALESCE(SUM(total_tokens), 0) AS total_tokens,
                      COALESCE(SUM(cost_usd), 0) AS total_cost_usd
               FROM usage_log
               GROUP BY stage
               ORDER BY total_cost_usd DESC"""
        ).fetchall()

        recent = conn.execute(
            """SELECT id, created_at, provider, model, stage,
                      prompt_tokens, completion_tokens, total_tokens,
                      cost_usd, latency_ms, status
               FROM usage_log ORDER BY id DESC LIMIT ?""",
            (limit_calls,),
        ).fetchall()

    return {
        "totals": {
            "calls": totals["calls"],
            "prompt_tokens": totals["prompt_tokens"],
            "completion_tokens": totals["completion_tokens"],
            "total_tokens": totals["total_tokens"],
            "total_cost_usd": round(totals["total_cost_usd"], 6),
            "avg_latency_ms": round(totals["avg_latency_ms"]),
            "errors": totals["errors"] or 0,
        },
        "by_provider": [dict(row) | {"total_cost_usd": round(row["total_cost_usd"], 6),
                                     "avg_latency_ms": round(row["avg_latency_ms"])} for row in by_provider],
        "by_stage": [dict(row) | {"total_cost_usd": round(row["total_cost_usd"], 6)} for row in by_stage],
        "recent": [
            {
                "id": row["id"],
                "created_at": row["created_at"],
                "provider": row["provider"],
                "model": row["model"],
                "stage": row["stage"],
                "prompt_tokens": row["prompt_tokens"],
                "completion_tokens": row["completion_tokens"],
                "total_tokens": row["total_tokens"],
                "cost_usd": round(row["cost_usd"], 6) if row["cost_usd"] is not None else None,
                "latency_ms": row["latency_ms"],
                "status": row["status"],
            }
            for row in recent
        ],
    }


def usage_since(utc_timestamp: str) -> dict[str, Any]:
    """Aggregated usage recorded after the given UTC timestamp.

    ``utc_timestamp`` must match SQLite's ``CURRENT_TIMESTAMP`` format
    (``YYYY-MM-DD HH:MM:SS``, UTC).
    """
    init_db()
    with get_connection() as conn:
        totals = conn.execute(
            """SELECT COUNT(*) AS calls,
                      COALESCE(SUM(prompt_tokens), 0) AS prompt_tokens,
                      COALESCE(SUM(completion_tokens), 0) AS completion_tokens,
                      COALESCE(SUM(total_tokens), 0) AS total_tokens,
                      COALESCE(SUM(cost_usd), 0) AS total_cost_usd
               FROM usage_log
               WHERE created_at >= ?""",
            (utc_timestamp,),
        ).fetchone()

        by_provider = conn.execute(
            """SELECT provider, model,
                      COUNT(*) AS calls,
                      COALESCE(SUM(total_tokens), 0) AS tokens,
                      COALESCE(SUM(cost_usd), 0) AS cost_usd
               FROM usage_log
               WHERE created_at >= ?
               GROUP BY provider, model ORDER BY cost_usd DESC""",
            (utc_timestamp,),
        ).fetchall()

    return {
        "calls": totals["calls"],
        "prompt_tokens": totals["prompt_tokens"],
        "completion_tokens": totals["completion_tokens"],
        "total_tokens": totals["total_tokens"],
        "estimated_cost_usd": round(totals["total_cost_usd"], 6),
        # A zero-cost total with calls > 0 means local/free models were used.
        "per_provider": [dict(row) | {"cost_usd": round(row["cost_usd"], 6)} for row in by_provider],
    }


class RunUsageTracker:
    """Accumulates usage across one pipeline run."""

    def __init__(self) -> None:
        self.calls = 0
        self.prompt_tokens = 0
        self.completion_tokens = 0
        self.total_cost_usd = 0.0
        self.cost_known_calls = 0
        self.per_provider: dict[str, dict[str, Any]] = {}

    def add(self, result: Any, cost: float | None) -> None:
        self.calls += 1
        self.prompt_tokens += result.prompt_tokens or 0
        self.completion_tokens += result.completion_tokens or 0
        if cost is not None:
            self.total_cost_usd += cost
            self.cost_known_calls += 1
        entry = self.per_provider.setdefault(
            f"{result.provider}:{result.model}",
            {"provider": result.provider, "model": result.model, "calls": 0,
             "tokens": 0, "cost_usd": 0.0},
        )
        entry["calls"] += 1
        entry["tokens"] += (result.prompt_tokens or 0) + (result.completion_tokens or 0)
        if cost is not None:
            entry["cost_usd"] = round(entry["cost_usd"] + cost, 6)

    def snapshot(self) -> dict[str, Any]:
        return {
            "calls": self.calls,
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.prompt_tokens + self.completion_tokens,
            "estimated_cost_usd": round(self.total_cost_usd, 6),
            # Some models have unknown pricing; surface how much of the spend
            # is actually priced vs untracked.
            "priced_calls": self.cost_known_calls,
            "unpriced_calls": self.calls - self.cost_known_calls,
            "per_provider": list(self.per_provider.values()),
        }
