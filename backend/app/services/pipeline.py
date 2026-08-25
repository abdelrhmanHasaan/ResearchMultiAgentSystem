"""Research pipeline orchestrator.

Runs the five-agent flow and emits structured events so the API can stream
progress to the frontend in real time:

    Planner -> Scraper -> Analyzer -> Writer <-> Critic (revision loop) -> PDF
"""
from __future__ import annotations

import asyncio
import logging
import time
from typing import Any, Awaitable, Callable

from app.agents.analyzer import AnalyzerAgent
from app.agents.critic import CriticAgent
from app.agents.planner import PlannerAgent
from app.agents.scraper_agent import ScraperAgent
from app.agents.writer import WriterAgent
from app.core.config import settings
from app.services.reports import save_report

logger = logging.getLogger(__name__)

STAGES = ("Planner", "Scraper", "Analyzer", "Writer", "Critic")

EventCallback = Callable[[dict[str, Any]], Awaitable[None]]


class ResearchPipeline:
    def __init__(self) -> None:
        self._planner = PlannerAgent()
        self._scraper = ScraperAgent()
        self._analyzer: AnalyzerAgent | None = None
        self._writer: WriterAgent | None = None
        self._critic = CriticAgent()

    async def run(
        self,
        query: str,
        research_type: str,
        detail_level: str,
        emit: EventCallback | None = None,
    ) -> dict[str, Any]:
        started = time.monotonic()
        logs: list[dict[str, str]] = []

        async def stage(stage_name: str, status: str, output: str) -> None:
            entry = {"stage": stage_name, "status": status, "output": output}
            # Replace any previous entry for the same stage (revision loops).
            for existing in logs:
                if existing["stage"] == stage_name:
                    existing.update(status=status, output=output)
                    break
            else:
                logs.append(entry)
            logger.info("[%s] %s: %s", query, stage_name, output)
            if emit:
                await emit({"type": "stage", **entry})

        def blocking(fn, *args):
            return asyncio.to_thread(fn, *args)

        try:
            # 1. Planner -------------------------------------------------
            await stage("Planner", "running", f"Analyzing semantic core of prompt: '{query}'")
            plan = await blocking(self._planner.generate_plan, query, research_type)
            keywords = plan.get("keywords") or [query]
            await stage("Planner", "completed", f"Expanded query into keywords: {', '.join(keywords[:6])}")

            # 2. Scraper -------------------------------------------------
            await stage("Scraper", "running", "Running parallel web search & content extraction...")
            data: dict[str, Any] = {
                "query": query,
                "research_type": research_type,
                "keywords": keywords,
                "sources": [],
            }
            data = await self._scraper.run(data)
            sources = data.get("sources", [])
            if not sources:
                raise RuntimeError(
                    "No usable web sources were scraped. Try rephrasing the query."
                )
            await stage(
                "Scraper",
                "completed",
                f"Retrieved {len(sources)} high-quality sources "
                f"({data['scrape_stats']['failed']} failed).",
            )

            # 3. Analyzer ------------------------------------------------
            await stage("Analyzer", "running", "Deduplicating, chunking & indexing content...")
            if self._analyzer is None:
                self._analyzer = AnalyzerAgent()
            data = await blocking(self._analyzer.run, data)
            inserted = data.get("inserted", 0)
            await stage(
                "Analyzer",
                "completed",
                f"Indexed {inserted} new pages ({data.get('chunks_stored', 0)} vector chunks); "
                f"{data.get('skipped', 0)} duplicates skipped.",
            )

            # 4. Writer <-> Critic loop ----------------------------------
            feedback: str | None = None
            report_text = ""
            pdf_name = ""
            scores: dict[str, Any] = {}
            for iteration in range(1, settings.max_revision_loops + 1):
                suffix = f" (Iteration {iteration})" if iteration > 1 else ""
                await stage("Writer", "running", f"Synthesizing markdown draft chapters{suffix}...")
                options = {"detail_level": detail_level, "feedback": feedback}
                try:
                    data = await blocking(self._writer_run, {**data, "options": options})
                except RuntimeError as exc:
                    if "No indexed pages" in str(exc):
                        raise RuntimeError(str(exc)) from exc
                    raise

                report_text = data["report"]
                pdf_name = data["pdf"]

                await stage("Critic", "running", f"Auditing draft for factual consistency{suffix}...")
                scores = await blocking(self._critic.evaluate, report_text, sources[:12])

                if CriticAgent.passed(scores):
                    await stage(
                        "Critic",
                        "completed",
                        f"Critic rating {scores['score']:.1f}/10 - passed factual consistency check.",
                    )
                    break

                feedback = scores["feedback"]
                await stage(
                    "Critic",
                    "running",
                    f"Critic rating {scores['score']:.1f}/10"
                    + (f" - hallucinations detected" if scores["hallucinations_detected"] else "")
                    + ". Re-routing to writer for revision.",
                )
            else:
                await stage(
                    "Critic",
                    "completed",
                    f"Max revision iterations reached (final score {scores.get('score', 0):.1f}/10). "
                    "Proceeding with best draft.",
                )

            # 5. Persist --------------------------------------------------
            elapsed = round(time.monotonic() - started, 1)
            record = save_report(
                topic=query,
                pdf_path=pdf_name,
                pages_processed=len(sources),
                chunks_included=data.get("inserted", 0),
                detail_level=detail_level,
                report_content=report_text,
                critic_score=scores.get("score"),
            )

            result = {
                "status": "success",
                "query": query,
                "report": report_text,
                "pdf": pdf_name,
                "report_id": record["id"],
                "critic_score": scores.get("score"),
                "stats": {
                    "total_pages": len(sources),
                    "total_chunks": data.get("chunks_stored", 0),
                    "recent_pages": len(sources),
                    "avg_chunks_per_page": round(
                        data.get("chunks_stored", 0) / max(inserted, 1), 1
                    ),
                },
                "elapsed_seconds": elapsed,
                "logs": logs,
            }
            if emit:
                await emit({"type": "result", **result})
            return result

        except Exception as exc:  # noqa: BLE001 - convert failures into structured errors
            logger.exception("Pipeline failed for %r", query)
            failed_stage = next(
                (log["stage"] for log in reversed(logs) if log["status"] == "running"),
                "Planner",
            )
            message = str(exc) or exc.__class__.__name__
            await stage(failed_stage, "failed", f"Pipeline failed: {message}")
            error_result = {
                "status": "error",
                "query": query,
                "report": "",
                "pdf": "",
                "error": message,
                "stats": {"total_pages": 0, "total_chunks": 0, "recent_pages": 0, "avg_chunks_per_page": 0},
                "elapsed_seconds": round(time.monotonic() - started, 1),
                "logs": logs,
            }
            if emit:
                await emit({"type": "result", **error_result})
            return error_result

    def _writer_run(self, data: dict[str, Any]) -> dict[str, Any]:
        if self._writer is None:
            self._writer = WriterAgent()
        return self._writer.run(data)


_pipeline: ResearchPipeline | None = None


def get_pipeline() -> ResearchPipeline:
    global _pipeline  # noqa: PLW0603
    if _pipeline is None:
        _pipeline = ResearchPipeline()
    return _pipeline
