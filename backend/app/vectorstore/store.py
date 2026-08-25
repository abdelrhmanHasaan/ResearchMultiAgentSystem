"""Vector store with optional ChromaDB backend.

If ``chromadb`` is installed the store persists embeddings on disk; otherwise
a lightweight in-process store keeps the pipeline fully functional.
"""
from __future__ import annotations

import logging
from typing import Any

from app.services.embeddings import get_embedding_service

logger = logging.getLogger(__name__)

try:  # Optional dependency - the system works without it.
    import chromadb  # type: ignore

    CHROMA_AVAILABLE = True
except ImportError:  # pragma: no cover - depends on environment
    chromadb = None
    CHROMA_AVAILABLE = False


class InMemoryVectorStore:
    """Tiny fallback store using brute-force cosine similarity."""

    def __init__(self) -> None:
        self._vectors: list[list[float]] = []
        self._documents: list[str] = []
        self._metadatas: list[dict[str, Any]] = []

    def upsert(self, *, ids, embeddings, documents, metadatas) -> None:
        existing = {m.get("uid") for m in self._metadatas}
        for uid, vec, doc, meta in zip(ids, embeddings, documents, metadatas):
            if uid in existing:
                continue
            self._vectors.append(vec)
            self._documents.append(doc)
            self._metadatas.append(meta)

    def query(self, query_embedding: list[float], n_results: int = 5) -> dict[str, Any]:
        def cosine(a: list[float], b: list[float]) -> float:
            dot = sum(x * y for x, y in zip(a, b))
            na = sum(x * x for x in a) ** 0.5 or 1.0
            nb = sum(y * y for y in b) ** 0.5 or 1.0
            return dot / (na * nb)

        scored = sorted(
            ((cosine(query_embedding, vec), i) for i, vec in enumerate(self._vectors)),
            key=lambda pair: pair[0],
            reverse=True,
        )[:n_results]
        return {
            "documents": [[self._documents[i] for _, i in scored]],
            "metadatas": [[self._metadatas[i] for _, i in scored]],
            "distances": [[1.0 - score for score, _ in scored]],
        }


class VectorStoreManager:
    """Chunk ingestion + semantic search over scraped research content."""

    def __init__(self, collection_name: str = "research_docs") -> None:
        self.embedder = get_embedding_service()
        self.collection_name = collection_name

        if CHROMA_AVAILABLE:
            from pathlib import Path

            from app.core.config import settings as s

            persist_dir = Path(s.data_dir) / "chroma"
            persist_dir.mkdir(parents=True, exist_ok=True)
            client = chromadb.PersistentClient(path=str(persist_dir))
            self.collection = client.get_or_create_collection(name=collection_name)
            self._backend = "chromadb"
        else:
            self.collection = InMemoryVectorStore()
            self._backend = "memory"

        logger.info("Vector store backend: %s (embeddings: %s)", self._backend, self.embedder.backend_name)

    @property
    def backend(self) -> str:
        return self._backend

    @staticmethod
    def chunk_text(text: str, chunk_words: int = 220, overlap_words: int = 40) -> list[str]:
        words = text.split()
        step = max(chunk_words - overlap_words, 1)
        return [" ".join(words[i : i + chunk_words]) for i in range(0, len(words), step)]

    def ingest_documents(self, documents: list[dict[str, Any]]) -> int:
        """Ingest scraped pages. Returns number of chunks stored."""
        ids: list[str] = []
        embeddings: list[list[float]] = []
        texts: list[str] = []
        metadatas: list[dict[str, Any]] = []

        for doc in documents:
            url = doc.get("url", "unknown")
            content = doc.get("content", "")
            if not content:
                continue

            for index, chunk in enumerate(self.chunk_text(content)):
                try:
                    embedding = self.embedder.embed(chunk)
                except Exception as exc:  # noqa: BLE001
                    logger.warning("Skipping chunk (embedding failed): %s", exc)
                    continue
                uid = f"{url}#{index}"
                ids.append(uid)
                embeddings.append(embedding)
                texts.append(chunk)
                metadatas.append({"uid": uid, "url": url, "title": doc.get("title", ""), "chunk_index": index})

        if ids:
            try:
                self.collection.upsert(
                    ids=ids, embeddings=embeddings, documents=texts, metadatas=metadatas
                )
                logger.info("Ingested %d chunks into vector store (%s).", len(ids), self._backend)
            except Exception as exc:  # noqa: BLE001
                logger.error("Vector store upsert failed: %s", exc)
                return 0
        return len(ids)

    def search(self, query: str, n_results: int = 5) -> list[dict[str, Any]]:
        try:
            query_embedding = self.embedder.embed(query)
            results = self.collection.query(query_embeddings=[query_embedding], n_results=n_results)
        except Exception as exc:  # noqa: BLE001
            logger.error("Vector search failed: %s", exc)
            return []

        documents = (results.get("documents") or [[]])[0]
        metadatas = (results.get("metadatas") or [[]])[0]
        distances = (results.get("distances") or [[]])[0]
        hits = []
        for i, document in enumerate(documents):
            metadata = metadatas[i] if i < len(metadatas) else {}
            distance = distances[i] if i < len(distances) else 1.0
            hits.append({"text": document, "metadata": metadata, "score": round(1.0 - distance, 4)})
        return hits


_store: VectorStoreManager | None = None


def get_vector_store() -> VectorStoreManager:
    global _store  # noqa: PLW0603
    if _store is None:
        _store = VectorStoreManager()
    return _store
