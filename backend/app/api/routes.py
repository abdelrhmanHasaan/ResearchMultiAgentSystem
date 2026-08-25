"""HTTP API routes."""
from __future__ import annotations

import asyncio
import json
import logging

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse, StreamingResponse

from app.api.schemas import (
    DeleteResponse,
    HealthResponse,
    HistoryItem,
    ProviderInfo,
    ResearchRequest,
    ResearchResponse,
    StatsResponse,
)
from app.core.config import settings
from app.services.embeddings import get_embedding_service
from app.services.llm import LLMError, describe_providers
from app.services.pipeline import get_pipeline
from app.services.reports import delete_report, get_stats, list_reports
from app.vectorstore.store import CHROMA_AVAILABLE, get_vector_store

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api")


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------
@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    providers = describe_providers()
    active = any(p["active"] for p in providers)
    return HealthResponse(
        status="ok" if active else "degraded",
        version=settings.version,
        llm_providers=[ProviderInfo(**p) for p in providers],
        vector_store_backend="chromadb" if CHROMA_AVAILABLE else "memory",
        embedding_backend=get_embedding_service().backend_name,
    )


@router.get("/providers")
async def providers():
    return {"providers": describe_providers(), "fallback_order": settings.fallback_order()}


# ---------------------------------------------------------------------------
# Research (blocking + streaming variants)
# ---------------------------------------------------------------------------
@router.post("/research", response_model=ResearchResponse)
async def run_research(request: ResearchRequest) -> ResearchResponse:
    """Run the full pipeline and return the final result."""
    try:
        result = await get_pipeline().run(
            request.query.strip(), request.research_type, request.detail_level
        )
    except LLMError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return ResearchResponse(**result)


@router.post("/research/stream")
async def run_research_stream(request: ResearchRequest) -> StreamingResponse:
    """Run the pipeline, streaming stage-by-stage progress as server-sent events."""

    async def event_stream():
        queue: asyncio.Queue[bytes | None] = asyncio.Queue()

        async def emit(event: dict) -> None:
            payload = json.dumps(event, ensure_ascii=False, default=str)
            await queue.put(f"data: {payload}\n\n".encode("utf-8"))

        async def runner() -> None:
            try:
                await get_pipeline().run(
                    request.query.strip(),
                    request.research_type,
                    request.detail_level,
                    emit=emit,
                )
            except Exception as exc:  # noqa: BLE001 - last-resort guard for the stream
                logger.exception("Stream pipeline crashed")
                error = json.dumps({"type": "result", "status": "error", "error": str(exc)})
                await queue.put(f"data: {error}\n\n".encode("utf-8"))
            finally:
                await queue.put(None)

        task = asyncio.create_task(runner())
        try:
            yield b": connected\n\n"
            while True:
                chunk = await queue.get()
                if chunk is None:
                    break
                yield chunk
            yield b"data: [DONE]\n\n"
        finally:
            task.cancel()

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no", "Connection": "keep-alive"},
    )


# ---------------------------------------------------------------------------
# Stats / history / files
# ---------------------------------------------------------------------------
@router.get("/stats", response_model=StatsResponse)
async def stats() -> StatsResponse:
    return StatsResponse(**get_stats())


@router.get("/history", response_model=list[HistoryItem])
async def history(limit: int = Query(100, ge=1, le=500)) -> list[HistoryItem]:
    return [HistoryItem(**item) for item in list_reports(limit)]


@router.delete("/history/{report_id}", response_model=DeleteResponse)
async def remove_report(report_id: int) -> DeleteResponse:
    return DeleteResponse(deleted=delete_report(report_id), id=report_id)


@router.get("/pdf/{filename}")
async def serve_pdf(filename: str) -> FileResponse:
    from pathlib import Path

    safe_name = Path(filename).name  # blocks directory traversal
    if not safe_name.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Invalid file type")

    path = settings.reports_dir / safe_name
    if not path.is_file():
        raise HTTPException(status_code=404, detail="Report not found")
    return FileResponse(path, media_type="application/pdf", filename=safe_name)
