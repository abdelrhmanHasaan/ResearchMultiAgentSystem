"""Pytest configuration and shared fixtures."""
from __future__ import annotations

import pytest

from app.core import config
from app.core.database import init_db


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
