import { useState } from "react";
import { ChevronDown, Coins, Cpu, Gauge, Zap } from "lucide-react";
import type { RunUsage } from "../types";

interface UsagePanelProps {
  usage: RunUsage | null;
  live: boolean;
}

function formatUsd(value: number): string {
  if (value === 0) return "$0.00";
  if (value < 0.01) return `$${value.toFixed(6)}`;
  return `$${value.toFixed(4)}`;
}

function formatTokens(value: number): string {
  if (value >= 1_000_000) return `${(value / 1_000_000).toFixed(2)}M`;
  if (value >= 1_000) return `${(value / 1_000).toFixed(1)}k`;
  return String(value);
}

export default function UsagePanel({ usage, live }: UsagePanelProps) {
  const [expanded, setExpanded] = useState(false);

  if (!live || !usage || usage.calls === 0) return null;

  const { calls, prompt_tokens, completion_tokens, total_tokens, estimated_cost_usd, per_provider } = usage;

  return (
    <div id="usage-panel" className="glass-card rounded-xl p-4 mb-5 relative overflow-hidden">
      <div className="absolute top-0 right-0 w-48 h-48 bg-amber-500/5 rounded-full blur-3xl pointer-events-none"></div>

      <button
        onClick={() => setExpanded((prev) => !prev)}
        className="w-full flex items-center justify-between gap-3 cursor-pointer text-left"
      >
        <div className="flex items-center gap-1.5">
          <Coins className="w-4 h-4 text-amber-400" />
          <h3 className="text-sm font-bold text-white">Run Cost & Token Usage</h3>
          <span className="text-[9px] bg-slate-950 px-1.5 py-0.5 rounded border border-slate-800 text-slate-400 font-mono uppercase">
            estimated
          </span>
        </div>
        <ChevronDown className={`w-4 h-4 text-slate-400 transition-transform ${expanded ? "rotate-180" : ""}`} />
      </button>

      {/* Headline metrics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mt-3">
        <div className="bg-slate-950/60 border border-slate-800/80 rounded-lg p-2.5">
          <p className="text-[9px] font-mono text-slate-500 uppercase tracking-wider flex items-center gap-1">
            <Zap className="w-2.5 h-2.5" /> Est. Cost
          </p>
          <p className="text-lg font-bold font-mono text-amber-400 mt-0.5">{formatUsd(estimated_cost_usd)}</p>
        </div>
        <div className="bg-slate-950/60 border border-slate-800/80 rounded-lg p-2.5">
          <p className="text-[9px] font-mono text-slate-500 uppercase tracking-wider flex items-center gap-1">
            <Cpu className="w-2.5 h-2.5" /> Total Tokens
          </p>
          <p className="text-lg font-bold font-mono text-cyan-400 mt-0.5">{formatTokens(total_tokens)}</p>
        </div>
        <div className="bg-slate-950/60 border border-slate-800/80 rounded-lg p-2.5">
          <p className="text-[9px] font-mono text-slate-500 uppercase tracking-wider">LLM Calls</p>
          <p className="text-lg font-bold font-mono text-white mt-0.5">{calls}</p>
        </div>
        <div className="bg-slate-950/60 border border-slate-800/80 rounded-lg p-2.5">
          <p className="text-[9px] font-mono text-slate-500 uppercase tracking-wider flex items-center gap-1">
            <Gauge className="w-2.5 h-2.5" /> In / Out Split
          </p>
          <p className="text-sm font-bold font-mono text-emerald-400 mt-1">
            {formatTokens(prompt_tokens)} / {formatTokens(completion_tokens)}
          </p>
        </div>
      </div>

      {/* Provider breakdown */}
      {expanded && per_provider.length > 0 && (
        <div className="mt-3 overflow-x-auto">
          <table className="w-full text-[10px] font-mono">
            <thead>
              <tr className="text-slate-500 border-b border-slate-800 text-left">
                <th className="pb-1.5 pr-3 font-medium">Provider</th>
                <th className="pb-1.5 pr-3 font-medium">Model</th>
                <th className="pb-1.5 pr-3 font-medium text-right">Calls</th>
                <th className="pb-1.5 pr-3 font-medium text-right">Tokens</th>
                <th className="pb-1.5 font-medium text-right">Est. Cost</th>
              </tr>
            </thead>
            <tbody>
              {per_provider.map((entry) => (
                <tr key={`${entry.provider}-${entry.model}`} className="border-b border-slate-900 last:border-0">
                  <td className="py-1.5 pr-3 text-slate-300 capitalize">{entry.provider}</td>
                  <td className="py-1.5 pr-3 text-slate-400 truncate max-w-[220px]" title={entry.model}>
                    {entry.model}
                  </td>
                  <td className="py-1.5 pr-3 text-right text-white">{entry.calls}</td>
                  <td className="py-1.5 pr-3 text-right text-cyan-400">{formatTokens(entry.tokens)}</td>
                  <td className="py-1.5 text-right text-amber-400">{formatUsd(entry.cost_usd)}</td>
                </tr>
              ))}
            </tbody>
          </table>
          <p className="text-[9px] text-slate-600 mt-2 font-mono">
            Estimates use public list pricing per 1M tokens; free tiers and local Ollama models are counted as $0.
          </p>
        </div>
      )}
    </div>
  );
}
