"""Tests for database layer, report store and stats."""
from __future__ import annotations

import pytest

from app.core import config
from app.core.database import get_connection, init_db
from app.services.reports import delete_report, get_stats, list_reports, save_report


@pytest.fixture()
def temp_settings(tmp_path, monkeypatch):
    """Point settings at a temporary directory and reset cached state."""
    fresh = config.Settings(data_dir=tmp_path / "data", reports_dir=tmp_path / "reports")
    monkeypatch.setattr(config, "settings", fresh)
    # database.py imports `settings` directly; patch it there too.
    import app.core.database as db_mod

    monkeypatch.setattr(db_mod, "settings", fresh)
    init_db()
    return fresh


def test_init_db_creates_tables(temp_settings) -> None:
    with get_connection() as conn:
        tables = {
            row["name"]
            for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        }
    assert {"pages", "chunks", "reports"} <= tables


def test_save_list_delete_roundtrip(temp_settings) -> None:
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
    assert delete_report(record["id"]) is True
    assert list_reports() == []


def test_stats_empty_database(temp_settings) -> None:
    stats = get_stats()
    assert stats["total_pages"] == 0
    assert stats["total_chunks"] == 0
