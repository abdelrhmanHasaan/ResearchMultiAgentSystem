"""Tests for database layer, report store and stats."""
from __future__ import annotations

from app.core.database import get_connection, init_db
from app.services.reports import (
    delete_report,
    get_report,
    get_stats,
    list_reports,
    save_report,
)


def test_init_db_creates_tables(temp_settings) -> None:
    with get_connection() as conn:
        tables = {
            row["name"]
            for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        }
    assert {"pages", "chunks", "reports", "usage_log"} <= tables


def test_save_list_get_delete_roundtrip(temp_settings) -> None:
    record = save_report(
        topic="quantum computing",
        pdf_path="report_x.pdf",
        pages_processed=5,
        chunks_included=42,
        detail_level="standard",
        report_content="# Report",
        critic_score=8.5,
    )
    items = list_reports()
    assert len(items) == 1
    assert items[0]["topic"] == "quantum computing"
    assert items[0]["metadata"]["chunks_included"] == 42
    assert items[0]["critic_score"] == 8.5

    stored = get_report(record["id"])
    assert stored is not None
    assert stored["report"] == "# Report"
    assert stored["critic_score"] == 8.5

    assert delete_report(record["id"]) is True
    assert list_reports() == []
    assert get_report(record["id"]) is None


def test_stats_empty_database(temp_settings) -> None:
    stats = get_stats()
    assert stats["total_pages"] == 0
    assert stats["total_chunks"] == 0


def test_critic_score_migration_on_legacy_db(temp_settings) -> None:
    """Simulate a v3 database without critic_score and verify migration adds it."""
    with get_connection() as conn:
        conn.execute("ALTER TABLE reports RENAME TO reports_old")
        conn.execute(
            """CREATE TABLE reports (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   topic TEXT, timestamp TEXT, pdf_path TEXT,
                   pages_processed INTEGER, chunks_included INTEGER,
                   detail_level TEXT, report_content TEXT
               )"""
        )
        conn.execute("DROP TABLE reports_old")

    init_db()  # should apply the migration

    with get_connection() as conn:
        columns = {row["name"] for row in conn.execute("PRAGMA table_info(reports)").fetchall()}
    assert "critic_score" in columns
