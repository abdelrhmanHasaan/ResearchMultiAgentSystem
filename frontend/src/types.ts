export type ResearchType = "quick" | "deep" | "academic";
export type DetailLevel = "brief" | "standard" | "comprehensive";

export type StageName = "Planner" | "Scraper" | "Analyzer" | "Writer" | "Critic";
export type StageStatus = "pending" | "running" | "completed" | "failed";
export type PipelineStage = StageName | "complete" | "idle";

export interface ResearchRequest {
  query: string;
  research_type: ResearchType;
  detail_level: DetailLevel;
}

export interface PipelineStats {
  total_pages: number;
  total_chunks: number;
  recent_pages?: number | null;
  avg_chunks_per_page: number;
}

export interface PipelineLog {
  stage: string;
  status: string;
  output: string;
}

export interface ResearchResponse {
  status: "success" | "error";
  query: string;
  report?: string;
  pdf?: string;
  report_id?: number | null;
  critic_score?: number | null;
  sources?: SourceRef[];
  usage?: RunUsage | null;
  error?: string | null;
  stats?: PipelineStats;
  elapsed_seconds?: number;
  logs: PipelineLog[];
}

export interface HistoryItem {
  id: number;
  topic: string;
  timestamp: string;
  pdf_path: string;
  metadata: {
    pages_processed: number;
    chunks_included: number;
    detail_level: string;
  };
  critic_score?: number | null;
}

export interface StoredReport extends HistoryItem {
  report: string;
}

export interface SourceRef {
  url?: string | null;
  title?: string | null;
}

export interface RunUsage {
  calls: number;
  prompt_tokens: number;
  completion_tokens: number;
  total_tokens: number;
  estimated_cost_usd: number;
  per_provider: Array<{ provider: string; model: string; calls: number; tokens: number; cost_usd: number }>;
}

export interface UsageSummary {
  totals: {
    calls: number;
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number;
    total_cost_usd: number;
    avg_latency_ms: number;
    errors: number;
  };
  by_provider: Array<{
    provider: string;
    model: string;
    calls: number;
    total_tokens: number;
    prompt_tokens: number;
    completion_tokens: number;
    total_cost_usd: number;
    avg_latency_ms: number;
  }>;
  by_stage: Array<{ stage: string; calls: number; total_tokens: number; total_cost_usd: number }>;
  recent: Array<{
    id: number;
    created_at: string;
    provider: string;
    model: string;
    stage: string;
    prompt_tokens: number | null;
    completion_tokens: number | null;
    total_tokens: number | null;
    cost_usd: number | null;
    latency_ms: number | null;
    status: string;
  }>;
}

export interface GlobalStats {
  total_pages: number;
  total_chunks: number;
  recent_pages?: number | null;
  avg_chunks_per_page: number;
  avg_summary_length: number;
}

export interface ProviderInfo {
  provider: string;
  model: string;
  configured: boolean;
  active: boolean;
}

export interface HealthResponse {
  status: "ok" | "degraded";
  version: string;
  llm_providers: ProviderInfo[];
  vector_store_backend: string;
  embedding_backend: string;
}

export interface StatsResponse {
  total_pages: number;
  total_chunks: number;
  recent_pages: number;
  avg_chunks_per_page: number;
  avg_summary_length: number;
}
