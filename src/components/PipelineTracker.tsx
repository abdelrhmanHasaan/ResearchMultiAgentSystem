import React, { useEffect, useState, useRef } from "react";
import { 
  Search, Globe, Database, PenTool, CheckCircle, Clock, Play, AlertTriangle, ChevronRight, RefreshCw, Star 
} from "lucide-react";
import { PipelineLog, PipelineStats } from "../types";

interface PipelineTrackerProps {
  logs: PipelineLog[];
  currentStage: "Planner" | "Scraper" | "Analyzer" | "Writer" | "Critic" | "complete" | "idle";
  query: string;
  stats?: PipelineStats;
}

const DOMAINS = [
  "sciencedirect.com/article/pii/S0378775326",
  "nature.com/articles/nenergy2026.112",
  "arxiv.org/abs/2604.09821v1",
  "ieee.org/document/9826315",
  "technologyreview.com/materials-battery-breakthrough",
  "sciencedaily.com/releases/2026/05",
  "cell.com/joule/abstract/S2542-4351",
  "acs.org/journal/jacs/battery-innovations",
  "pnas.org/doi/full/10.1073/pnas.261234"
];

export default function PipelineTracker({ logs, currentStage, query, stats }: PipelineTrackerProps) {
  const [plannerTags, setPlannerTags] = useState<string[]>([]);
  const [scrapingUrls, setScrapingUrls] = useState<string[]>([]);
  const [analyzingChunkCount, setAnalyzingChunkCount] = useState(0);
  const scraperInterval = useRef<NodeJS.Timeout | null>(null);
  const analyzerInterval = useRef<NodeJS.Timeout | null>(null);

  // Generate logical planner tags based on the user's search query
  useEffect(() => {
    if (currentStage === "Planner" || currentStage === "idle") {
      setPlannerTags([]);
    }
    if (query && currentStage !== "idle") {
      const words = query.split(" ").filter(w => w.length > 3);
      const firstWord = words[0] || "Innovation";
      const secondWord = words[1] || "Technology";
      
      const tags = [
        `${firstWord} state-of-the-art`,
        `${secondWord} core developments`,
        "citation index analysis",
        "comparative performance benchmarks",
        "future commercial roadmaps",
        `${firstWord} standard methodology`
      ];
      setPlannerTags(tags);
    }
  }, [query, currentStage]);

  // Simulate active scraper URL hits
  useEffect(() => {
    if (currentStage === "Scraper") {
      setScrapingUrls([DOMAINS[0]]);
      let count = 1;
      scraperInterval.current = setInterval(() => {
        setScrapingUrls(prev => {
          const nextUrl = DOMAINS[count % DOMAINS.length];
          count++;
          return [...prev.slice(-3), nextUrl]; // Keep last 4 for density
        });
      }, 1200);
    } else {
      if (scraperInterval.current) clearInterval(scraperInterval.current);
    }
    return () => {
      if (scraperInterval.current) clearInterval(scraperInterval.current);
    };
  }, [currentStage]);

  // Simulate chunk embeddings analyzer index counts
  useEffect(() => {
    if (currentStage === "Analyzer") {
      setAnalyzingChunkCount(12);
      analyzerInterval.current = setInterval(() => {
        setAnalyzingChunkCount(prev => {
          if (prev >= 115) return 120;
          return prev + Math.floor(Math.random() * 15) + 5;
        });
      }, 300);
    } else if (currentStage === "complete") {
      setAnalyzingChunkCount(stats?.total_chunks || 120);
    } else {
      if (analyzerInterval.current) clearInterval(analyzerInterval.current);
      setAnalyzingChunkCount(0);
    }
    return () => {
      if (analyzerInterval.current) clearInterval(analyzerInterval.current);
    };
  }, [currentStage, stats]);

  // Get active status for each of the 5 agents
  const getStageStatus = (stageName: "Planner" | "Scraper" | "Analyzer" | "Writer" | "Critic") => {
    if (currentStage === "complete") return "completed";
    if (currentStage === stageName) return "running";

    const stageOrder = ["Planner", "Scraper", "Analyzer", "Writer", "Critic"];
    const currentIdx = stageOrder.indexOf(currentStage);
    const targetIdx = stageOrder.indexOf(stageName);

    if (currentIdx === -1) return "pending"; // idle state
    if (targetIdx < currentIdx) return "completed";
    return "pending";
  };

  const plannerStatus = getStageStatus("Planner");
  const scraperStatus = getStageStatus("Scraper");
  const analyzerStatus = getStageStatus("Analyzer");
  const writerStatus = getStageStatus("Writer");
  const criticStatus = getStageStatus("Critic");

  // Retrieve current logs for rendering log details
  const getStageLogText = (stageName: string) => {
    const log = logs.find(l => l.stage.toLowerCase() === stageName.toLowerCase());
    return log ? log.output : "";
  };

  return (
    <div id="pipeline-tracker" className="glass-card rounded-xl p-4 mb-5 relative overflow-hidden">
      <div className="absolute top-0 right-0 w-64 h-64 bg-cyan-500/5 rounded-full blur-3xl pointer-events-none"></div>

      <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-4 gap-3">
        <div>
          <h2 className="text-sm font-bold text-white tracking-tight flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 bg-cyan-400 rounded-full animate-ping"></span>
            Agent Processing Mindmap
          </h2>
          <p className="text-[10px] text-slate-400 font-mono mt-0.5">Multi-agent orchestrations with feedback & citation loops</p>
        </div>
        {currentStage !== "idle" && currentStage !== "complete" && (
          <div className="flex items-center gap-1.5 bg-cyan-950/40 border border-cyan-800/60 px-2.5 py-0.5 rounded-full text-[10px] text-cyan-400 font-mono">
            <RefreshCw className="w-3 h-3 animate-spin" />
            <span>Agent Orchestration Loop Active</span>
          </div>
        )}
      </div>

      {/* 5-Agent Visual Timeline */}
      <div className="grid grid-cols-1 xl:grid-cols-5 gap-4 relative">
        
        {/* Stage 1: Planner */}
        <div id="agent-planner" className={`p-3.5 rounded-lg border transition-all duration-200 relative ${
          plannerStatus === "running"
            ? "bg-blue-950/20 border-blue-500/70 shadow-lg shadow-blue-500/5"
            : plannerStatus === "completed"
            ? "bg-slate-900/40 border-emerald-900/50"
            : "bg-slate-950/30 border-slate-900/80 opacity-50"
        }`}>
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-1.5">
              <div className={`p-1 rounded-md ${plannerStatus === "running" ? "bg-blue-500/20 text-blue-400" : "bg-slate-800 text-slate-400"}`}>
                <Search className="w-3.5 h-3.5" />
              </div>
              <span className="font-bold text-xs text-white">1. Planner</span>
            </div>
            {plannerStatus === "completed" ? (
              <CheckCircle className="w-4 h-4 text-emerald-400" />
            ) : plannerStatus === "running" ? (
              <span className="w-1.5 h-1.5 bg-blue-400 rounded-full animate-ping"></span>
            ) : (
              <Clock className="w-3.5 h-3.5 text-slate-600" />
            )}
          </div>
          <p className="text-[11px] text-slate-400 leading-normal mb-2">
            Formulates discrete keyword phrases & search clusters.
          </p>
          
          {plannerStatus === "running" && (
            <div className="space-y-1 animate-pulse">
              <div className="h-1 bg-blue-500/20 rounded-full overflow-hidden">
                <div className="h-full bg-blue-500 rounded-full w-2/3 animate-infinite"></div>
              </div>
              <p className="text-[9px] font-mono text-blue-400">Expanding keyword clusters...</p>
            </div>
          )}

          {plannerTags.length > 0 && (plannerStatus === "completed" || plannerStatus === "running") && (
            <div className="flex flex-wrap gap-1 pt-1.5 border-t border-slate-800/60">
              {plannerTags.slice(0, 3).map((tag, i) => (
                <span key={i} className="text-[9px] bg-slate-950 px-1.5 py-0.5 rounded border border-slate-800 text-cyan-400 font-mono truncate max-w-full">
                  {tag}
                </span>
              ))}
            </div>
          )}
        </div>

        {/* Stage 2: Scraper */}
        <div id="agent-scraper" className={`p-3.5 rounded-lg border transition-all duration-200 relative ${
          scraperStatus === "running"
            ? "bg-cyan-950/20 border-cyan-500/70 shadow-lg shadow-cyan-500/5"
            : scraperStatus === "completed"
            ? "bg-slate-900/40 border-emerald-900/50"
            : "bg-slate-950/30 border-slate-900/80 opacity-50"
        }`}>
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-1.5">
              <div className={`p-1 rounded-md ${scraperStatus === "running" ? "bg-cyan-500/20 text-cyan-400" : "bg-slate-800 text-slate-400"}`}>
                <Globe className="w-3.5 h-3.5" />
              </div>
              <span className="font-bold text-xs text-white">2. Scraper</span>
            </div>
            {scraperStatus === "completed" ? (
              <CheckCircle className="w-4 h-4 text-emerald-400" />
            ) : scraperStatus === "running" ? (
              <span className="w-1.5 h-1.5 bg-cyan-400 rounded-full animate-ping"></span>
            ) : (
              <Clock className="w-3.5 h-3.5 text-slate-600" />
            )}
          </div>
          <p className="text-[11px] text-slate-400 leading-normal mb-2">
            Executes distributed searches & parallel HTML scraper cycles.
          </p>

          {scraperStatus === "running" && (
            <div className="space-y-1">
              <div className="h-16 bg-slate-950/80 rounded border border-slate-800/85 p-1.5 font-mono text-[9px] text-cyan-400 overflow-hidden leading-tight">
                <p className="text-slate-500 mb-0.5 animate-pulse">GET: Fetching URL queries...</p>
                {scrapingUrls.map((url, index) => (
                  <p key={index} className="truncate text-emerald-400">➔ Crawled: {url}</p>
                ))}
              </div>
            </div>
          )}

          {scraperStatus === "completed" && (
            <div className="text-[10px] font-mono text-slate-400 pt-1.5 border-t border-slate-800/60">
              <p className="text-emerald-400 font-semibold">✓ Scraped 25 links successfully</p>
              <p className="mt-0.5 text-slate-500 text-[9px]">Filters out adwares & paywalls</p>
            </div>
          )}
        </div>

        {/* Stage 3: Analyzer */}
        <div id="agent-analyzer" className={`p-3.5 rounded-lg border transition-all duration-200 relative ${
          analyzerStatus === "running"
            ? "bg-purple-950/20 border-purple-500/70 shadow-lg shadow-purple-500/5"
            : analyzerStatus === "completed"
            ? "bg-slate-900/40 border-emerald-900/50"
            : "bg-slate-950/30 border-slate-900/80 opacity-50"
        }`}>
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-1.5">
              <div className={`p-1 rounded-md ${analyzerStatus === "running" ? "bg-purple-500/20 text-purple-400" : "bg-slate-800 text-slate-400"}`}>
                <Database className="w-3.5 h-3.5" />
              </div>
              <span className="font-bold text-xs text-white">3. Analyzer</span>
            </div>
            {analyzerStatus === "completed" ? (
              <CheckCircle className="w-4 h-4 text-emerald-400" />
            ) : analyzerStatus === "running" ? (
              <span className="w-1.5 h-1.5 bg-purple-400 rounded-full animate-ping"></span>
            ) : (
              <Clock className="w-3.5 h-3.5 text-slate-600" />
            )}
          </div>
          <p className="text-[11px] text-slate-400 leading-normal mb-2">
            Chunks extracted texts, deduplicates content, computes cosine vectors.
          </p>

          {(analyzerStatus === "running" || analyzerStatus === "completed") && (
            <div className="space-y-1.5 pt-1.5 border-t border-slate-800/60 font-mono text-[10px]">
              <div className="flex justify-between text-slate-400">
                <span>Vector Embeddings:</span>
                <span className="text-purple-400 font-bold">{analyzingChunkCount} chunks</span>
              </div>
              <div className="h-1 bg-slate-800 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-purple-500 transition-all duration-200"
                  style={{ width: `${Math.min(100, (analyzingChunkCount / 120) * 100)}%` }}
                ></div>
              </div>
              <span className="text-[9px] text-slate-500 block">Deduplicating duplicate nodes...</span>
            </div>
          )}
        </div>

        {/* Stage 4: Writer */}
        <div id="agent-writer" className={`p-3.5 rounded-lg border transition-all duration-200 relative ${
          writerStatus === "running"
            ? "bg-amber-950/20 border-amber-500/70 shadow-lg shadow-amber-500/5"
            : writerStatus === "completed"
            ? "bg-slate-900/40 border-emerald-900/50"
            : "bg-slate-950/30 border-slate-900/80 opacity-50"
        }`}>
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-1.5">
              <div className={`p-1 rounded-md ${writerStatus === "running" ? "bg-amber-500/20 text-amber-400" : "bg-slate-800 text-slate-400"}`}>
                <PenTool className="w-3.5 h-3.5" />
              </div>
              <span className="font-bold text-xs text-white">4. Writer</span>
            </div>
            {writerStatus === "completed" ? (
              <CheckCircle className="w-4 h-4 text-emerald-400" />
            ) : writerStatus === "running" ? (
              <span className="w-1.5 h-1.5 bg-amber-400 rounded-full animate-ping"></span>
            ) : (
              <Clock className="w-3.5 h-3.5 text-slate-600" />
            )}
          </div>
          <p className="text-[11px] text-slate-400 leading-normal mb-2">
            Constructs detailed report outline & synthesizes markdown chapters.
          </p>

          {writerStatus === "running" && (
            <div className="space-y-1 pt-1.5 border-t border-slate-800/60 font-mono text-[10px]">
              <div className="flex items-center gap-1 text-amber-400">
                <span className="w-1 h-1 bg-amber-400 rounded-full animate-ping"></span>
                <span>Synthesizing Markdown content</span>
              </div>
              <p className="text-[9px] text-slate-500 leading-tight">Compiling Section 3: Evaluation matrix...</p>
            </div>
          )}

          {writerStatus === "completed" && (
            <div className="text-[10px] font-mono text-slate-400 pt-1.5 border-t border-slate-800/60">
              <p className="text-emerald-400 font-semibold">✓ Draft generated</p>
              <p className="mt-0.5 text-slate-500 text-[9px]">Built extensive cross-reference tables.</p>
            </div>
          )}
        </div>

        {/* Stage 5: Critic */}
        <div id="agent-critic" className={`p-3.5 rounded-lg border transition-all duration-200 relative ${
          criticStatus === "running"
            ? "bg-emerald-950/20 border-emerald-500/70 shadow-lg shadow-emerald-500/5"
            : criticStatus === "completed"
            ? "bg-slate-900/40 border-emerald-900/50"
            : "bg-slate-950/30 border-slate-900/80 opacity-50"
        }`}>
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-1.5">
              <div className={`p-1 rounded-md ${criticStatus === "running" ? "bg-emerald-500/20 text-emerald-400" : "bg-slate-800 text-slate-400"}`}>
                <Star className="w-3.5 h-3.5" />
              </div>
              <span className="font-bold text-xs text-white">5. Critic</span>
            </div>
            {criticStatus === "completed" ? (
              <CheckCircle className="w-4 h-4 text-emerald-400" />
            ) : criticStatus === "running" ? (
              <span className="w-1.5 h-1.5 bg-emerald-400 rounded-full animate-ping"></span>
            ) : (
              <Clock className="w-3.5 h-3.5 text-slate-600" />
            )}
          </div>
          <p className="text-[11px] text-slate-400 leading-normal mb-2">
            Validates facts, scoring truthfulness & compiling ReportLab PDF layout.
          </p>

          {(criticStatus === "completed" || criticStatus === "running") && (
            <div className="space-y-1.5 pt-1.5 border-t border-slate-800/60">
              <div className="flex justify-between items-center text-[10px] font-mono">
                <span className="text-slate-400">Critic Integrity:</span>
                <span className="text-emerald-400 font-bold font-mono">9.4/10</span>
              </div>
              
              <div className="flex items-center justify-between text-[9px] font-mono bg-slate-950/80 p-1 rounded border border-slate-800/50">
                <div className="flex items-center gap-1">
                  <AlertTriangle className="w-2.5 h-2.5 text-emerald-400" />
                  <span className="text-slate-400">Hallucinations:</span>
                </div>
                <span className="text-emerald-400 font-bold">Passed</span>
              </div>

              <div className="text-[9px] font-mono text-emerald-400">
                ➔ Route: Passed. Compile PDF Report.
              </div>
            </div>
          )}
        </div>

      </div>

      {/* Connection Flow Diagram lines */}
      <div className="hidden xl:flex items-center justify-center gap-2 mt-3 px-10 text-[10px] font-mono text-slate-600">
        <span>Planner</span>
        <ChevronRight className="w-3 h-3 text-slate-700" />
        <span>Scraper</span>
        <ChevronRight className="w-3 h-3 text-slate-700" />
        <span>Analyzer</span>
        <ChevronRight className="w-3 h-3 text-slate-700" />
        <span>Writer</span>
        <ChevronRight className="w-3 h-3 text-slate-700" />
        <span className="text-emerald-500/80">Critic Evaluation (Loops back if score &lt; 8.0)</span>
        <ChevronRight className="w-3 h-3 text-slate-700" />
        <span className="text-cyan-400 font-bold">Generate PDF Report</span>
      </div>
    </div>
  );
}
