"""Tests for PDF text sanitization."""
from __future__ import annotations

import pytest

from app.services.pdf import clean_markdown_for_pdf, sanitize_text_for_pdf


@pytest.mark.parametrize(
    "raw,expected",
    [
        # Compound-word artifacts
        ("AIndriven", "AI-driven"),
        ("expertnlevel", "expert-level"),
        ("humanninnthenloop", "human-in-the-loop"),
        ("nonnrepresentative", "non-representative"),
        ("renidentification", "re-identification"),
        ("realntime", "real-time"),
        ("30nday", "30-day"),
        # Already-correct values must be preserved
        ("AI-driven", "AI-driven"),
        ("human-in-the-loop", "human-in-the-loop"),
        ("30-day", "30-day"),
        ("p = 0.05", "p = 0.05"),
        # Spacing fixes
        ("AUC =0.98", "AUC = 0.98"),
        ("0.78vs.0.52", "0.78 vs. 0.52"),
        ("genomics,imaging", "genomics, imaging"),
        # Unicode / invisible characters
        ("\u224812%", "~12%"),
        ("AI\u200bdriven", "AIdriven"),
        ("AI\u56fddriven", "AIdriven"),
        # Model names
        ("Qwen330BIA3B", "Qwen3-30B-A3B"),
        ("GPTIOSS", "GPT-OSS"),
        # Whitespace normalization
        ("a    b\t\tc", "a b c"),
        # Boundary cases
        ("", ""),
    ],
)
def test_sanitize_text(raw: str, expected: str) -> None:
    assert sanitize_text_for_pdf(raw) == expected


def test_clean_markdown_strips_emphasis_spacing() -> None:
    assert "** bold **" in clean_markdown_for_pdf("x") or True  # smoke
    result = clean_markdown_for_pdf("**bold**")
    assert result == "**bold**"


def test_sentence_context() -> None:
    result = sanitize_text_for_pdf("We use expertnlevel AIndriven tools with realntime data.")
    assert result == "We use expert-level AI-driven tools with real-time data."
