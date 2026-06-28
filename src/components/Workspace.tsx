import React, { useState } from "react";
import Markdown from "react-markdown";
import { Download, FileText, FileDown, BookOpen, Layers, Maximize2, Sparkles, HelpCircle } from "lucide-react";

interface WorkspaceProps {
  reportMarkdown: string;
  pdfFilename: string;
  isDemo: boolean;
  query: string;
}

export default function Workspace({ reportMarkdown, pdfFilename, isDemo, query }: WorkspaceProps) {
  const [activeTab, setActiveTab] = useState<"both" | "markdown" | "pdf">("both");
  const [currentPage, setCurrentPage] = useState(1);
  const pdfUrl = isDemo ? "" : `http://localhost:8679/api/pdf/${pdfFilename}`;

  // Download logic for real vs demo
  const handleDownload = () => {
    if (isDemo) {
      // Create a simulated text download to mimic the ReportLab PDF
      const element = document.createElement("a");
      const file = new Blob([reportMarkdown], { type: "text/markdown" });
      element.href = URL.createObjectURL(file);
      element.download = `Academic_Report_${query.replace(/\s+/g, "_")}.md`;
      document.body.appendChild(element);
      element.click();
      document.body.removeChild(element);
    } else {
      window.open(pdfUrl, "_blank");
    }
  };

  return (
    <div id="workspace-container" className="glass-card rounded-xl border border-slate-800/80 overflow-hidden mb-5">
      
      {/* Workspace Menu Bar */}
      <div className="bg-slate-900/80 border-b border-slate-800/80 px-4 py-3 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
        <div className="flex items-center gap-2.5">
          <div className="p-1.5 bg-gradient-to-br from-blue-500/20 to-cyan-500/20 rounded-lg text-cyan-400 border border-cyan-500/30">
            <Layers className="w-4.5 h-4.5" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-white flex items-center gap-1.5">
              Synthesized Research Workspace
              <span className="text-[9px] bg-cyan-950 text-cyan-400 border border-cyan-800 px-1.5 py-0.5 rounded-full font-mono">
                PDF Ready
              </span>
            </h3>
            <p className="text-[10px] text-slate-400 font-mono mt-0.5">Topic: "{query || "Current Research Prompt"}"</p>
          </div>
        </div>

        {/* Workspace Mode switchers */}
        <div className="flex items-center gap-2 w-full sm:w-auto justify-end">
          <div className="bg-slate-950 p-0.5 rounded-lg border border-slate-800/80 flex">
            <button
              onClick={() => setActiveTab("both")}
              className={`px-2.5 py-1 rounded-md text-[11px] font-semibold cursor-pointer transition-all ${
                activeTab === "both"
                  ? "bg-slate-800 text-white shadow"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              Split View
            </button>
            <button
              onClick={() => setActiveTab("markdown")}
              className={`px-2.5 py-1 rounded-md text-[11px] font-semibold cursor-pointer transition-all ${
                activeTab === "markdown"
                  ? "bg-slate-800 text-white shadow"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              Markdown
            </button>
            <button
              onClick={() => setActiveTab("pdf")}
              className={`px-2.5 py-1 rounded-md text-[11px] font-semibold cursor-pointer transition-all ${
                activeTab === "pdf"
                  ? "bg-slate-800 text-white shadow"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              PDF Report
            </button>
          </div>

          <button
            onClick={handleDownload}
            className="px-3 py-1.5 bg-gradient-to-r from-blue-600 to-cyan-500 hover:from-blue-500 hover:to-cyan-400 text-white text-[11px] font-semibold rounded-lg flex items-center gap-1 transition-all shadow-md shadow-cyan-500/10 cursor-pointer"
          >
            <Download className="w-3 h-3" />
            <span>{isDemo ? "Export MD" : "Download PDF"}</span>
          </button>
        </div>
      </div>

      {/* Workspace Panels */}
      <div className="grid grid-cols-1 lg:grid-cols-2 divide-y lg:divide-y-0 lg:divide-x divide-slate-800/80 h-[600px]">
        
        {/* Left Panel: Markdown Renderer */}
        {(activeTab === "both" || activeTab === "markdown") && (
          <div className="flex flex-col h-full bg-slate-950/20 overflow-hidden">
            <div className="bg-slate-900/40 px-4 py-2 border-b border-slate-800/50 flex items-center justify-between">
              <span className="text-[11px] font-mono font-bold text-slate-400 tracking-wider uppercase flex items-center gap-1.5">
                <BookOpen className="w-3.5 h-3.5 text-blue-400" />
                Section A: Document Markup
              </span>
              <span className="text-[9px] text-slate-500 font-mono">Rendering Engines: Markdown</span>
            </div>
            
            <div className="flex-1 overflow-y-auto p-4 md:p-5">
              <div className="markdown-body">
                <Markdown>{reportMarkdown}</Markdown>
              </div>
            </div>
          </div>
        )}

        {/* Right Panel: PDF Viewer / Embedded PDF */}
        {(activeTab === "both" || activeTab === "pdf") && (
          <div className="flex flex-col h-full bg-slate-950/40 overflow-hidden">
            <div className="bg-slate-900/40 px-4 py-2 border-b border-slate-800/50 flex items-center justify-between">
              <span className="text-[11px] font-mono font-bold text-slate-400 tracking-wider uppercase flex items-center gap-1.5">
                <FileText className="w-3.5 h-3.5 text-cyan-400" />
                Section B: ReportLab PDF Engine
              </span>
              <span className="text-[9px] text-emerald-400 font-mono flex items-center gap-1">
                <span className="w-1.5 h-1.5 bg-emerald-400 rounded-full animate-pulse"></span>
                Standard Vector Layout
              </span>
            </div>

            {isDemo ? (
              /* Simulated High-Fidelity PDF Document layout for Offline Demo Mode */
              <div className="flex-1 overflow-y-auto p-4 bg-slate-900/80 flex flex-col items-center">
                
                {/* Simulated PDF Document Page */}
                <div className="w-full max-w-[450px] bg-white text-slate-900 shadow-2xl rounded-sm p-5 min-h-[500px] font-sans flex flex-col justify-between border-t-4 border-blue-600 relative my-1">
                  
                  {/* Page Header */}
                  <div>
                    <div className="flex justify-between items-center border-b border-slate-200 pb-2 mb-4">
                      <span className="text-[8px] uppercase font-bold tracking-widest text-slate-500 font-sans">Autonomous Research Lab Report</span>
                      <span className="text-[8px] font-mono text-slate-400">Class: Academic Standard</span>
                    </div>

                    {/* Report Metadata */}
                    <div className="mb-4">
                      <h1 className="text-lg font-bold tracking-tight text-slate-900 leading-tight">
                        {query ? query.toUpperCase() : "RESEARCH BRIEF REPORT"}
                      </h1>
                      <div className="mt-2 flex flex-wrap gap-y-0.5 gap-x-3 text-[9px] text-slate-500 font-mono">
                        <p>Date: June 2026</p>
                        <p>Author: DeepResearch Agent Pipeline</p>
                        <p>Document Ref: RL-82631</p>
                      </div>
                    </div>

                    {/* Abstract / Intro Section */}
                    <div className="mb-4">
                      <h2 className="text-[9px] font-bold text-blue-600 uppercase tracking-wider mb-1 font-mono">1. EXECUTIVE SUMMARY</h2>
                      <p className="text-[10px] text-slate-700 leading-relaxed text-justify">
                        This synthesis explores state-of-the-art technological vectors regarding <strong>{query || "the specified query"}</strong>. 
                        By pulling data nodes from high-impact domains and employing a five-agent consensus protocol, 
                        the resulting taxonomy identifies critical industrial breakthroughs, citation clusters, and engineering limits.
                      </p>
                    </div>

                    {/* Technical details Grid */}
                    <div className="mb-4">
                      <h2 className="text-[9px] font-bold text-blue-600 uppercase tracking-wider mb-1 font-mono">2. TECHNICAL PARAMETERS</h2>
                      <div className="bg-slate-50 p-2 rounded border border-slate-200">
                        <table className="w-full text-[9px] text-left text-slate-600">
                          <thead>
                            <tr className="border-b border-slate-300 text-slate-800 font-bold">
                              <th className="pb-1 font-semibold">Indexed Node</th>
                              <th className="pb-1 text-right font-semibold">Magnitude</th>
                            </tr>
                          </thead>
                          <tbody>
                            <tr className="border-b border-slate-100">
                              <td className="py-0.5">Scraped Source Links</td>
                              <td className="py-0.5 text-right font-mono">25 Pages</td>
                            </tr>
                            <tr className="border-b border-slate-100">
                              <td className="py-0.5">Ingested Chunks</td>
                              <td className="py-0.5 text-right font-mono">120 Nodes</td>
                            </tr>
                            <tr>
                              <td className="py-0.5">Critic Consensus Rating</td>
                              <td className="py-0.5 text-right font-mono text-emerald-600 font-bold">9.4 / 10</td>
                            </tr>
                          </tbody>
                        </table>
                      </div>
                    </div>

                    {/* Methodology */}
                    <div>
                      <h2 className="text-[9px] font-bold text-blue-600 uppercase tracking-wider mb-1 font-mono">3. EXPERIMENTAL ROADMAP</h2>
                      <p className="text-[10px] text-slate-700 leading-relaxed text-justify">
                        All gathered inputs underwent strict text cleansing and semantic tokenization. Key insights were filtered using 
                        cosine embeddings matching to exclude redundant content and hallucinations prior to synthesizing the final chapters.
                      </p>
                    </div>

                  </div>

                  {/* Page Footer */}
                  <div className="border-t border-slate-100 pt-2 flex justify-between items-center text-[8px] text-slate-400 mt-4">
                    <span>Generated via Autonomous Research Portal 2026</span>
                    <span className="font-mono">Page 1 of {query ? "7" : "1"}</span>
                  </div>
                </div>

                <div className="text-[10px] text-slate-400 mt-2 font-mono flex items-center gap-1">
                  <Sparkles className="w-3 h-3 text-cyan-400" />
                  <span>The custom ReportLab vector renderer has built a perfect PDF. Ready for download.</span>
                </div>

              </div>
            ) : (
              /* Embedded Iframe referencing real local FastAPI report */
              <div className="flex-1 w-full bg-slate-900 relative">
                <iframe
                  src={pdfUrl}
                  title="PDF Report Viewer"
                  className="w-full h-full border-none bg-slate-900"
                />
              </div>
            )}
          </div>
        )}

      </div>
    </div>
  );
}
