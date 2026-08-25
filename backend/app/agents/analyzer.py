"""Analyzer agent: deduplication, LLM summaries, chunking, vector indexing."""
from __future__ import annotations

import hashlib
import logging
from typing import Any

from app.agents.base import BaseAgent
from app.agents.prompts import ANALYZER_BATCH_PROMPT
from app.core.database import get_connection, init_db
from app.services.llm import LLMError, extract_json, get_llm
from app.vectorstore.store import get_vector_store

logger = logging.getLogger(__name__)

CHUNK_SIZE = 1200
CHUNK_OVERLAP = 200


def hash_content(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def chunk_text(text: str, size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[tuple[int, str]]:
    chunks: list[tuple[int, str]] = []
    start, index = 0, 0
    while start < len(text):
        chunks.append((index, text[start : start + size]))
        start += size - overlap
        index += 1
    return chunks


class AnalyzerAgent(BaseAgent):
    name = "analyzer"

    def __init__(self) -> None:
        init_db()

    def run(self, data: dict[str, Any]) -> dict[str, Any]:
        sources = data.get("sources", [])
        with get_connection() as conn:
            new_sources = self._filter_new(sources, conn)
            if not new_sources:
                logger.info("Analyzer: nothing new to insert (%d sources seen before).", len(sources))
                return {**data, "inserted": 0, "skipped": len(sources), "chunks_stored": 0}

            analyses = self._analyze_batch([src["content"] for src in new_sources])

            inserted = 0
            for src, analysis in zip(new_sources, analyses):
                page_id = self._insert_page(src, analysis, conn)
                self._insert_chunks(page_id, src["content"], conn)
                inserted += 1

        # Vector indexing is best-effort; the pipeline continues on failure.
        try:
            stored = get_vector_store().ingest_documents(new_sources)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Vector ingestion skipped: %s", exc)
            stored = 0

        return {
            **data,
            "inserted": inserted,
            "skipped": len(sources) - inserted,
            "chunks_stored": stored,
        }

    # ------------------------------------------------------------------
    @staticmethod
    def _filter_new(sources: list[dict[str, Any]], conn) -> list[dict[str, Any]]:
        cursor = conn.cursor()
        new_sources = []
        for src in sources:
            content, url = src.get("content", ""), src.get("url")
            if not content or not url:
                continue
            content_hash = hash_content(content)
            cursor.execute(
                "SELECT id FROM pages WHERE url=? OR content_hash=?", (url, content_hash)
            )
            if cursor.fetchone():
                continue
            src = dict(src)
            src["_hash"] = content_hash
            new_sources.append(src)
        return new_sources

    def _analyze_batch(self, contents: list[str]) -> list[dict[str, Any]]:
        """LLM summaries are best-effort: failures degrade to truncated content."""
        default = [{"summary": "", "key_topics": []}] * len(contents)
        if not contents:
            return []
        try:
            joined = "\n\n---\n\n".join(c[:1500] for c in contents)
            response = get_llm().generate(
                ANALYZER_BATCH_PROMPT.format(documents=joined), temperature=0.2, json_mode=True
            )
            parsed = extract_json(response)
            results = parsed.get("results", [])
            # Pad/trim so results always align with inputs (fixes zip-truncation bug).
            while len(results) < len(contents):
                results.append({"summary": "", "key_topics": []})
            return results[: len(contents)]
        except (LLMError, ValueError) as exc:
            logger.warning("Batch analysis failed; storing raw excerpts as summaries: %s", exc)
            fallback = []
            for content in contents:
                fallback.append({
                    "summary": content[:280].rsplit(" ", 1)[0] + "...",
                    "key_topics": [],
                    "_fallback": True,
                })
            return fallback

    @staticmethod
    def _insert_page(src: dict[str, Any], analysis: dict[str, Any], conn) -> int:
        summary = analysis.get("summary") or ""
        topics = ", ".join(analysis.get("key_topics", [])[:5])
        if topics:
            summary = f"{summary}\n\nKey topics: {topics}".strip()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO pages (url, title, content_hash, summary) VALUES (?, ?, ?, ?)",
            (src["url"], src.get("title"), src["_hash"], summary),
        )
        return int(cursor.lastrowid)

    @staticmethod
    def _insert_chunks(page_id: int, content: str, conn) -> int:
        cursor = conn.cursor()
        count = 0
        for index, chunk in chunk_text(content):
            try:
                cursor.execute(
                    "INSERT INTO chunks (page_id, chunk_text, chunk_index) VALUES (?, ?, ?)",
                    (page_id, chunk, index),
                )
                count += 1
            except Exception:  # noqa: BLE001 - duplicate chunk indices are harmless
                continue
        return count
