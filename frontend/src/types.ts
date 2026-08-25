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
