"use client";

import { useState } from "react";
import { FileText, Globe, ExternalLink, ChevronDown, ChevronRight, CheckCircle2, ShieldCheck, Tag } from "lucide-react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

export interface CitationItem {
  id: string; // e.g. "[1]"
  index: number;
  source_id?: string;
  source_name: string;
  source_type: string;
  source_url?: string | null;
  page?: number | null;
  chunk_index?: number | null;
  snippet: string;
}

export function Citation({ 
  citation, 
  onSelect 
}: { 
  citation: CitationItem; 
  onSelect?: (citation: CitationItem) => void; 
}) {
  return (
    <button
      onClick={() => onSelect?.(citation)}
      className="inline-flex items-center gap-1 px-2 py-0.5 mx-0.5 text-xs font-medium rounded bg-emerald-950/60 text-emerald-400 border border-emerald-700/50 hover:bg-emerald-900/60 hover:border-emerald-500 transition-colors"
      title={`Source: ${citation.source_name}${citation.page ? ` (Page ${citation.page})` : ''}`}
    >
      <span>{citation.id}</span>
      <span className="truncate max-w-[120px] text-[11px] text-zinc-400">{citation.source_name}</span>
      {citation.page ? <span className="text-[10px] text-emerald-300">p.{citation.page}</span> : null}
    </button>
  );
}

export function CitationList({ 
  citations, 
  onSelectCitation 
}: { 
  citations: CitationItem[]; 
  onSelectCitation?: (citation: CitationItem) => void; 
}) {
  const [isOpen, setIsOpen] = useState(true);

  if (!citations || citations.length === 0) return null;

  return (
    <div className="mt-4 border border-zinc-800/80 rounded-lg overflow-hidden bg-zinc-950/60">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between p-3 text-xs font-semibold text-zinc-300 hover:bg-zinc-900/40 transition-colors uppercase tracking-wider"
      >
        <div className="flex items-center gap-2">
          <ShieldCheck className="w-4 h-4 text-emerald-400" />
          <span>Verified Sources & Citations ({citations.length})</span>
        </div>
        {isOpen ? <ChevronDown className="w-3.5 h-3.5 text-zinc-500" /> : <ChevronRight className="w-3.5 h-3.5 text-zinc-500" />}
      </button>

      {isOpen && (
        <div className="p-3 border-t border-zinc-800/60 grid grid-cols-1 md:grid-cols-2 gap-2.5">
          {citations.map((c) => (
            <div
              key={c.id}
              onClick={() => onSelectCitation?.(c)}
              className="cursor-pointer text-xs bg-zinc-900/80 hover:bg-zinc-900 p-2.5 rounded-md border border-zinc-800 hover:border-emerald-500/50 transition-all flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between gap-1.5 mb-1.5 font-medium text-emerald-400">
                  <div className="flex items-center gap-1.5 truncate">
                    <span className="px-1.5 py-0.2 bg-emerald-950 text-emerald-400 border border-emerald-800/50 rounded font-mono text-[10px]">
                      {c.id}
                    </span>
                    {c.source_type === "WIKIPEDIA" || c.source_type === "WEBSITE" ? (
                      <Globe className="w-3.5 h-3.5 text-blue-400 shrink-0" />
                    ) : (
                      <FileText className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                    )}
                    <span className="truncate">{c.source_name}</span>
                  </div>
                  {c.page ? (
                    <span className="text-[10px] text-zinc-400 bg-zinc-800 px-1.5 py-0.5 rounded shrink-0">
                      Page {c.page}
                    </span>
                  ) : null}
                </div>
                <p className="text-zinc-400 text-[11px] leading-relaxed line-clamp-2 italic">
                  "{c.snippet}"
                </p>
              </div>

              {c.source_url && (
                <a
                  href={c.source_url}
                  target="_blank"
                  rel="noreferrer"
                  onClick={(e) => e.stopPropagation()}
                  className="inline-flex items-center gap-1 text-[10px] text-emerald-500 hover:underline mt-2"
                >
                  <span>View Source</span>
                  <ExternalLink className="w-2.5 h-2.5" />
                </a>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export function EvidencePanel({
  selectedCitation,
  onClose
}: {
  selectedCitation: CitationItem | null;
  onClose: () => void;
}) {
  if (!selectedCitation) return null;

  return (
    <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex justify-end">
      <div className="w-full max-w-md bg-zinc-950 border-l border-zinc-800 h-full p-6 flex flex-col justify-between overflow-y-auto shadow-2xl animate-in slide-in-from-right duration-200">
        <div>
          <div className="flex items-center justify-between pb-4 border-b border-zinc-800">
            <div className="flex items-center gap-2">
              <span className="px-2 py-0.5 bg-emerald-950 text-emerald-400 border border-emerald-700/60 rounded font-mono text-xs font-semibold">
                {selectedCitation.id}
              </span>
              <h3 className="font-semibold text-sm text-zinc-100 truncate max-w-[240px]">
                Evidence Inspection
              </h3>
            </div>
            <button
              onClick={onClose}
              className="text-zinc-400 hover:text-zinc-200 text-xs px-2 py-1 rounded bg-zinc-900 border border-zinc-800"
            >
              Close
            </button>
          </div>

          <div className="mt-4 space-y-4 text-xs">
            <div>
              <span className="text-zinc-500 font-medium uppercase tracking-wider text-[10px]">Source Name</span>
              <div className="text-zinc-200 mt-1 font-medium flex items-center gap-2">
                <FileText className="w-4 h-4 text-emerald-400" />
                <span>{selectedCitation.source_name}</span>
              </div>
            </div>

            {selectedCitation.page ? (
              <div>
                <span className="text-zinc-500 font-medium uppercase tracking-wider text-[10px]">Verified Page</span>
                <div className="text-zinc-200 mt-1">Page {selectedCitation.page}</div>
              </div>
            ) : null}

            {selectedCitation.chunk_index !== undefined && selectedCitation.chunk_index !== null ? (
              <div>
                <span className="text-zinc-500 font-medium uppercase tracking-wider text-[10px]">Chunk Index</span>
                <div className="text-zinc-200 mt-1 font-mono">#{selectedCitation.chunk_index}</div>
              </div>
            ) : null}

            <div>
              <span className="text-zinc-500 font-medium uppercase tracking-wider text-[10px]">Verified Source Passage</span>
              <div className="mt-1.5 p-3 rounded-lg bg-zinc-900 border border-zinc-800 text-zinc-300 leading-relaxed italic text-xs">
                "{selectedCitation.snippet}"
              </div>
            </div>

            {selectedCitation.source_url && (
              <div>
                <span className="text-zinc-500 font-medium uppercase tracking-wider text-[10px]">Origin URL</span>
                <a
                  href={selectedCitation.source_url}
                  target="_blank"
                  rel="noreferrer"
                  className="text-emerald-400 hover:underline block mt-1 truncate"
                >
                  {selectedCitation.source_url}
                </a>
              </div>
            )}
          </div>
        </div>

        <div className="pt-4 border-t border-zinc-800/80 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded text-xs font-medium"
          >
            Done
          </button>
        </div>
      </div>
    </div>
  );
}

export function RelatedKnowledge({ entities }: { entities?: string[] }) {
  if (!entities || entities.length === 0) return null;

  return (
    <div className="mt-3 flex items-center gap-2 flex-wrap">
      <span className="text-[11px] text-zinc-500 font-medium flex items-center gap-1">
        <Tag className="w-3 h-3 text-zinc-500" />
        Related:
      </span>
      {entities.map((ent, i) => (
        <span
          key={i}
          className="text-[10px] px-2 py-0.5 bg-zinc-900 border border-zinc-800 text-zinc-400 rounded-full"
        >
          {ent}
        </span>
      ))}
    </div>
  );
}
