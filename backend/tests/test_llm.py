"""Tests for the LLM provider registry and JSON extraction."""
from __future__ import annotations

import pytest

from app.services.llm import extract_json
from app.services.llm.base import LLMError, LLMProvider


class FakeProvider(LLMProvider):
    name = "fake"

    def __init__(self, fail_times: int = 0) -> None:
        self.fail_times = fail_times

    def is_configured(self) -> bool:
        return True

    def _generate(self, prompt, *, system, temperature, max_tokens, json_mode):
        if self.fail_times > 0:
            self.fail_times -= 1
            raise RuntimeError("boom")
        return "ok"


def test_retry_then_success() -> None:
    provider = FakeProvider(fail_times=1)
    assert provider.generate("hello", retries=2) == "ok"


def test_retries_exhausted_raises_llm_error() -> None:
    provider = FakeProvider(fail_times=10)
    with pytest.raises(LLMError):
        provider.generate("hello", retries=1)


def test_extract_json_direct() -> None:
    assert extract_json('{"keywords": ["a"]}') == {"keywords": ["a"]}


def test_extract_json_with_code_fence() -> None:
    text = '```json\n{"score": 8.5}\n```'
    assert extract_json(text) == {"score": 8.5}


def test_extract_json_embedded_in_prose() -> None:
    text = 'Here is your result: {"ok": true, "n": 3} hope that helps!'
    assert extract_json(text) == {"ok": True, "n": 3}


def test_extract_json_invalid_raises() -> None:
    with pytest.raises(ValueError):
        extract_json("no json here at all")
