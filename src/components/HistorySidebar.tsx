import React, { useState } from "react";
import { History, ChevronLeft, ChevronRight, Download, Calendar, Tag, Trash2, Search, Sparkles } from "lucide-react";
import { HistoryItem } from "../types";

interface HistorySidebarProps {
  history: HistoryItem[];
  onSelectItem: (item: HistoryItem) => void;
  onClearHistory?: () => void;
  isOpen: boolean;
  setIsOpen: (val: boolean) => void;
  isDemo: boolean;
}

export default function HistorySidebar({
  history,
  onSelectItem,
  onClearHistory,
  isOpen,
  setIsOpen,
  isDemo,
}: HistorySidebarProps) {
  const [searchTerm, setSearchTerm] = useState("");

  const filteredHistory = history.filter((item) =>
    item.topic.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div
      id="history-sidebar"
      className={`fixed top-0 right-0 h-full z-40 bg-slate-950 border-l border-slate-800 transition-all duration-300 flex ${
        isOpen ? "w-[310px]" : "w-0 border-l-0"
      }`}
    >
      {/* Toggle Tab Trigger handle */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="absolute top-24 left-[-36px] w-[36px] h-9 bg-slate-900 hover:bg-slate-800 text-cyan-400 border border-r-0 border-slate-800 rounded-l-lg flex items-center justify-center cursor-pointer shadow-lg hover:text-cyan-300 transition-colors"
        title={isOpen ? "Collapse History Panel" : "Expand Research Logs"}
      >
        <History className={`w-4 h-4 ${!isOpen ? "animate-pulse" : ""}`} />
      </button>

      {/* Sidebar Contents */}
      {isOpen && (
        <div className="flex flex-col w-full h-full p-4 select-none">
          {/* Sidebar Header */}
          <div className="flex items-center justify-between pb-3 border-b border-slate-800">
            <div className="flex items-center gap-1.5">
              <History className="w-4 h-4 text-cyan-400" />
              <div>
                <h3 className="font-bold text-white text-xs">Research Indexes</h3>
                <p className="text-[9px] text-slate-400 font-mono">Archive & Local Reports</p>
              </div>
            </div>
            <button
              onClick={() => setIsOpen(false)}
              className="p-1 hover:bg-slate-900 rounded-md text-slate-400 hover:text-white cursor-pointer"
            >
              <ChevronRight className="w-3.5 h-3.5" />
            </button>
          </div>

          {/* Search bar inside Sidebar */}
          <div className="my-2.5 relative">
            <Search className="w-3.5 h-3.5 text-slate-500 absolute left-2.5 top-2" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search past reports..."
              className="w-full bg-slate-900/60 border border-slate-800 focus:border-cyan-500/80 rounded-md pl-8 pr-2 py-1 text-[11px] text-white placeholder-slate-500 focus:outline-none transition-colors"
            />
          </div>

          {/* History Lists */}
          <div className="flex-1 overflow-y-auto space-y-2 pr-1 scrollbar-thin">
            {filteredHistory.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-48 text-center px-2">
                <div className="p-2.5 bg-slate-900 rounded-full text-slate-600 mb-1.5">
                  <History className="w-5 h-5" />
                </div>
                <p className="text-[11px] text-slate-400 font-semibold">No reports index found</p>
                <p className="text-[9px] text-slate-500 mt-1 leading-normal">
                  Your generated summaries and academic PDFs will appear here for immediate access.
                </p>
              </div>
            ) : (
              filteredHistory.map((item) => (
                <div
                  key={item.id}
                  onClick={() => onSelectItem(item)}
                  className="bg-slate-900/40 border border-slate-850 hover:border-slate-700 p-2.5 rounded-lg transition-all hover:bg-slate-900/60 cursor-pointer relative group"
                >
                  <div className="flex items-start justify-between mb-1">
                    <h4 className="font-bold text-[11px] text-slate-200 group-hover:text-cyan-400 transition-colors line-clamp-1 pr-3">
                      {item.topic}
                    </h4>
                    <span className="text-[8px] bg-slate-950 px-1.5 py-0.5 rounded border border-slate-800 text-slate-400 font-mono uppercase">
                      {item.metadata.detail_level}
                    </span>
                  </div>

                  <div className="grid grid-cols-2 gap-1 text-[8px] text-slate-400 font-mono mb-2">
                    <p className="flex items-center gap-1">
                      <Calendar className="w-2.5 h-2.5 text-slate-500" />
                      {new Date(item.timestamp).toLocaleDateString()}
                    </p>
                    <p className="flex items-center gap-1 justify-end">
                      <Tag className="w-2.5 h-2.5 text-slate-500" />
                      {item.metadata.chunks_included} chunks
                    </p>
                  </div>

                  <div className="flex items-center justify-between pt-1.5 border-t border-slate-800/40 text-[8px]">
                    <span className="text-slate-400 font-mono">
                      Sources: {item.metadata.pages_processed} scraped
                    </span>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        onSelectItem(item);
                      }}
                      className="text-cyan-400 hover:text-cyan-300 font-bold flex items-center gap-0.5 transition-colors"
                    >
                      <Download className="w-2.5 h-2.5" />
                      <span>Review</span>
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>

          {/* Sidebar Footer with toggle indicators */}
          {onClearHistory && filteredHistory.length > 0 && (
            <div className="pt-3 border-t border-slate-800 mt-auto flex flex-col gap-1.5">
              <button
                onClick={onClearHistory}
                className="w-full py-1.5 bg-slate-900 hover:bg-red-950/20 hover:text-red-400 hover:border-red-900/30 text-slate-400 text-[11px] font-semibold rounded-md border border-slate-800 flex items-center justify-center gap-1 transition-all cursor-pointer"
              >
                <Trash2 className="w-3 h-3" />
                <span>Clear Local Archive</span>
              </button>
              
              <p className="text-[9px] text-slate-500 text-center font-mono flex items-center justify-center gap-1">
                <Sparkles className="w-2.5 h-2.5 text-cyan-400" />
                <span>Auto-cached locally</span>
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
