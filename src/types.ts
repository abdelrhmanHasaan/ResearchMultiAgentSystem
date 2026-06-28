export type ResearchType = "quick" | "deep" | "academic";
export type DetailLevel = "brief" | "standard" | "comprehensive";

export interface ResearchRequest {
  query: string;
  research_type: ResearchType;
  detail_level: DetailLevel;
}

export interface PipelineStats {
  total_pages: number;
  total_chunks: number;
  recent_pages?: number;
  avg_chunks_per_page: number;
}

export interface PipelineLog {
  stage: "Planner" | "Scraper" | "Analyzer" | "Writer" | "Critic";
  status: "pending" | "running" | "completed" | "failed";
  output: string;
}

export interface ResearchResponse {
  status: "success" | "error";
  query: string;
  report: string;
  pdf: string;
  stats: PipelineStats;
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
  avg_chunks_per_page: number;
  avg_summary_length: number;
}
