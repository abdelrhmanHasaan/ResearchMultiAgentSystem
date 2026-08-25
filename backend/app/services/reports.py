"""Report history persistence."""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from app.core.database import get_connection, init_db

logger = logging.getLogger(__name__)


def save_report(
    *,
    topic: str,
    pdf_path: str,
    pages_processed: int,
    chunks_included: int,
    detail_level: str,
    report_content: str,
    critic_score: float | None = None,
) -> dict[str, Any]:
    init_db()
    with get_connection() as conn:
        cursor = conn.execute(
            """INSERT INTO reports
               (topic, timestamp, pdf_path, pages_processed, chunks_included, detail_level, report_content)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                topic,
                datetime.now().isoformat(),
                pdf_path,
                pages_processed,
                chunks_included,
                detail_level,
                report_content,
            ),
        )
        return {"id": cursor.lastrowid}


def list_reports(limit: int = 100) -> list[dict[str, Any]]:
    init_db()
    with get_connection() as conn:
        rows = conn.execute(
            """SELECT id, topic, timestamp, pdf_path, pages_processed, chunks_included, detail_level
               FROM reports ORDER BY id DESC LIMIT ?""",
            (limit,),
        ).fetchall()
    return [
        {
            "id": row["id"],
            "topic": row["topic"],
            "timestamp": row["timestamp"],
            "pdf_path": row["pdf_path"],
            "metadata": {
                "pages_processed": row["pages_processed"] or 0,
                "chunks_included": row["chunks_included"] or 0,
                "detail_level": row["detail_level"] or "standard",
            },
        }
        for row in rows
    ]


def delete_report(report_id: int) -> bool:
    with get_connection() as conn:
        cursor = conn.execute("DELETE FROM reports WHERE id = ?", (report_id,))
        return cursor.rowcount > 0


def get_stats() -> dict[str, Any]:
    init_db()
    try:
        with get_connection() as conn:
            total_pages = conn.execute("SELECT COUNT(*) AS c FROM pages").fetchone()["c"]
            total_chunks = conn.execute("SELECT COUNT(*) AS c FROM chunks").fetchone()["c"]
            recent_pages = conn.execute(
                "SELECT COUNT(*) AS c FROM pages WHERE created_at >= datetime('now', '-7 days')"
            ).fetchone()["c"]
            avg_row = conn.execute(
                """SELECT AVG(chunk_count) AS avg FROM
                   (SELECT COUNT(*) AS chunk_count FROM chunks GROUP BY page_id)"""
            ).fetchone()["avg"]
            avg_summary = conn.execute(
                "SELECT AVG(LENGTH(summary)) AS avg FROM pages WHERE summary IS NOT NULL"
            ).fetchone()["avg"]
    except Exception:  # noqa: BLE001 - stats must never break the API
        logger.exception("Failed computing stats")
        total_pages = total_chunks = recent_pages = 0
        avg_row = avg_summary = 0

    return {
        "total_pages": total_pages,
        "total_chunks": total_chunks,
        "recent_pages": recent_pages,
        "avg_chunks_per_page": round(avg_row or 0.0, 1),
        "avg_summary_length": int(avg_summary or 0),
    }
