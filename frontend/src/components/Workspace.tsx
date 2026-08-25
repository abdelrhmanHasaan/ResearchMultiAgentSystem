import { useMemo, useState } from "react";
import Markdown from "react-markdown";
import { BookOpen, Download, FileText, Layers } from "lucide-react";
import { API_BASE, pdfUrl } from "../lib/api";

interface WorkspaceProps {
  reportMarkdown: string;
  pdfFilename: string;
  isDemo: boolean;
  query: string;
}

type Tab = "both" | "markdown" | "pdf";

export default function Workspace({ reportMarkdown, pdfFilename, isDemo, query }: WorkspaceProps) {
  const [activeTab, setActiveTab] = useState<Tab>("both");

  const hasRealPdf = useMemo(
    () => !isDemo && Boolean(pdfFilename) && pdfFilename.endsWith(".pdf"),
    [isDemo, pdfFilename],
  );

  const handleDownload = () => {
    if (hasRealPdf) {
      window.open(pdfUrl(pdfFilename), "_blank");
      return;
    }
    // Export the markdown itself when no backend PDF exists (demo mode).
    const blob = new Blob([reportMarkdown], { type: "text/markdown;charset=utf-8" });
    const element = document.createElement("a");
    element.href = URL.createObjectURL(blob);
    element.download = `${(query || "research_report").replace(/\s+/g, "_").slice(0, 60)}.md`;
    document.body.appendChild(element);
    element.click();
    element.remove();
    URL.revokeObjectURL(element.href);
  };

  return (
    <div id="workspace-container" className="glass-card rounded-xl border border-slate-800/80 overflow-hidden mb-5">
      {/* Menu bar */}
      <div className="bg-slate-900/80 border-b border-slate-800/80 px-4 py-3 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
        <div className="flex items-center gap-2.5">
          <div className="p-1.5 bg-gradient-to-br from-blue-500/20 to-cyan-500/20 rounded-lg text-cyan-400 border border-cyan-500/30">
            <Layers className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-white flex items-center gap-1.5">
              Research Workspace
              {hasRealPdf && (
                <span className="text-[9px] bg-cyan-950 text-cyan-400 border border-cyan-800 px-1.5 py-0.5 rounded-full font-mono">
                  PDF Ready
                </span>
              )}
            </h3>
            <p className="text-[10px] text-slate-400 font-mono mt-0.5">Topic: "{query || "Current research prompt"}"</p>
          </div>
        </div>

        <div className="flex items-center gap-2 w-full sm:w-auto justify-end">
          <div className="bg-slate-950 p-0.5 rounded-lg border border-slate-800/80 flex">
            {(["both", "markdown", "pdf"] as Tab[]).map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`px-2.5 py-1 rounded-md text-[11px] font-semibold cursor-pointer transition-all ${
                  activeTab === tab ? "bg-slate-800 text-white shadow" : "text-slate-400 hover:text-slate-200"
                }`}
              >
                {tab === "both" ? "Split View" : tab === "markdown" ? "Markdown" : "PDF Report"}
              </button>
            ))}
          </div>

          <button
            onClick={handleDownload}
            className="px-3 py-1.5 bg-gradient-to-r from-blue-600 to-cyan-500 hover:from-blue-500 hover:to-cyan-400 text-white text-[11px] font-semibold rounded-lg flex items-center gap-1 transition-all shadow-md shadow-cyan-500/10 cursor-pointer"
          >
            <Download className="w-3 h-3" />
            <span>{hasRealPdf ? "Download PDF" : "Export MD"}</span>
          </button>
        </div>
      </div>

      {/* Panels */}
      <div className="grid grid-cols-1 lg:grid-cols-2 divide-y lg:divide-y-0 lg:divide-x divide-slate-800/80 h-[600px]">
        {/* Markdown panel */}
        {(activeTab === "both" || activeTab === "markdown") && (
          <div className="flex flex-col h-full bg-slate-950/20 overflow-hidden">
            <div className="bg-slate-900/40 px-4 py-2 border-b border-slate-800/50 flex items-center justify-between">
              <span className="text-[11px] font-mono font-bold text-slate-400 tracking-wider uppercase flex items-center gap-1.5">
                <BookOpen className="w-3.5 h-3.5 text-blue-400" />
                Section A: Document Markup
              </span>
              <span className="text-[9px] text-slate-500 font-mono">Renderer: react-markdown</span>
            </div>
            <div className="flex-1 overflow-y-auto p-4 md:p-5">
              <div className="markdown-body">
                <Markdown>{reportMarkdown}</Markdown>
              </div>
            </div>
          </div>
        )}

        {/* PDF panel */}
        {(activeTab === "both" || activeTab === "pdf") && (
          <div className="flex flex-col h-full bg-slate-950/40 overflow-hidden">
            <div className="bg-slate-900/40 px-4 py-2 border-b border-slate-800/50 flex items-center justify-between">
              <span className="text-[11px] font-mono font-bold text-slate-400 tracking-wider uppercase flex items-center gap-1.5">
                <FileText className="w-3.5 h-3.5 text-cyan-400" />
                Section B: ReportLab PDF Engine
              </span>
              <span className={`text-[9px] font-mono flex items-center gap-1 ${hasRealPdf ? "text-emerald-400" : "text-slate-400"}`}>
                <span className={`w-1.5 h-1.5 rounded-full ${hasRealPdf ? "bg-emerald-400 animate-pulse" : "bg-slate-500"}`}></span>
                {hasRealPdf ? "Vector layout ready" : "No backend PDF"}
              </span>
            </div>

            {hasRealPdf ? (
              <iframe
                key={`${API_BASE}-${pdfFilename}`}
                src={pdfUrl(pdfFilename)}
                title="PDF Report Viewer"
                className="flex-1 w-full border-none bg-slate-900"
              />
            ) : (
              <DemoPdfPlaceholder query={query} />
            )}
          </div>
        )}
      </div>
    </div>
  );
}

function DemoPdfPlaceholder({ query }: { query: string }) {
  return (
    <div className="flex-1 flex flex-col items-center justify-center p-6 bg-slate-900/80 text-center">
      <FileText className="w-10 h-10 text-slate-600 mb-3" />
      <p className="text-sm font-semibold text-slate-300">PDF preview unavailable in demo mode</p>
      <p className="text-xs text-slate-500 mt-1 max-w-xs leading-relaxed">
        Connect the FastAPI backend and run a live research task to render a real
        ReportLab-generated PDF here.
      </p>
      <p className="text-[10px] text-slate-600 mt-3 font-mono max-w-md truncate">Query: "{query}"</p>
    </div>
  );
}
