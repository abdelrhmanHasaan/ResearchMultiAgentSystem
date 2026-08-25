"""SQLite persistence layer: single schema definition + connection helpers."""
from __future__ import annotations

import logging
import sqlite3
from contextlib import contextmanager
from typing import Iterator

from app.core.config import settings

logger = logging.getLogger(__name__)

SCHEMA = [
    """
    CREATE TABLE IF NOT EXISTS pages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        url TEXT UNIQUE,
        title TEXT,
        content_hash TEXT,
        summary TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS chunks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        page_id INTEGER REFERENCES pages(id) ON DELETE CASCADE,
        chunk_text TEXT,
        chunk_index INTEGER,
        UNIQUE(page_id, chunk_index)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        topic TEXT,
        timestamp TEXT,
        pdf_path TEXT,
        pages_processed INTEGER,
        chunks_included INTEGER,
        detail_level TEXT,
        report_content TEXT
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_pages_url ON pages(url)",
    "CREATE INDEX IF NOT EXISTS idx_chunks_page_id ON chunks(page_id)",
]


def init_db() -> None:
    """Create all tables/indexes if missing. Safe to call repeatedly."""
    with get_connection() as conn:
        for statement in SCHEMA:
            conn.execute(statement)
    logger.info("Database initialised at %s", settings.db_path)


@contextmanager
def get_connection() -> Iterator[sqlite3.Connection]:
    settings.ensure_dirs()
    conn = sqlite3.connect(settings.db_path_str, timeout=30)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
