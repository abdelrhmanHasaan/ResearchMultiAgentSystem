import React, { useState, useEffect } from "react";
import { 
  History, ShieldCheck, Database, RefreshCw, AlertCircle, ToggleLeft, ToggleRight, Sparkles, BookOpen, HardDrive
} from "lucide-react";
import { ResearchType, DetailLevel, HistoryItem, GlobalStats, PipelineLog, ResearchResponse } from "./types";
import StatsGrid from "./components/StatsGrid";
import ResearchConfig from "./components/ResearchConfig";
import PipelineTracker from "./components/PipelineTracker";
import Workspace from "./components/Workspace";
import HistorySidebar from "./components/HistorySidebar";

// GORGEOUS RICH ACADEMIC MOCK REPORTS
const MOCK_REPORTS: Record<string, { report: string; stats: any }> = {
  "solid-state battery": {
    stats: { total_pages: 35, total_chunks: 172, recent_pages: 6, avg_chunks_per_page: 4.9 },
    report: `# Advanced Anode Materials and Dendrite Prevention in Solid-State Batteries

## 1. Executive Summary
Solid-state lithium batteries (SSLBs) offer superior energy density and safety compared to conventional liquid electrolyte cells. However, **lithium dendrite penetration** through solid electrolytes (SEs) remains a primary failure mechanism, causing internal short circuits and cell death. This study synthesizes mechanical, electrochemical, and metallurgical strategies to overcome dendrite propagation, focusing on 2026 state-of-the-art anode designs.

---

## 2. Technical Evaluation Matrix
Below is a structured analysis of solid electrolyte (SE) classes and their mechanical parameters impacting dendrite prevention:

| Solid Electrolyte Class | Shear Modulus (Gpa) | Li-Ionic Conductivity (mS/cm) | Primary Failure Vector | Dendrite Resistance |
| :--- | :---: | :---: | :--- | :---: |
| **Garnet-Type (LLZO)** | 61.2 | 1.0 - 2.5 | Grain boundary conduction | Medium |
| **Sulfide-Type (LPSCl)** | 18.5 | 3.0 - 12.0 | High electronic leakage | Low |
| **Polymer (PEO-LiTFSI)** | 0.12 | 0.01 - 0.1 | Elastic mechanical failure | Very Low |
| **Composite (LLZO-PVDF)**| 8.4 | 0.5 - 1.2 | Phase boundary interface resistance | High |

> **Key Takeaway:** While LLZO ceramic offers superior mechanical shear modulus, the high lithium-metal interface roughness allows local electric field hotspot concentrations, causing grain-boundary penetration.

---

## 3. Comparative Dendrite Prevention Methodologies

### A. Metallurgical Anode Surface Modification
Applying thin, lithiophilic interlayers mitigates the high surface impedance between lithium metal and solid electrolytes:
* **Atomic Layer Deposition (ALD):** Depositing 2–5 nm of \`Al2O3\` or \`ZnO\` which reacts with Li to form highly conductive alloy interfaces.
* **Chemical Vapor Deposition (CVD):** Infusing ultrathin carbonaceous layers to distribute local current density evenly.

### B. 3D Porous Lithiophilic Frameworks
Instead of a planar foil, placing lithium inside sub-micron pore frameworks eliminates local mechanical stresses:
1. *In-situ* alloy scaffolding (\`Li-Mg\`, \`Li-In\`).
2. Nitrogen-doped carbon nanotube matrices offering superior electronic conduits.

---

## 4. Current Academic Recommendations
Researchers must shift design priorities from high solid electrolyte thickness to **microstructural density control**. Sintering techniques must reach \`> 98.5%\` relative theoretical densities to successfully bypass grain-boundary lithium tracking.
`
  },
  "quantum computing": {
    stats: { total_pages: 58, total_chunks: 290, recent_pages: 11, avg_chunks_per_page: 5.0 },
    report: `# Next-Generation Quantum Computing Hardware: Superconducting vs Neutral Atom Qubits

## 1. Technological Abstract
The quantum computing industry in 2026 is witnessing an intense rivalry between **Superconducting Josephson-junction qubits** and **Neutral Atom (Rydberg) qubits**. This evaluation maps physical parameters, error correction overheads, and fault-tolerant scaling matrices for both paradigms.

---

## 2. Hardware Benchmark Matrix

| Physics Paradigm | Coherence Time ($T_2$) | Single-Qubit Gate Fidelity | Two-Qubit Gate Fidelity | Operating Temp (K) |
| :--- | :---: | :---: | :---: | :---: |
| **Superconducting** (Transmon) | ~100 µs | 99.99% | 99.8% | 0.015 K (Cryo) |
| **Neutral Atoms** (Rubidium) | ~10 s | 99.95% | 99.5% | Room Temp Vacuum |
| **Ion Trap** (Ytterbium) | ~100 s | 99.99% | 99.9% | Room Temp Vacuum |
| **Silicon Spin Qubits** | ~10 ms | 99.9% | 99.0% | 1.1 K (Sub-cryo) |

> **Analyst Consensus:** Neutral atom systems have rapidly scaled past 1,000 qubits in 2026 due to optical tweezer dynamic rearrangement, bypassing the heavy wiring limitations of dilution refrigerators.

---

## 3. Scalability and Error Mitigation Vectors

### A. Neutral Rydberg Atoms
* **Physical Mechanism:** Rubidium or Strontium atoms suspended in an array of optical traps. Entanglement is turned on by exciting atoms to highly polarizable Rydberg states.
* **Core Strength:** Identical qubits by nature, preventing fabrication variations seen in lithography-based solid-state transmons.

### B. Superconducting Transmon Chips
* **Physical Mechanism:** Microsecond microwave pulse routing over coaxial cable feeds into niobium/aluminum superconducting loops.
* **Core Strength:** Extremely fast gate execution speed (~10 ns) allows rapid error extraction under Surface Code architectures.

---

## 4. Engineering Outlook
While Superconducting chips remain dominant in commercial clouds (IBM, Google), Neutral Atom platforms (Pasqal, Atom Computing) offer the shortest timeline to early fault-tolerant simulation tasks.
`
  },
  "smr reactors": {
    stats: { total_pages: 42, total_chunks: 210, recent_pages: 8, avg_chunks_per_page: 5.0 },
    report: `# Coolant Efficiency and Thermal Benchmarks in Small Modular Nuclear Reactors (SMRs)

## 1. Executive Briefing
Small Modular Reactors (SMRs) present a decentralized, factory-fabricated atomic alternative to high-gigawatt fission facilities. SMR safety margins rely on passive natural convection coolant designs. This study focuses on heat-exchanger coefficients and phase margins of advanced non-aqueous coolants.

---

## 2. Coolant Thermodynamic Specifications

| Coolant Substance | Operating Temperature Range (°C) | Volumetric Heat Capacity (kJ/m³·K) | Operating Pressure (MPa) | Core Safety Feedback |
| :--- | :---: | :---: | :---: | :---: |
| **Superheated Light Water**| 280 - 325 | 3,100 | 15.0 (Extremely High)| Critical (Negative Void) |
| **Liquid Sodium (Metal)** | 390 - 540 | 1,120 | 0.1 (Atmospheric) | High Chemical Reactivity|
| **Molten FLiBe Salt** | 550 - 700 | 4,200 | 0.1 (Atmospheric) | Excellent (Passive) |
| **Helium Gas** | 450 - 850 | 5.4 | 7.0 (High) | Single-phase stability |

> **Safety Warning:** High pressure in Light Water SMRs requires expensive heavy containment structures, mitigating some of SMR's financial module scaling advantages. Molten Salt designs operate at atmospheric pressures, virtually eliminating rupture threats.

---

## 3. Passive Safety and Natural Circulation Mechanics
Advanced SMR structures are designed to prevent core meltdowns *without operator intervention* or electric backup pumps:
1. **Buoyancy-Driven Convection:** Heating decreases coolant density, forcing gravity-driven upward movement into auxiliary condensers.
2. **Freeze-Plug Drains:** Molten salt reactors utilize actively cooled salt plugs. If power fails, the plug melts, safely draining active fuel into sub-critical dump tanks.
`
  }
};

const DEFAULT_GLOBAL_STATS: GlobalStats = {
  total_pages: 135,
  total_chunks: 672,
  avg_chunks_per_page: 5.0,
  avg_summary_length: 1250,
};

const DEFAULT_HISTORY: HistoryItem[] = [
  {
    id: 1,
    topic: "Next-generation Solid-State Battery technology & dendrite prevention",
    timestamp: "2026-06-25T14:32:00Z",
    pdf_path: "Academic_Report_solid_state_battery.pdf",
    metadata: {
      pages_processed: 35,
      chunks_included: 172,
      detail_level: "comprehensive",
    },
  },
  {
    id: 2,
    topic: "Quantum Computing hardware innovations: superconducting qubits vs neutral atoms",
    timestamp: "2026-06-26T09:15:00Z",
    pdf_path: "Academic_Report_quantum_computing.pdf",
    metadata: {
      pages_processed: 58,
      chunks_included: 290,
      detail_level: "comprehensive",
    },
  },
  {
    id: 3,
    topic: "SMR (Small Modular Nuclear Reactors) coolant efficiency benchmarks 2026",
    timestamp: "2026-06-27T11:45:00Z",
    pdf_path: "Academic_Report_smr_reactors.pdf",
    metadata: {
      pages_processed: 42,
      chunks_included: 210,
      detail_level: "standard",
    },
  },
];

export default function App() {
  const [query, setQuery] = useState("");
  const [researchType, setResearchType] = useState<ResearchType>("deep");
  const [detailLevel, setDetailLevel] = useState<DetailLevel>("standard");
  const [isDemo, setIsDemo] = useState(true);
  const [backendReachable, setBackendReachable] = useState(false);
  const [globalStats, setGlobalStats] = useState<GlobalStats>(DEFAULT_GLOBAL_STATS);
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [sidebarOpen, setSidebarOpen] = useState(true);

  // Active generation states
  const [isRunning, setIsRunning] = useState(false);
  const [currentStage, setCurrentStage] = useState<"idle" | "Planner" | "Scraper" | "Analyzer" | "Writer" | "Critic" | "complete">("idle");
  const [logs, setLogs] = useState<PipelineLog[]>([]);
  const [reportMarkdown, setReportMarkdown] = useState<string>("");
  const [pdfFilename, setPdfFilename] = useState<string>("");
  const [activeQuery, setActiveQuery] = useState<string>("");
  const [pipelineStats, setPipelineStats] = useState<any>(null);

  // On Load: load cache from LocalStorage, ping FastAPI backend
  useEffect(() => {
    // 1. Load History
    const cachedHistory = localStorage.getItem("research_portal_history");
    if (cachedHistory) {
      try {
        setHistory(JSON.parse(cachedHistory));
      } catch (e) {
        setHistory(DEFAULT_HISTORY);
      }
    } else {
      setHistory(DEFAULT_HISTORY);
      localStorage.setItem("research_portal_history", JSON.stringify(DEFAULT_HISTORY));
    }

    // 2. Load Stats
    const cachedStats = localStorage.getItem("research_portal_stats");
    if (cachedStats) {
      try {
        setGlobalStats(JSON.parse(cachedStats));
      } catch (e) {
        setGlobalStats(DEFAULT_GLOBAL_STATS);
      }
    } else {
      setGlobalStats(DEFAULT_GLOBAL_STATS);
    }

    // 3. Select first item from default mock as initial report
    const initialReport = MOCK_REPORTS["solid-state battery"];
    setReportMarkdown(initialReport.report);
    setPdfFilename("Academic_Report_solid_state_battery.pdf");
    setActiveQuery(DEFAULT_HISTORY[0].topic);

    // 4. Ping local backend
    checkBackendHealth();
  }, []);

  const checkBackendHealth = async () => {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 1200);
      
      const res = await fetch("http://localhost:8679/api/stats", { signal: controller.signal });
      clearTimeout(timeoutId);
      
      if (res.ok) {
        const statsData = await res.json();
        setGlobalStats(statsData);
        setBackendReachable(true);
        setIsDemo(false); // Automatically switch to backend mode if available!
      } else {
        setBackendReachable(false);
      }
    } catch (e) {
      setBackendReachable(false);
    }
  };

  // Switch between Connection profiles manually
  const toggleDemoMode = () => {
    if (!backendReachable && isDemo) {
      // User is trying to switch to live connection, check health first
      checkBackendHealth().then(() => {
        if (!backendReachable) {
          alert("Could not reach local FastAPI server on http://localhost:8679.\n\nEnsure FastAPI is running and CORS is allowed.");
        } else {
          setIsDemo(false);
        }
      });
    } else {
      setIsDemo(!isDemo);
    }
  };

  // Clear Local history logs
  const handleClearHistory = () => {
    setHistory([]);
    localStorage.removeItem("research_portal_history");
    
    const freshStats = { total_pages: 0, total_chunks: 0, avg_chunks_per_page: 0.0, avg_summary_length: 0 };
    setGlobalStats(freshStats);
    localStorage.setItem("research_portal_stats", JSON.stringify(freshStats));
  };

  // Click on a historical archive to load it up
  const handleSelectHistoryItem = (item: HistoryItem) => {
    // Check if we have preloaded mock report
    let reportKey = "";
    const lowerTopic = item.topic.toLowerCase();
    if (lowerTopic.includes("battery")) reportKey = "solid-state battery";
    else if (lowerTopic.includes("quantum")) reportKey = "quantum computing";
    else if (lowerTopic.includes("smr") || lowerTopic.includes("modular")) reportKey = "smr reactors";

    if (reportKey && MOCK_REPORTS[reportKey]) {
      setReportMarkdown(MOCK_REPORTS[reportKey].report);
      setPdfFilename(item.pdf_path);
      setActiveQuery(item.topic);
      setPipelineStats(MOCK_REPORTS[reportKey].stats);
      setCurrentStage("complete");
    } else {
      // Fallback structured generation
      setReportMarkdown(`# Academic Synthesis: ${item.topic}\n\n## 1. Historical Abstract\nReport generated on *${new Date(item.timestamp).toLocaleDateString()}* with a detailed level of **${item.metadata.detail_level}**.\n\n*Source data index: ${item.metadata.pages_processed} documents processed into ${item.metadata.chunks_included} vector chunks.*`);
      setPdfFilename(item.pdf_path);
      setActiveQuery(item.topic);
      setPipelineStats({ total_pages: item.metadata.pages_processed, total_chunks: item.metadata.chunks_included, avg_chunks_per_page: 5 });
      setCurrentStage("complete");
    }
  };

  // Launch Research Task
  const handleLaunchResearch = async () => {
    if (!query.trim()) return;

    setIsRunning(true);
    setLogs([]);
    setReportMarkdown("");
    setCurrentStage("Planner");
    setActiveQuery(query);

    // Dynamic clean log triggers helper
    const addLog = (stage: any, status: any, output: string) => {
      setLogs(prev => {
        const filtered = prev.filter(l => l.stage !== stage);
        return [...filtered, { stage, status, output }];
      });
    };

    if (isDemo) {
      // HIGH-FIDELITY SIMULATION TIMELINES (2 seconds per agent step)
      
      // Stage 1: Planner
      addLog("Planner", "running", `Analyzing semantic core of prompt: "${query}"`);
      await new Promise(r => setTimeout(r, 1800));
      addLog("Planner", "completed", `Expanded query into 5 focused keyword clusters. Dispatched search tags to crawler.`);
      
      // Stage 2: Scraper
      setCurrentStage("Scraper");
      addLog("Scraper", "running", "Initiating parallel chromium headless scrapers...");
      await new Promise(r => setTimeout(r, 2200));
      addLog("Scraper", "completed", "Crawled 25 technical articles. Removed commercial paywalls & boilerplate JS tags.");

      // Stage 3: Analyzer
      setCurrentStage("Analyzer");
      addLog("Analyzer", "running", "Splitting page contents into 512-character overlapping text chunks...");
      await new Promise(r => setTimeout(r, 2000));
      addLog("Analyzer", "completed", "Generated 120 vector embeddings. Completed semantic deduplication.");

      // Stage 4: Writer
      setCurrentStage("Writer");
      addLog("Writer", "running", "Orchestrating technical outline layout. Crafting sections 1-4.");
      await new Promise(r => setTimeout(r, 2000));
      addLog("Writer", "completed", "Synthesized comprehensive markdown files. Formatted cross-reference tables.");

      // Stage 5: Critic
      setCurrentStage("Critic");
      addLog("Critic", "running", "Validating numeric claims against source index context...");
      await new Promise(r => setTimeout(r, 1800));
      addLog("Critic", "completed", "Critic Consensus Rating: 9.4/10. Passed factual consistency test. Generating ReportLab PDF layouts.");
      await new Promise(r => setTimeout(r, 1000));

      // Complete
      const simulatedStats = { total_pages: 25, total_chunks: 120, recent_pages: 5, avg_chunks_per_page: 4.8 };
      setPipelineStats(simulatedStats);

      // Determine appropriate report content
      let targetReport = MOCK_REPORTS["solid-state battery"].report;
      const lowerQuery = query.toLowerCase();
      if (lowerQuery.includes("quantum")) {
        targetReport = MOCK_REPORTS["quantum computing"].report;
      } else if (lowerQuery.includes("smr") || lowerQuery.includes("reactor")) {
        targetReport = MOCK_REPORTS["smr reactors"].report;
      } else {
        // Fallback custom generated report structure
        targetReport = `# Academic Brief: ${query}

## 1. Executive Summary
This autonomous brief synthesizes current engineering and scientific developments regarding **${query}** as of June 2026. 

---

## 2. Technical Evaluation
Below is a structured taxonomy of indexed variables derived during our crawler run:

| Analyzed Parameter | Structural Impact | Consensus Score | Research Confidence |
| :--- | :--- | :---: | :---: |
| **Material Interface** | Primary physical stability constraint | 8.8 / 10 | High |
| **Volumetric Efficiency** | Governs spatial scalability parameters | 9.2 / 10 | Excellent |
| **Thermal Dissipation** | Critical safety buffer indicator | 8.5 / 10 | High |

> **Analyst Consensus:** The evaluated nodes demonstrate strong technical alignment with current industry specifications.

---

## 3. Recommended Engineering Roadmap
* **Step 1:** Establish high-throughput testing chambers to validate material density.
* **Step 2:** Refine vector embeddings matching models to prevent local factual deviations.
`;
      }

      setReportMarkdown(targetReport);
      setPdfFilename(`Academic_Report_${Date.now()}.pdf`);

      // Save into History
      const newItem: HistoryItem = {
        id: Date.now(),
        topic: query,
        timestamp: new Date().toISOString(),
        pdf_path: `Academic_Report_${Date.now()}.pdf`,
        metadata: {
          pages_processed: 25,
          chunks_included: 120,
          detail_level: detailLevel,
        }
      };

      const updatedHistory = [newItem, ...history];
      setHistory(updatedHistory);
      localStorage.setItem("research_portal_history", JSON.stringify(updatedHistory));

      // Update Global Stats
      const updatedGlobalStats = {
        total_pages: globalStats.total_pages + 25,
        total_chunks: globalStats.total_chunks + 120,
        avg_chunks_per_page: 4.9,
        avg_summary_length: 1280
      };
      setGlobalStats(updatedGlobalStats);
      localStorage.setItem("research_portal_stats", JSON.stringify(updatedGlobalStats));

      setCurrentStage("complete");
      setIsRunning(false);
      setQuery("");

    } else {
      // REAL FASTAPI REQUEST COUPLING
      try {
        const response = await fetch("http://localhost:8679/api/research", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            query: query,
            research_type: researchType,
            detail_level: detailLevel,
          }),
        });

        if (!response.ok) {
          throw new Error(`Server returned error: ${response.statusText}`);
        }

        const data: ResearchResponse = await response.json();
        
        if (data.status === "success") {
          setReportMarkdown(data.report);
          setPdfFilename(data.pdf);
          setPipelineStats(data.stats);
          
          // Re-populate logs in UI
          setLogs(data.logs);
          
          // Refresh global stats and history from endpoints
          await refreshBackendStates();
          
          setCurrentStage("complete");
        } else {
          addLog("Critic", "failed", "FastAPI backend reported internal assembly failure.");
        }
      } catch (err: any) {
        alert(`Failed to communicate with FastAPI backend.\nError: ${err.message}\n\nFalling back to high-fidelity Demo Mode so you can inspect UI capabilities.`);
        setIsDemo(true);
      } finally {
        setIsRunning(false);
      }
    }
  };

  const refreshBackendStates = async () => {
    try {
      // Get History
      const histRes = await fetch("http://localhost:8679/api/history");
      if (histRes.ok) {
        const histData = await histRes.json();
        setHistory(histData);
        localStorage.setItem("research_portal_history", JSON.stringify(histData));
      }

      // Get Global Stats
      const statsRes = await fetch("http://localhost:8679/api/stats");
      if (statsRes.ok) {
        const statsData = await statsRes.json();
        setGlobalStats(statsData);
        localStorage.setItem("research_portal_stats", JSON.stringify(statsData));
      }
    } catch (e) {
      console.warn("Failed to sync backend state archives.", e);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 font-sans relative pb-16">
      
      {/* Decorative Grid Mesh Background */}
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#0f172a_1px,transparent_1px),linear-gradient(to_bottom,#0f172a_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_0%,#000_70%,transparent_100%)] pointer-events-none"></div>

      {/* Connection fallbacks Top banner */}
      {isDemo && (
        <div className="bg-slate-900 border-b border-cyan-500/20 py-2.5 px-6 text-center text-xs relative z-30">
          <div className="max-w-7xl mx-auto flex items-center justify-center gap-2 flex-wrap">
            <span className="w-2 h-2 bg-cyan-400 rounded-full animate-ping"></span>
            <span className="font-mono text-cyan-400 font-bold">Simulator Profile Active</span>
            <span className="text-slate-400">| You can interactively test the complete 5-agent pipeline, generated layouts, and academic logs instantly.</span>
            {backendReachable && (
              <button 
                onClick={() => setIsDemo(false)} 
                className="ml-2 px-2.5 py-0.5 bg-cyan-500/10 hover:bg-cyan-500/20 border border-cyan-400/40 text-cyan-400 font-semibold rounded text-[10px] cursor-pointer transition-all"
              >
                Engage Live Backend
              </button>
            )}
          </div>
        </div>
      )}

      {/* Main Core Header */}
      <header className="bg-slate-950/80 backdrop-blur-md border-b border-slate-900 sticky top-0 z-30 px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          
          {/* Logo Title */}
          <div className="flex items-center gap-3">
            <div className="relative flex items-center justify-center">
              <div className="absolute inset-0 bg-cyan-500/30 rounded-lg blur"></div>
              <div className="relative p-2.5 bg-slate-900 border border-slate-800 rounded-lg text-cyan-400 font-bold">
                <BookOpen className="w-5.5 h-5.5" />
              </div>
            </div>
            <div>
              <h1 className="text-lg font-bold text-white tracking-tight flex items-center gap-2">
                Autonomous Research Portal
                <span className="text-[10px] px-2 py-0.5 bg-blue-950 text-blue-400 border border-blue-800 rounded-full font-mono uppercase">
                  v3.4
                </span>
              </h1>
              <p className="text-[10px] text-slate-400 font-mono tracking-wider">CRITICAL CRAWLER ORCHESTRATION ENVIRONMENT</p>
            </div>
          </div>

          {/* Connection Profile Controls */}
          <div className="flex items-center gap-4">
            
            <div className="hidden md:flex items-center gap-2 bg-slate-900/60 px-3 py-1.5 rounded-xl border border-slate-800 text-xs">
              <span className={`w-2 h-2 rounded-full ${backendReachable ? "bg-emerald-400 animate-pulse" : "bg-red-400 animate-pulse"}`}></span>
              <span className="font-mono text-slate-300">
                Ollama / Local FastAPI: {backendReachable ? "ONLINE" : "OFFLINE"}
              </span>
            </div>

            <button
              onClick={toggleDemoMode}
              className={`px-4 py-2 rounded-xl text-xs font-semibold border flex items-center gap-2 transition-all cursor-pointer ${
                isDemo
                  ? "bg-slate-900 border-slate-800 text-cyan-400 hover:text-cyan-300"
                  : "bg-emerald-950/20 border-emerald-800/60 text-emerald-400"
              }`}
            >
              <span>{isDemo ? "Simulating System" : "FastAPI Link Live"}</span>
              {isDemo ? <ToggleRight className="w-5 h-5" /> : <ToggleLeft className="w-5 h-5" />}
            </button>
          </div>

        </div>
      </header>

      {/* Main Core Layout View */}
      <main className={`max-w-7xl mx-auto px-6 pt-8 transition-all duration-300 ${sidebarOpen ? "xl:pr-[380px]" : ""}`}>
        
        {/* Welcome Section */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2">
            Welcome to the Scientific Synthesis Sandbox
            <Sparkles className="w-5 h-5 text-cyan-400" />
          </h2>
          <p className="text-sm text-slate-400 mt-1">
            Query the web using five autonomous consensus agents. Crawl PDF manuals, synthesize research notes, and generate ready-to-publish ReportLab vector documents.
          </p>
        </div>

        {/* 3 Dashboard Widgets */}
        <StatsGrid stats={globalStats} loading={false} />

        {/* Input Configuration settings Control Panel */}
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

        {/* Multi-Agent Processing tracker visualizer (renders when running or completed) */}
        {(isRunning || currentStage === "complete") && (
          <PipelineTracker
            logs={logs}
            currentStage={currentStage}
            query={activeQuery}
            stats={pipelineStats}
          />
        )}

        {/* Split Screen Document Workspace */}
        {reportMarkdown && (
          <Workspace
            reportMarkdown={reportMarkdown}
            pdfFilename={pdfFilename}
            isDemo={isDemo}
            query={activeQuery}
          />
        )}

      </main>

      {/* History Slide Panel */}
      <HistorySidebar
        history={history}
        onSelectItem={handleSelectHistoryItem}
        onClearHistory={handleClearHistory}
        isOpen={sidebarOpen}
        setIsOpen={setSidebarOpen}
        isDemo={isDemo}
      />

    </div>
  );
}
