/**
 * Central API client.
 *
 * All backend communication goes through this module. The base URL defaults to
 * same-origin (Vite dev proxy / unified deployment) and can be overridden with
 * VITE_API_URL for split deployments.
 */
import type {
  HealthResponse,
  HistoryItem,
  PipelineStats,
  ResearchRequest,
  ResearchResponse,
  StatsResponse,
} from "../types";

export const API_BASE: string = (import.meta.env?.VITE_API_URL as string | undefined)?.replace(/\/$/, "") ?? "";

export function pdfUrl(filename: string): string {
  return `${API_BASE}/api/pdf/${encodeURIComponent(filename)}`;
}

async function fetchJson<T>(path: string, init?: RequestInit, timeoutMs = 15000): Promise<T> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  try {
    const response = await fetch(`${API_BASE}${path}`, { ...init, signal: controller.signal });
    if (!response.ok) {
      const body = await response.text().catch(() => "");
      throw new Error(`HTTP ${response.status}: ${body || response.statusText}`);
    }
    return (await response.json()) as T;
  } finally {
    clearTimeout(timer);
  }
}

export interface StageEvent {
  type: "stage";
  stage: string;
  status: string;
  output: string;
}

export interface ResultEvent extends ResearchResponse {
  type: "result";
}

export type StreamEvent = StageEvent | ResultEvent;

/**
 * Runs a research query. Streams live stage events when the backend supports
 * SSE streaming; transparently falls back to the blocking endpoint otherwise.
 */
export async function runResearch(
  payload: ResearchRequest,
  onStageEvent?: (event: StageEvent) => void,
): Promise<ResearchResponse> {
  try {
    return await streamResearch(payload, onStageEvent);
  } catch (streamError) {
    console.warn("Streaming unavailable, falling back to blocking request:", streamError);
    return runResearchBlocking(payload);
  }
}

async function streamResearch(
  payload: ResearchRequest,
  onStageEvent?: (event: StageEvent) => void,
): Promise<ResearchResponse> {
  const response = await fetch(`${API_BASE}/api/research/stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!response.ok || !response.body) {
    throw new Error(`Stream endpoint returned HTTP ${response.status}`);
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  let result: ResearchResponse | null = null;

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });

    let separatorIndex: number;
    while ((separatorIndex = buffer.indexOf("\n\n")) !== -1) {
      const rawEvent = buffer.slice(0, separatorIndex).trim();
      buffer = buffer.slice(separatorIndex + 2);
      if (!rawEvent.startsWith("data:")) continue;

      const data = rawEvent.slice(5).trim();
      if (data === "[DONE]") continue;

      let event: StreamEvent;
      try {
        event = JSON.parse(data) as StreamEvent;
      } catch {
        continue;
      }

      if (event.type === "stage") {
        onStageEvent?.(event);
      } else if (event.type === "result") {
        result = event;
      }
    }
  }

  if (!result) throw new Error("Stream ended without a result event");
  return result;
}

async function runResearchBlocking(payload: ResearchRequest): Promise<ResearchResponse> {
  return fetchJson<ResearchResponse>("/api/research", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

export const api = {
  health: () => fetchJson<HealthResponse>("/api/health", undefined, 5000),
  stats: () => fetchJson<StatsResponse>("/api/stats"),
  history: () => fetchJson<HistoryItem[]>("/api/history"),
  deleteHistoryItem: (id: number) =>
    fetchJson<{ deleted: boolean; id: number }>(`/api/history/${id}`, { method: "DELETE" }),
  runResearch,
};

export type { PipelineStats };
