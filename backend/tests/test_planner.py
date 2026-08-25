"""Tests for the planner agent's keyword handling."""
from __future__ import annotations

from app.agents.planner import PlannerAgent


def test_heuristic_keywords() -> None:
    keywords = PlannerAgent._heuristic_keywords("quantum computing")
    assert "quantum computing" in keywords
    assert "quantum computing tutorial" in keywords
    assert len(keywords) == 5


def test_normalize_keywords_dedupes_and_limits() -> None:
    raw = ["Quantum Computing", "quantum computing", "", 42, "quantum supremacy"]
    result = PlannerAgent._normalize_keywords(raw, "topic")
    assert result == ["Quantum Computing", "quantum supremacy"]


def test_normalize_keywords_falls_back_when_empty() -> None:
    assert PlannerAgent._normalize_keywords([], "solar cells") == PlannerAgent._heuristic_keywords("solar cells")


def test_generate_plan_falls_back_without_llm(monkeypatch) -> None:
    def raise_llm_error(*args, **kwargs):
        from app.services.llm.base import LLMError

        raise LLMError("no provider")

    # generate_with_failover raises -> planner should use heuristics.
    monkeypatch.setattr("app.agents.planner.generate_with_failover", raise_llm_error)

    plan = PlannerAgent().generate_plan("fusion energy", "quick")
    assert plan["keywords"] and all(isinstance(k, str) for k in plan["keywords"])
    assert plan["research_type"] == "quick"
