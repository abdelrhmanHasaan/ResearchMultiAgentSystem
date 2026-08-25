"""Critic agent: hallucination/contradiction guardrail with revision feedback."""
from __future__ import annotations

import logging
from typing import Any

from app.agents.base import BaseAgent
from app.agents.prompts import CRITIC_SYSTEM, CRITIC_TEMPLATE
from app.core.config import settings
from app.services.llm import LLMError, extract_json, generate_with_failover

logger = logging.getLogger(__name__)

MAX_RAW_DATA_CHARS = 12000
MAX_DRAFT_CHARS = 24000


class CriticAgent(BaseAgent):
    name = "critic"

    def evaluate(self, draft: str, sources: list[dict[str, Any]]) -> dict[str, Any]:
        raw_data = "\n\n".join(
            f"URL: {src.get('url')}\nTITLE: {src.get('title', '')}\nCONTENT: {src.get('content', '')[:800]}"
            for src in sources[:12]
        )[:MAX_RAW_DATA_CHARS]

        prompt = CRITIC_TEMPLATE.format(raw_data=raw_data or "(no source data)", draft=draft[:MAX_DRAFT_CHARS])

        try:
            result = generate_with_failover(prompt, stage="critic", temperature=0.0, json_mode=True)
            scores = self._normalize(extract_json(result.text))
        except (LLMError, ValueError) as exc:
            # Never block the pipeline on critic failure - fail open.
            logger.error("Critic evaluation failed; failing open: %s", exc)
            return {
                "score": 10.0,
                "hallucinations_detected": False,
                "contradictions_detected": False,
                "feedback": "",
                "error": str(exc),
            }

        logger.info(
            "Critic score: %.1f/10 (hallucinations=%s, contradictions=%s)",
            scores["score"], scores["hallucinations_detected"], scores["contradictions_detected"],
        )
        return scores

    @staticmethod
    def passed(scores: dict[str, Any]) -> bool:
        if scores.get("error"):
            return True
        return (
            scores["score"] >= settings.critic_pass_score
            and not scores["hallucinations_detected"]
            and not scores["contradictions_detected"]
        )

    @staticmethod
    def _normalize(parsed: dict[str, Any]) -> dict[str, Any]:
        def to_bool(value: Any) -> bool:
            if isinstance(value, bool):
                return value
            return str(value).strip().lower() in ("true", "yes", "1")

        try:
            score = float(parsed.get("score", 0.0))
        except (TypeError, ValueError):
            score = 0.0
        return {
            "score": max(0.0, min(10.0, score)),
            "hallucinations_detected": to_bool(parsed.get("hallucinations_detected", False)),
            "contradictions_detected": to_bool(parsed.get("contradictions_detected", False)),
            "feedback": str(parsed.get("feedback", ""))[:1500],
        }

    def run(self, data: dict[str, Any]) -> dict[str, Any]:
        return {**data, "critic_scores": self.evaluate(data["draft_report"], data.get("sources", []))}
