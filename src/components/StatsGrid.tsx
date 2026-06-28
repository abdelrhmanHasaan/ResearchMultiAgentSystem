import React from "react";
import { Globe, Database, FileText } from "lucide-react";
import { GlobalStats } from "../types";

interface StatsGridProps {
  stats: GlobalStats;
  loading: boolean;
}

export default function StatsGrid({ stats, loading }: StatsGridProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-5">
      {/* Total Sources Scraped */}
      <div 
        id="stats-sources" 
        className="glass-card glow-blue rounded-xl p-4 transition-all duration-200 hover:border-slate-600/80 hover:translate-y-[-1px] relative overflow-hidden group"
      >
        <div className="absolute top-0 right-0 w-24 h-24 bg-blue-500/5 rounded-full blur-2xl -mr-8 -mt-8 group-hover:bg-blue-500/10 transition-all duration-200"></div>
        <div className="flex items-center justify-between relative z-10">
          <div>
            <p className="text-[10px] font-mono text-slate-400 tracking-wider uppercase">Sources Scraped</p>
            <h3 className="text-2xl font-bold text-white mt-1 tracking-tight font-mono">
              {loading ? (
                <span className="inline-block w-12 h-6 bg-slate-800 animate-pulse rounded"></span>
              ) : (
                stats.total_pages.toLocaleString()
              )}
            </h3>
            <p className="text-[10px] text-emerald-400 font-medium mt-0.5 flex items-center gap-1">
              <span className="w-1.5 h-1.5 bg-emerald-400 rounded-full animate-ping"></span>
              Live Database Feed
            </p>
          </div>
          <div className="p-2 bg-blue-500/10 border border-blue-500/20 text-blue-400 rounded-lg">
            <Globe className="w-5 h-5" />
          </div>
        </div>
      </div>

      {/* Total Text Chunks in DB */}
      <div 
        id="stats-chunks" 
        className="glass-card glow-cyan rounded-xl p-4 transition-all duration-200 hover:border-slate-600/80 hover:translate-y-[-1px] relative overflow-hidden group"
      >
        <div className="absolute top-0 right-0 w-24 h-24 bg-cyan-500/5 rounded-full blur-2xl -mr-8 -mt-8 group-hover:bg-cyan-500/10 transition-all duration-200"></div>
        <div className="flex items-center justify-between relative z-10">
          <div>
            <p className="text-[10px] font-mono text-slate-400 tracking-wider uppercase">Indexed Chunks</p>
            <h3 className="text-2xl font-bold text-white mt-1 tracking-tight font-mono">
              {loading ? (
                <span className="inline-block w-12 h-6 bg-slate-800 animate-pulse rounded"></span>
              ) : (
                stats.total_chunks.toLocaleString()
              )}
            </h3>
            <p className="text-[10px] text-slate-400 font-medium mt-0.5">
              Vector Embeddings Ingested
            </p>
          </div>
          <div className="p-2 bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 rounded-lg">
            <Database className="w-5 h-5" />
          </div>
        </div>
      </div>

      {/* Average Summary Length */}
      <div 
        id="stats-summary" 
        className="glass-card glow-emerald rounded-xl p-4 transition-all duration-200 hover:border-slate-600/80 hover:translate-y-[-1px] relative overflow-hidden group"
      >
        <div className="absolute top-0 right-0 w-24 h-24 bg-emerald-500/5 rounded-full blur-2xl -mr-8 -mt-8 group-hover:bg-emerald-500/10 transition-all duration-200"></div>
        <div className="flex items-center justify-between relative z-10">
          <div>
            <p className="text-[10px] font-mono text-slate-400 tracking-wider uppercase">Avg Summary Length</p>
            <h3 className="text-2xl font-bold text-white mt-1 tracking-tight font-mono">
              {loading ? (
                <span className="inline-block w-12 h-6 bg-slate-800 animate-pulse rounded"></span>
              ) : (
                `${stats.avg_summary_length.toLocaleString()} words`
              )}
            </h3>
            <p className="text-[10px] text-emerald-400 font-medium mt-0.5">
              Academic-Grade Detail Level
            </p>
          </div>
          <div className="p-2 bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 rounded-lg">
            <FileText className="w-5 h-5" />
          </div>
        </div>
      </div>
    </div>
  );
}
