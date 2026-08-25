import { useState } from "react";
import {
  AlertTriangle,
  CheckCircle,
  ChevronRight,
  Clock,
  Database,
  Globe,
  PenTool,
  RefreshCw,
  Search,
  Star,
} from "lucide-react";
import type { GlobalStats, PipelineLog, PipelineStage, StageName } from "../types";

interface PipelineTrackerProps {
  logs: PipelineLog[];
  currentStage: PipelineStage;
  query: string;
  stats?: GlobalStats | null;
  live?: boolean;
}

interface StageConfig {
  name: StageName;
  icon: typeof Search;
  accent: string;
  description: string;
}

const STAGES: StageConfig[] = [
  { name: "Planner", icon: Search, accent: "blue", description: "Formulates keyword phrases & search clusters." },
  { name: "Scraper", icon: Globe, accent: "cyan", description: "Executes distributed searches & parallel scraping." },
  { name: "Analyzer", icon: Database, accent: "purple", description: "Chunks text, deduplicates content, computes embeddings." },
  { name: "Writer", icon: PenTool, accent: "amber", description: "Synthesizes structured markdown report chapters." },
  { name: "Critic", icon: Star, accent: "emerald", description: "Validates facts and routes revisions before PDF export." },
];

const ACCENTS: Record<string, { runningBg: string; runningBorder: string; chip: string; dot: string }> = {
  blue: { runningBg: "bg-blue-950/20", runningBorder: "border-blue-500/70", chip: "bg-blue-500/20 text-blue-400", dot: "bg-blue-400" },
  cyan: { runningBg: "bg-cyan-950/20", runningBorder: "border-cyan-500/70", chip: "bg-cyan-500/20 text-cyan-400", dot: "bg-cyan-400" },
  purple: { runningBg: "bg-purple-950/20", runningBorder: "border-purple-500/70", chip: "bg-purple-500/20 text-purple-400", dot: "bg-purple-400" },
  amber: { runningBg: "bg-amber-950/20", runningBorder: "border-amber-500/70", chip: "bg-amber-500/20 text-amber-400", dot: "bg-amber-400" },
  emerald: { runningBg: "bg-emerald-950/20", runningBorder: "border-emerald-500/70", chip: "bg-emerald-500/20 text-emerald-400", dot: "bg-emerald-400" },
};

export default function PipelineTracker({ logs, currentStage, query, live = false }: PipelineTrackerProps) {
  const [scrapedUrls] = useState<string[]>([]);

  // Derive per-stage status from logs + current stage.
  const getStatusFor = (stageName: StageName): "pending" | "running" | "completed" | "failed" => {
    if (currentStage === "complete") return "completed";
    const log = logs.find((l) => l.stage === stageName);
    if (log) return log.status as "running" | "completed" | "failed";
    if (currentStage === stageName) return "running";
    if (currentStage === "idle") return "pending";
    const currentIdx = STAGES.findIndex((s) => s.name === currentStage);
    const targetIdx = STAGES.findIndex((s) => s.name === stageName);
    if (currentIdx !== -1 && targetIdx < currentIdx) return "completed";
    return "pending";
  };

  const getLogOutput = (stageName: StageName): string => {
    const log = [...logs].reverse().find((l) => l.stage === stageName);
    return log?.output ?? "";
  };

  const criticLog = [...logs].reverse().find((l) => l.stage === "Critic");
  const criticScoreMatch = criticLog?.output.match(/(\d+\.?\d*)\s*\/\s*10/);

  return (
    <div id="pipeline-tracker" className="glass-card rounded-xl p-4 mb-5 relative overflow-hidden">
      <div className="absolute top-0 right-0 w-64 h-64 bg-cyan-500/5 rounded-full blur-3xl pointer-events-none"></div>

      <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-4 gap-3">
        <div>
          <h2 className="text-sm font-bold text-white tracking-tight flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 bg-cyan-400 rounded-full animate-ping"></span>
            Agent Processing Pipeline
          </h2>
          <p className="text-[10px] text-slate-400 font-mono mt-0.5">
            {live ? "Live backend execution with revision loops" : "Simulated execution"} - "{query}"
          </p>
        </div>
        {isRunningState(currentStage) && (
          <div className="flex items-center gap-1.5 bg-cyan-950/40 border border-cyan-800/60 px-2.5 py-0.5 rounded-full text-[10px] text-cyan-400 font-mono">
            <RefreshCw className="w-3 h-3 animate-spin" />
            <span>Pipeline Active</span>
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-5 gap-4">
        {STAGES.map(({ name, icon: Icon, accent, description }) => {
          const status = getStatusFor(name);
          const colors = ACCENTS[accent];
          const output = getLogOutput(name);
          return (
            <div
              key={name}
              className={`p-3.5 rounded-lg border transition-all duration-200 ${
                status === "running"
                  ? `${colors.runningBg} ${colors.runningBorder} shadow-lg`
                  : status === "completed"
                    ? "bg-slate-900/40 border-emerald-900/50"
                    : status === "failed"
                      ? "bg-red-950/30 border-red-500/60"
                      : "bg-slate-950/30 border-slate-900/80 opacity-50"
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-1.5">
                  <div className={`p-1 rounded-md ${status === "running" ? colors.chip : "bg-slate-800 text-slate-400"}`}>
                    <Icon className="w-3.5 h-3.5" />
                  </div>
                  <span className="font-bold text-xs text-white">{name}</span>
                </div>
                {status === "completed" ? (
                  <CheckCircle className="w-4 h-4 text-emerald-400" />
                ) : status === "failed" ? (
                  <AlertTriangle className="w-4 h-4 text-red-400" />
                ) : status === "running" ? (
                  <span className={`w-1.5 h-1.5 rounded-full animate-ping ${colors.dot}`}></span>
                ) : (
                  <Clock className="w-3.5 h-3.5 text-slate-600" />
                )}
              </div>

              <p className="text-[11px] text-slate-400 leading-normal mb-2">{description}</p>

              {output && (
                <div
                  className={`text-[10px] font-mono pt-1.5 border-t border-slate-800/60 leading-snug ${
                    status === "failed" ? "text-red-300" : "text-slate-400"
                  }`}
                >
                  {status === "completed" && <span className="text-emerald-400 block mb-0.5">Done</span>}
                  {output}
                </div>
              )}

              {/* Scraper live URL feed */}
              {name === "Scraper" && status === "running" && scrapedUrls.length > 0 && (
                <div className="mt-1.5 space-y-0.5">
                  {scrapedUrls.slice(-3).map((url) => (
                    <p key={url} className="text-[9px] font-mono text-emerald-400 truncate">→ {url}</p>
                  ))}
                </div>
              )}

              {/* Critic score */}
              {name === "Critic" && (status === "completed" || criticScoreMatch) && criticScoreMatch && (
                <div className="mt-2 flex justify-between text-[10px] font-mono bg-slate-950/80 p-1 rounded border border-slate-800/50">
                  <span className="text-slate-400">Integrity:</span>
                  <span className="text-emerald-400 font-bold">{criticScoreMatch[1]}/10</span>
                </div>
              )}
            </div>
          );
        })}
      </div>

      <div className="hidden xl:flex items-center justify-center gap-2 mt-3 px-10 text-[10px] font-mono text-slate-600 flex-wrap">
        {STAGES.map(({ name }, i) => (
          <span key={name} className="flex items-center gap-2">
            <span>{name}</span>
            {i < STAGES.length - 1 && <ChevronRight className="w-3 h-3 text-slate-700" />}
          </span>
        ))}
        <ChevronRight className="w-3 h-3 text-slate-700" />
        <span className="text-emerald-500/80">Critic loop (revises if score &lt; 7)</span>
        <ChevronRight className="w-3 h-3 text-slate-700" />
        <span className="text-cyan-400 font-bold">PDF Export</span>
      </div>
    </div>
  );
}

function isRunningState(stage: PipelineStage): boolean {
  return !["idle", "complete"].includes(stage);
}
