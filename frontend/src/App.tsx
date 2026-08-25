import { useCallback, useEffect, useRef, useState } from "react";
import { BookOpen, Sparkles, ToggleLeft, ToggleRight, WifiOff } from "lucide-react";
import type {
  DetailLevel,
  GlobalStats,
  HistoryItem,
  PipelineLog,
  PipelineStage,
  ResearchType,
  StageName,
} from "./types";
import { api } from "./lib/api";
import StatsGrid from "./components/StatsGrid";
import ResearchConfig from "./components/ResearchConfig";
import PipelineTracker from "./components/PipelineTracker";
import Workspace from "./components/Workspace";
import HistorySidebar from "./components/HistorySidebar";
import { DEMO_REPORTS, DEMO_STAGES, pickDemoReport } from "./mocks/demoReports";

const EMPTY_STATS: GlobalStats = {
  total_pages: 0,
  total_chunks: 0,
  recent_pages: 0,
  avg_chunks_per_page: 0,
  avg_summary_length: 0,
};

const STAGE_ORDER: StageName[] = ["Planner", "Scraper", "Analyzer", "Writer", "Critic"];
const sleep = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

export default function App() {
  // Configuration
  const [query, setQuery] = useState("");
  const [researchType, setResearchType] = useState<ResearchType>("deep");
  const [detailLevel, setDetailLevel] = useState<DetailLevel>("standard");

  // Connectivity
  const [backendOnline, setBackendOnline] = useState(false);
  const [demoMode, setDemoMode] = useState(true);
  const backendOnlineRef = useRef(false);
  backendOnlineRef.current = backendOnline;

  // Data
  const [globalStats, setGlobalStats] = useState<GlobalStats>(EMPTY_STATS);
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [sidebarOpen, setSidebarOpen] = useState(true);

  // Active research run
  const [isRunning, setIsRunning] = useState(false);
  const [currentStage, setCurrentStage] = useState<PipelineStage>("idle");
  const [logs, setLogs] = useState<PipelineLog[]>([]);
  const [reportMarkdown, setReportMarkdown] = useState("");
  const [pdfFilename, setPdfFilename] = useState("");
  const [activeQuery, setActiveQuery] = useState("");
  const [runStats, setRunStats] = useState<GlobalStats | null>(null);

  // ------------------------------------------------------------------
  // Backend sync
  // ------------------------------------------------------------------
  const refreshBackendState = useCallback(async () => {
    try {
      const [stats, historyItems] = await Promise.all([api.stats(), api.history()]);
      setGlobalStats(stats);
      setHistory(historyItems);
      localStorage.setItem("research_portal_stats", JSON.stringify(stats));
      localStorage.setItem("research_portal_history", JSON.stringify(historyItems));
    } catch (error) {
      console.warn("Failed to sync backend state:", error);
    }
  }, []);

  const checkBackendHealth = useCallback(async (): Promise<boolean> => {
    try {
      await api.health();
      setBackendOnline(true);
      return true;
    } catch {
      setBackendOnline(false);
      return false;
    }
  }, []);

  useEffect(() => {
    // Restore local cache first for instant paint.
    try {
      const cachedHistory = localStorage.getItem("research_portal_history");
      if (cachedHistory) setHistory(JSON.parse(cachedHistory));
      const cachedStats = localStorage.getItem("research_portal_stats");
      if (cachedStats) setGlobalStats(JSON.parse(cachedStats));
    } catch {
      /* corrupted cache - ignore */
    }

    void checkBackendHealth().then((online) => {
      if (online) {
        setDemoMode(false);
        void refreshBackendState();
      } else {
        // Seed the demo workspace so the UI is explorable offline.
        const demo = pickDemoReport("solid-state battery technology");
        setReportMarkdown(demo.report);
        setActiveQuery("Solid-state battery technology (demo)");
        setCurrentStage("complete");
        setRunStats({ ...EMPTY_STATS, ...demo.stats });
        setDemoMode(true);
      }
    });
  }, [checkBackendHealth, refreshBackendState]);

  const toggleConnection = async () => {
    if (!demoMode) {
      setDemoMode(true);
      return;
    }
    const online = await checkBackendHealth();
    if (online) {
      setDemoMode(false);
      await refreshBackendState();
    } else {
      alert(
        "Could not reach the FastAPI backend.\n\n" +
          "Start it with:\n  cd backend\n  pip install -r requirements.txt\n  uvicorn app.main:app --port 8679"
      );
    }
  };

  const handleClearHistory = () => {
    setHistory([]);
    localStorage.removeItem("research_portal_history");
  };

  const handleDeleteHistoryItem = async (id: number) => {
    if (backendOnlineRef.current && !demoMode) {
      try {
        await api.deleteHistoryItem(id);
      } catch (error) {
        console.warn("Backend delete failed:", error);
      }
    }
    const next = history.filter((item) => item.id !== id);
    setHistory(next);
    localStorage.setItem("research_portal_history", JSON.stringify(next));
  };

  const handleSelectHistoryItem = (item: HistoryItem) => {
    // Prefer matching demo content when available, otherwise render a summary.
    const lowerTopic = item.topic.toLowerCase();
    let markdown = `# ${item.topic}\n\n*Generated on ${new Date(item.timestamp).toLocaleString()} with detail level **${item.metadata.detail_level}**.*\n\n- Sources processed: ${item.metadata.pages_processed}\n- Chunks indexed: ${item.metadata.chunks_included}\n`;
    for (const key of Object.keys(DEMO_REPORTS)) {
      if (lowerTopic.includes(key.split(" ")[0])) {
        markdown = DEMO_REPORTS[key].report;
        break;
      }
    }
    setReportMarkdown(markdown);
    setActiveQuery(item.topic);
    setPdfFilename(item.pdf_path);
    setRunStats({
      ...EMPTY_STATS,
      total_pages: item.metadata.pages_processed,
      total_chunks: item.metadata.chunks_included,
    });
    setCurrentStage("complete");
  };

  // ------------------------------------------------------------------
  // Research execution
  // ------------------------------------------------------------------
  const upsertLog = (stage: string, status: string, output: string) => {
    setLogs((prev) => {
      const rest = prev.filter((log) => log.stage !== stage);
      return [...rest, { stage, status, output }];
    });
  };

  const runDemoPipeline = async () => {
    for (let i = 0; i < STAGE_ORDER.length; i++) {
      const stage = STAGE_ORDER[i];
      setCurrentStage(stage as PipelineStage);
      upsertLog(stage, "running", `Simulating ${stage.toLowerCase()} stage...`);
      await sleep(1400);
      upsertLog(stage, "completed", DEMO_STAGES[i].output);
    }
    await sleep(600);

    const demo = pickDemoReport(query);
    setReportMarkdown(demo.report);
    setPdfFilename(`demo_report_${Date.now()}.pdf`);
    setRunStats({ ...EMPTY_STATS, ...demo.stats });
    setCurrentStage("complete");

    const newItem: HistoryItem = {
      id: Date.now(),
      topic: query,
      timestamp: new Date().toISOString(),
      pdf_path: `demo_report_${Date.now()}.pdf`,
      metadata: { pages_processed: demo.stats.total_pages, chunks_included: demo.stats.total_chunks, detail_level: detailLevel },
    };
    setHistory((prev) => [newItem, ...prev]);
    localStorage.setItem("research_portal_history", JSON.stringify([newItem, ...history]));
  };

  const handleLaunchResearch = async () => {
    if (!query.trim() || isRunning) return;

    setIsRunning(true);
    setLogs([]);
    setReportMarkdown("");
    setRunStats(null);
    setCurrentStage("Planner");
    setActiveQuery(query);

    if (demoMode) {
      await runDemoPipeline();
      setIsRunning(false);
      setQuery("");
      return;
    }

    try {
      const result = await api.runResearch(
        { query: query.trim(), research_type: researchType, detail_level: detailLevel },
        (event) => {
          setCurrentStage(event.stage as PipelineStage);
          upsertLog(event.stage, event.status, event.output);
        },
      );

      if (result.status === "success") {
        setReportMarkdown(result.report || "");
        setPdfFilename(result.pdf || "");
        setRunStats({ ...EMPTY_STATS, ...(result.stats ?? {}) });
        setLogs(result.logs ?? []);
        setCurrentStage("complete");
        await refreshBackendState();
      } else {
        upsertLog("Critic", "failed", result.error || "Pipeline reported an internal failure.");
        setCurrentStage("Critic");
      }
    } catch (error) {
      console.error(error);
      alert(
        `Failed to communicate with the backend.\n${error instanceof Error ? error.message : error}\n\n` +
          "Switching to demo mode so you can keep exploring the UI."
      );
      setDemoMode(true);
      setBackendOnline(false);
    } finally {
      setIsRunning(false);
    }
  };

  // ------------------------------------------------------------------
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 font-sans relative pb-16">
      {/* Decorative grid mesh */}
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#0f172a_1px,transparent_1px),linear-gradient(to_bottom,#0f172a_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_0%,#000_70%,transparent_100%)] pointer-events-none"></div>

      {/* Demo banner */}
      {demoMode && (
        <div className="bg-slate-900 border-b border-cyan-500/20 py-2.5 px-6 text-center text-xs relative z-30">
          <div className="max-w-7xl mx-auto flex items-center justify-center gap-2 flex-wrap">
            <WifiOff className="w-3.5 h-3.5 text-cyan-400" />
            <span className="font-mono text-cyan-400 font-bold">Demo Mode</span>
            <span className="text-slate-400">
              | Simulated pipeline output. Start the FastAPI backend and press "Connect" for real research.
            </span>
          </div>
        </div>
      )}

      {/* Header */}
      <header className="bg-slate-950/80 backdrop-blur-md border-b border-slate-900 sticky top-0 z-30 px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="relative flex items-center justify-center">
              <div className="absolute inset-0 bg-cyan-500/30 rounded-lg blur"></div>
              <div className="relative p-2.5 bg-slate-900 border border-slate-800 rounded-lg text-cyan-400 font-bold">
                <BookOpen className="w-5 h-5" />
              </div>
            </div>
            <div>
              <h1 className="text-lg font-bold text-white tracking-tight flex items-center gap-2">
                Autonomous Research Portal
                <span className="text-[10px] px-2 py-0.5 bg-blue-950 text-blue-400 border border-blue-800 rounded-full font-mono uppercase">
                  v4
                </span>
              </h1>
              <p className="text-[10px] text-slate-400 font-mono tracking-wider">
                MULTI-AGENT RESEARCH PIPELINE
              </p>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <div className="hidden md:flex items-center gap-2 bg-slate-900/60 px-3 py-1.5 rounded-xl border border-slate-800 text-xs">
              <span
                className={`w-2 h-2 rounded-full ${
                  backendOnline ? "bg-emerald-400 animate-pulse" : "bg-red-400"
                }`}
              ></span>
              <span className="font-mono text-slate-300">
                {backendOnline ? "FastAPI: ONLINE" : "FastAPI: OFFLINE"}
              </span>
            </div>

            <button
              onClick={toggleConnection}
              className={`px-4 py-2 rounded-xl text-xs font-semibold border flex items-center gap-2 transition-all cursor-pointer ${
                demoMode
                  ? "bg-slate-900 border-slate-800 text-cyan-400 hover:text-cyan-300"
                  : "bg-emerald-950/20 border-emerald-800/60 text-emerald-400"
              }`}
            >
              <span>{demoMode ? "Connect Backend" : "Live Connection"}</span>
              {demoMode ? (
                <ToggleLeft className="w-5 h-5" />
              ) : (
                <ToggleRight className="w-5 h-5" />
              )}
            </button>
          </div>
        </div>
      </header>

      {/* Main layout */}
      <main className={`max-w-7xl mx-auto px-6 pt-8 transition-all duration-300 ${sidebarOpen ? "xl:pr-[380px]" : ""}`}>
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2">
            Scientific Synthesis Workspace
            <Sparkles className="w-5 h-5 text-cyan-400" />
          </h2>
          <p className="text-sm text-slate-400 mt-1">
            Query the web through five autonomous agents - planner, scraper, analyzer, writer and critic -
            and download publication-ready PDF reports.
          </p>
        </div>

        <StatsGrid stats={globalStats} loading={isRunning && !demoMode && !globalStats.total_pages} />

        <ResearchConfig
          query={query}
          setQuery={setQuery}
          researchType={researchType}
          setResearchType={setResearchType}
          detailLevel={detailLevel}
          setDetailLevel={setDetailLevel}
          onRun={handleLaunchResearch}
          isRunning={isRunning}
        />

        {(isRunning || currentStage === "complete") && (
          <PipelineTracker logs={logs} currentStage={currentStage} query={activeQuery} stats={runStats} live={!demoMode} />
        )}

        {reportMarkdown && (
          <Workspace
            reportMarkdown={reportMarkdown}
            pdfFilename={pdfFilename}
            isDemo={demoMode}
            query={activeQuery}
          />
        )}
      </main>

      <HistorySidebar
        history={history}
        onSelectItem={handleSelectHistoryItem}
        onDeleteItem={handleDeleteHistoryItem}
        onClearHistory={handleClearHistory}
        isOpen={sidebarOpen}
        setIsOpen={setSidebarOpen}
        isDemo={demoMode}
      />
    </div>
  );
}
