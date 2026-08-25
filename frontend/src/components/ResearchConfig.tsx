import React from "react";
import { ArrowRight, Compass, Flame, GraduationCap, Search, Zap } from "lucide-react";
import type { DetailLevel, ResearchType } from "../types";

interface ResearchConfigProps {
  query: string;
  setQuery: (val: string) => void;
  researchType: ResearchType;
  setResearchType: (val: ResearchType) => void;
  detailLevel: DetailLevel;
  setDetailLevel: (val: DetailLevel) => void;
  onRun: () => void;
  isRunning: boolean;
}

export default function ResearchConfig({
  query,
  setQuery,
  researchType,
  setResearchType,
  detailLevel,
  setDetailLevel,
  onRun,
  isRunning,
}: ResearchConfigProps) {
  
  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && !isRunning && query.trim()) {
      onRun();
    }
  };

  return (
    <div id="control-center" className="glass-card rounded-xl p-4 md:p-5 mb-5 relative overflow-hidden">
      {/* Visual Ambient Glow background decoration */}
      <div className="absolute top-0 left-1/4 w-72 h-72 bg-blue-500/5 rounded-full blur-3xl pointer-events-none -translate-y-1/2"></div>
      
      <div className="relative z-10">
        <h2 className="text-sm font-bold text-white mb-4 flex items-center gap-1.5">
          <Flame className="w-4 h-4 text-cyan-400" />
          Orchestrator Settings
        </h2>

        {/* Query Input */}
        <div className="mb-4">
          <label className="block text-[10px] font-mono text-slate-400 uppercase tracking-wider mb-1.5">
            Research Prompt / Query Topic
          </label>
          <div className="relative group">
            <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-500 group-focus-within:text-cyan-400 transition-colors">
              <Search className="w-4.5 h-4.5" />
            </div>
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={isRunning}
              placeholder="e.g., Quantum Computing hardware innovations 2026, or Next-generation Solid-State Battery technology..."
              className="w-full pl-10 pr-4 py-2.5 bg-slate-950 border border-slate-800 focus:border-cyan-500/80 rounded-lg text-xs text-white placeholder-slate-500 focus:outline-none transition-all duration-200 focus:ring-2 focus:ring-cyan-500/10"
            />
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-4">
          {/* Research Mode Cards (Takes up 2 columns on lg) */}
          <div className="lg:col-span-2">
            <label className="block text-[10px] font-mono text-slate-400 uppercase tracking-wider mb-1.5">
              Research Agent Profile
            </label>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              
              {/* Quick Mode */}
              <button
                type="button"
                onClick={() => setResearchType("quick")}
                disabled={isRunning}
                className={`flex flex-col text-left p-3 rounded-lg border transition-all duration-200 cursor-pointer relative overflow-hidden ${
                  researchType === "quick"
                    ? "bg-blue-500/10 border-blue-500/80 ring-1 ring-blue-500/20"
                    : "bg-slate-950/60 border-slate-800/80 hover:border-slate-700 hover:bg-slate-900/40"
                }`}
              >
                <div className="flex items-center gap-1.5 mb-1">
                  <span className={`p-1 rounded-md ${researchType === "quick" ? "bg-blue-500/20 text-blue-400" : "bg-slate-800 text-slate-400"}`}>
                    <Zap className="w-3.5 h-3.5" />
                  </span>
                  <span className="font-semibold text-xs text-white">Quick Research</span>
                </div>
                <p className="text-[11px] text-slate-400 leading-normal">
                  Fast scan generating 5 key concepts, ideal for rapid definitions and high-level summaries.
                </p>
                {researchType === "quick" && (
                  <div className="absolute top-0 right-0 w-6 h-6 bg-blue-500/20 rounded-bl-lg flex items-center justify-center">
                    <span className="w-1.5 h-1.5 bg-blue-400 rounded-full animate-pulse"></span>
                  </div>
                )}
              </button>

              {/* Deep Mode */}
              <button
                type="button"
                onClick={() => setResearchType("deep")}
                disabled={isRunning}
                className={`flex flex-col text-left p-3 rounded-lg border transition-all duration-200 cursor-pointer relative overflow-hidden ${
                  researchType === "deep"
                    ? "bg-cyan-500/10 border-cyan-500/80 ring-1 ring-cyan-500/20"
                    : "bg-slate-950/60 border-slate-800/80 hover:border-slate-700 hover:bg-slate-900/40"
                }`}
              >
                <div className="flex items-center gap-1.5 mb-1">
                  <span className={`p-1 rounded-md ${researchType === "deep" ? "bg-cyan-500/20 text-cyan-400" : "bg-slate-800 text-slate-400"}`}>
                    <Compass className="w-3.5 h-3.5" />
                  </span>
                  <span className="font-semibold text-xs text-white">Deep Research</span>
                </div>
                <p className="text-[11px] text-slate-400 leading-normal">
                  Intensive crawl generating 10 key search tags with strict deduplication and robust web logs.
                </p>
                {researchType === "deep" && (
                  <div className="absolute top-0 right-0 w-6 h-6 bg-cyan-500/20 rounded-bl-lg flex items-center justify-center">
                    <span className="w-1.5 h-1.5 bg-cyan-400 rounded-full animate-pulse"></span>
                  </div>
                )}
              </button>

              {/* Academic Mode */}
              <button
                type="button"
                onClick={() => setResearchType("academic")}
                disabled={isRunning}
                className={`flex flex-col text-left p-3 rounded-lg border transition-all duration-200 cursor-pointer relative overflow-hidden ${
                  researchType === "academic"
                    ? "bg-emerald-500/10 border-emerald-500/80 ring-1 ring-emerald-500/20"
                    : "bg-slate-950/60 border-slate-800/80 hover:border-slate-700 hover:bg-slate-900/40"
                }`}
              >
                <div className="flex items-center gap-1.5 mb-1">
                  <span className={`p-1 rounded-md ${researchType === "academic" ? "bg-emerald-500/20 text-emerald-400" : "bg-slate-800 text-slate-400"}`}>
                    <GraduationCap className="w-3.5 h-3.5" />
                  </span>
                  <span className="font-semibold text-xs text-white">Academic Analysis</span>
                </div>
                <p className="text-[11px] text-slate-400 leading-normal">
                  Peer-reviewed outline focusing on technical terminology, structured citation frameworks, and strict verification.
                </p>
                {researchType === "academic" && (
                  <div className="absolute top-0 right-0 w-6 h-6 bg-emerald-500/20 rounded-bl-lg flex items-center justify-center">
                    <span className="w-1.5 h-1.5 bg-emerald-400 rounded-full animate-pulse"></span>
                  </div>
                )}
              </button>

            </div>
          </div>

          {/* Detail Level Selector */}
          <div>
            <label className="block text-[10px] font-mono text-slate-400 uppercase tracking-wider mb-1.5">
              Target Detail Level
            </label>
            <div className="flex flex-col gap-2">
              <div className="relative">
                <select
                  value={detailLevel}
                  onChange={(e) => setDetailLevel(e.target.value as DetailLevel)}
                  disabled={isRunning}
                  className="w-full bg-slate-950 border border-slate-800 text-xs text-white rounded-lg py-2.5 px-3 focus:outline-none focus:border-cyan-500 transition-colors cursor-pointer appearance-none"
                >
                  <option value="brief">Brief Report (2-3 Pages)</option>
                  <option value="standard">Standard Brief (5-7 Pages)</option>
                  <option value="comprehensive">Comprehensive Study (10+ Pages)</option>
                </select>
                <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-3 text-slate-500">
                  <svg className="fill-current h-4 w-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20">
                    <path d="M9.293 12.95l.707.707L15.657 8l-1.414-1.414L10 10.828 5.757 6.586 4.343 8z"/>
                  </svg>
                </div>
              </div>

              {/* Informative helper lines for the selected option */}
              <div className="p-2.5 bg-slate-950/40 rounded-lg border border-slate-800/50 text-[11px] text-slate-400 font-mono">
                {detailLevel === "brief" && (
                  <span>💨 Quick crawl, key metrics, and immediate executive brief summaries.</span>
                )}
                {detailLevel === "standard" && (
                  <span>📚 In-depth investigation. Synthesizes cross-reference tables and deep citations.</span>
                )}
                {detailLevel === "comprehensive" && (
                  <span>🔬 Academic thesis scope. Exhaustive citation indexes, critic revision runs.</span>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Action Run Button */}
        <div className="flex justify-end pt-1">
          <button
            type="button"
            onClick={onRun}
            disabled={isRunning || !query.trim()}
            className={`w-full md:w-auto px-6 py-2.5 rounded-lg text-xs font-semibold flex items-center justify-center gap-1.5 transition-all duration-200 relative group cursor-pointer ${
              isRunning || !query.trim()
                ? "bg-slate-800 border border-slate-700 text-slate-500 cursor-not-allowed"
                : "bg-gradient-to-r from-blue-600 to-cyan-500 hover:from-blue-500 hover:to-cyan-400 text-white shadow-md shadow-cyan-500/5 hover:shadow-cyan-500/15 hover:scale-[1.01] active:scale-[0.99]"
            }`}
          >
            {isRunning ? (
              <>
                <span className="w-4 h-4 border-2 border-slate-300 border-t-transparent rounded-full animate-spin"></span>
                <span>Agent Pipeline Engaged...</span>
              </>
            ) : (
              <>
                <span>Launch Autonomous Pipeline</span>
                <ArrowRight className="w-4 h-4 group-hover:translate-x-0.5 transition-transform" />
              </>
            )}
          </button>
        </div>

      </div>
    </div>
  );
}
