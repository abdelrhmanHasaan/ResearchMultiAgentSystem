"""API request/response models."""
from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

ResearchType = Literal["quick", "deep", "academic"]
DetailLevel = Literal["brief", "standard", "comprehensive"]


class ResearchRequest(BaseModel):
    query: str = Field(..., min_length=3, max_length=500)
    research_type: ResearchType = "deep"
    detail_level: DetailLevel = "standard"


class PipelineLog(BaseModel):
    stage: str
    status: str
    output: str


class PipelineStats(BaseModel):
    total_pages: int = 0
    total_chunks: int = 0
    recent_pages: int | None = 0
    avg_chunks_per_page: float = 0.0


class ResearchResponse(BaseModel):
    status: Literal["success", "error"]
    query: str
    report: str = ""
    pdf: str = ""
    report_id: int | None = None
    critic_score: float | None = None
    sources: list[SourceRef] = []
    usage: RunUsage | None = None
    error: str | None = None
    stats: PipelineStats = PipelineStats()
    elapsed_seconds: float = 0.0
    logs: list[PipelineLog] = []


class HistoryItemMetadata(BaseModel):
    pages_processed: int
    chunks_included: int
    detail_level: str


class HistoryItem(BaseModel):
    id: int
    topic: str
    timestamp: str
    pdf_path: str
    metadata: HistoryItemMetadata
    critic_score: float | None = None


class StoredReport(BaseModel):
    id: int
    topic: str
    timestamp: str
    pdf_path: str
    metadata: HistoryItemMetadata
    report: str
    critic_score: float | None = None


class SourceRef(BaseModel):
    url: str | None = None
    title: str | None = None


class RunUsage(BaseModel):
    calls: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    estimated_cost_usd: float = 0.0
    per_provider: list[dict[str, Any]] = []


class UsageTotals(BaseModel):
    calls: int
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    total_cost_usd: float
    avg_latency_ms: int
    errors: int


class UsageSummaryResponse(BaseModel):
    totals: UsageTotals
    by_provider: list[dict[str, Any]]
    by_stage: list[dict[str, Any]]
    recent: list[dict[str, Any]]


class ProviderInfo(BaseModel):
    provider: str
    model: str
    configured: bool
    active: bool


class HealthResponse(BaseModel):
    status: Literal["ok", "degraded"]
    version: str
    llm_providers: list[ProviderInfo]
    vector_store_backend: str
    embedding_backend: str


class StatsResponse(BaseModel):
    total_pages: int
    total_chunks: int
    recent_pages: int
    avg_chunks_per_page: float
    avg_summary_length: int


class DeleteResponse(BaseModel):
    deleted: bool
    id: int


class ErrorResponse(BaseModel):
    detail: Any
