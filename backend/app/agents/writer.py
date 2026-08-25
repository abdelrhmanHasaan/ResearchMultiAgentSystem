"""Writer agent: RAG report drafting + PDF rendering."""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from app.agents.base import BaseAgent
from app.agents.prompts import WRITER_DETAIL_INSTRUCTIONS, WRITER_FEEDBACK_BLOCK, WRITER_TEMPLATE
from app.core.config import settings
from app.core.database import get_connection
from app.services.llm import LLMError, get_llm
from app.services.pdf import generate_pdf, sanitize_text_for_pdf

logger = logging.getLogger(__name__)

MAX_CONTEXT_PAGES = 60
CHUNKS_PER_PAGE = {"brief": 3, "standard": 6, "comprehensive": 10}


def fetch_pages(limit: int = MAX_CONTEXT_PAGES) -> list[dict[str, Any]]:
    with get_connection() as conn:
        rows = conn.execute(
            """SELECT id, url, title, summary, created_at FROM pages
               WHERE url LIKE ? OR url LIKE ?
               ORDER BY id DESC LIMIT ?""",
            ("%http%", "%https%", limit),
        ).fetchall()
    return [dict(row) for row in rows]


def fetch_chunks(page_ids: list[int], per_page: int) -> list[dict[str, Any]]:
    if not page_ids:
        return []
    placeholders = ",".join("?" * len(page_ids))
    with get_connection() as conn:
        rows = conn.execute(
            f"""SELECT page_id, chunk_text, chunk_index FROM chunks
                WHERE page_id IN ({placeholders})
                ORDER BY page_id DESC, chunk_index ASC""",
            page_ids,
        ).fetchall()
    # Keep at most `per_page` chunks per page.
    seen: dict[int, int] = {}
    chunks = []
    for row in rows:
        count = seen.get(row["page_id"], 0)
        if count < per_page:
            chunks.append({"page_id": row["page_id"], "text": row["chunk_text"], "index": row["chunk_index"]})
            seen[row["page_id"]] = count + 1
    return chunks


def build_context(pages: list[dict[str, Any]], chunks: list[dict[str, Any]], max_chars: int = 28000) -> str:
    parts: list[str] = ["=== SOURCE SUMMARIES ===\n"]
    budget = max_chars * 0.5
    used = 0
    for page in pages:
        block = (
            f"TITLE: {page.get('title') or 'Untitled'}\n"
            f"URL: {page.get('url')}\n"
            f"DATE: {page.get('created_at')}\n"
            f"SUMMARY: {(page.get('summary') or '')[:900]}\n---\n"
        )
        if used + len(block) > budget:
            break
        parts.append(block)
        used += len(block)

    parts.append("\n=== SUPPORTING EVIDENCE (raw chunks) ===\n")
    used = 0
    budget = max_chars * 0.45
    for chunk in chunks:
        block = f"[Page {chunk['page_id']} | Chunk {chunk['index']}]\n{chunk['text'][:1400]}\n---\n"
        if used + len(block) > budget:
            break
        parts.append(block)
        used += len(block)
    return "\n".join(parts)


class WriterAgent(BaseAgent):
    name = "writer"

    def run(self, data: dict[str, Any]) -> dict[str, Any]:
        topic = data["query"]
        options = data.get("options", {})
        detail_level = options.get("detail_level", "comprehensive")
        feedback = options.get("feedback")

        pages = fetch_pages()
        if not pages:
            raise RuntimeError(
                "No indexed pages available. Run the scraper/analyzer stages first."
            )

        per_page = CHUNKS_PER_PAGE.get(detail_level, 10)
        chunks = fetch_chunks([p["id"] for p in pages], per_page)
        context = build_context(pages, chunks)

        prompt = self._build_prompt(topic, context, detail_level, feedback)
        report = get_llm().generate(prompt, temperature=0.55, max_tokens=4096)
        report = sanitize_text_for_pdf(report or "").strip()
        if not report:
            raise LLMError("Writer produced an empty report.")

        pdf_path = self._render_pdf(topic, report, pages, len(chunks))
        return {
            **data,
            "report": report,
            "pdf": pdf_path.name,
            "pages_used": len(pages),
            "chunks_used": len(chunks),
        }

    @staticmethod
    def _build_prompt(topic: str, context: str, detail_level: str, feedback: str | None) -> str:
        instructions = WRITER_DETAIL_INSTRUCTIONS.get(detail_level, WRITER_DETAIL_INSTRUCTIONS["comprehensive"])
        feedback_block = ""
        if feedback:
            feedback_block = WRITER_FEEDBACK_BLOCK.format(feedback=feedback)
        return WRITER_TEMPLATE.format(
            topic=topic,
            detail_instructions=instructions,
            context=context,
            feedback_block=feedback_block,
        )

    @staticmethod
    def _render_pdf(topic: str, report: str, pages: list[dict[str, Any]], chunk_count: int) -> Any:
        stats = {"total_pages": len(pages), "total_chunks": chunk_count, "recent_pages": len(pages)}
        safe_topic = "".join(ch for ch in topic.lower() if ch.isalnum() or ch in (" ", "-"))
        slug = "_".join(safe_topic.split())[:50] or "report"
        filename = f"report_{slug}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        output = settings.reports_dir / filename
        generate_pdf(report, output, topic=topic, stats=stats, pages_data=pages)
        logger.info("PDF generated: %s", output)
        return output


# Backwards-compatible alias.
EnhancedWriterAgent = WriterAgent
