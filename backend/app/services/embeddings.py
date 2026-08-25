"""Embedding service with graceful degradation.

Primary: Ollama (nomic-embed-text) when the local daemon is running.
Fallback: deterministic hashing embeddings, so semantic search keeps working
with zero local setup.
"""
from __future__ import annotations

import hashlib
import logging
import math

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

FALLBACK_DIMENSIONS = 384


class HashingEmbeddings:
    """Deterministic hashed bag-of-words embeddings (no external service)."""

    dimensions = FALLBACK_DIMENSIONS

    def name(self) -> str:
        return "hashing-fallback"

    def embed(self, text: str) -> list[float]:
        vector = [0.0] * self.dimensions
        tokens = "".join(ch.lower() if ch.isalnum() else " " for ch in text).split()
        for token in tokens:
            digest = hashlib.md5(token.encode("utf-8")).digest()
            index = int.from_bytes(digest[:4], "little") % self.dimensions
            sign = 1.0 if digest[4] % 2 == 0 else -1.0
            vector[index] += sign
        norm = math.sqrt(sum(v * v for v in vector)) or 1.0
        return [v / norm for v in vector]


class OllamaEmbeddings:
    dimensions = 768

    def __init__(self, model: str) -> None:
        self.model = model
        self._base_url = settings.ollama_base_url.rstrip("/")

    def name(self) -> str:
        return f"ollama:{self.model}"

    @staticmethod
    def available() -> bool:
        try:
            with httpx.Client(timeout=3.0) as client:
                return client.get(f"{settings.ollama_base_url.rstrip('/')}/api/tags").status_code == 200
        except Exception:  # noqa: BLE001
            return False

    def embed(self, text: str) -> list[float]:
        with httpx.Client(timeout=60.0) as client:
            response = client.post(
                f"{self._base_url}/api/embeddings",
                json={"model": self.model, "prompt": text[:4000]},
            )
            response.raise_for_status()
            embedding = response.json().get("embedding", [])
        if not embedding:
            raise RuntimeError("Ollama returned an empty embedding")
        return embedding


class EmbeddingService:
    """Chooses the best backend once, then serves every request."""

    def __init__(self) -> None:
        self._backend = None
        if OllamaEmbeddings.available():
            self._backend = OllamaEmbeddings(settings.ollama_embed_model)
            logger.info("Embeddings: Ollama (%s)", settings.ollama_embed_model)
        else:
            self._backend = HashingEmbeddings()
            logger.info("Embeddings: Ollama unavailable - using deterministic hashing fallback")

    @property
    def backend_name(self) -> str:
        return self._backend.name()

    @property
    def dimensions(self) -> int:
        return self._backend.dimensions

    def embed(self, text: str) -> list[float]:
        try:
            return self._backend.embed(text)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Embedding backend failed (%s); using fallback.", exc)
            return HashingEmbeddings().embed(text)


_embedding_service: EmbeddingService | None = None


def get_embedding_service() -> EmbeddingService:
    global _embedding_service  # noqa: PLW0603
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service
