"""Search planner agent: expands a topic into optimized keyword clusters."""
from __future__ import annotations

import logging
from typing import Any

from app.agents.base import BaseAgent
from app.agents.prompts import PLANNER_PROMPTS
from app.services.llm import LLMError, extract_json, generate_with_failover

logger = logging.getLogger(__name__)

_FALLBACK_SUFFIXES = ("", " tutorial", " guide", " examples", " explained")


class PlannerAgent(BaseAgent):
    name = "planner"

    def generate_plan(self, topic: str, research_type: str = "quick") -> dict[str, Any]:
        system_prompt = PLANNER_PROMPTS.get(research_type, PLANNER_PROMPTS["quick"])
        prompt = f"{system_prompt}\n\nTOPIC: {topic}\n\nOUTPUT JSON:"

        try:
            result = generate_with_failover(prompt, stage="planner", temperature=0.3, json_mode=True)
            parsed = extract_json(result.text)
            keywords = self._normalize_keywords(parsed.get("keywords", []), topic)
        except (LLMError, ValueError) as exc:
            logger.warning("Planner falling back to heuristic keywords: %s", exc)
            keywords = self._heuristic_keywords(topic)

        return {"topic": topic, "research_type": research_type, "keywords": keywords}

    @staticmethod
    def _normalize_keywords(raw: Any, topic: str) -> list[str]:
        keywords: list[str] = []
        seen: set[str] = set()
        for item in raw if isinstance(raw, list) else []:
            if isinstance(item, str) and item.strip():
                cleaned = item.strip()[:120]
                key = cleaned.lower()
                if key not in seen:
                    seen.add(key)
                    keywords.append(cleaned)
        return keywords or PlannerAgent._heuristic_keywords(topic)

    @staticmethod
    def _heuristic_keywords(topic: str) -> list[str]:
        return [f"{topic}{suffix}".strip() for suffix in _FALLBACK_SUFFIXES]

    def run(self, data: dict[str, Any]) -> dict[str, Any]:
        plan = self.generate_plan(data["query"], data.get("research_type", "quick"))
        return {**data, **plan}
