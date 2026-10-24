import React, { useState, useEffect } from 'react';
import {
  History,
  Search,
  Filter,
  Download,
  Trash2,
  Eye,
  AlertTriangle,
  CheckCircle,
  FileSpreadsheet,
  LayoutGrid,
  List,
  Layers,
  Video,
  Image as ImageIcon,
  Clock,
  Sparkles,
  RefreshCw
} from 'lucide-react';
import { HistoryRunRow } from '../types';

interface HazardHistoryViewProps {
  onSelectDetection: (item: any) => void;
}

export const HazardHistoryView: React.FC<HazardHistoryViewProps> = ({ onSelectDetection }) => {
  const [historyRuns, setHistoryRuns] = useState<HistoryRunRow[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedSourceType, setSelectedSourceType] = useState('all');
  const [viewMode, setViewMode] = useState<'table' | 'grid'>('table');
  const [loading, setLoading] = useState(false);

  // Load records from backend API
  const loadHistory = async () => {
    setLoading(true);
    try {
      const url = new URL('/api/history', window.location.origin);
      if (selectedSourceType !== 'all') url.searchParams.set('sourceType', selectedSourceType);
      if (searchTerm) url.searchParams.set('search', searchTerm);

      const res = await fetch(url.toString());
      const data = await res.json();
      if (data.status === 'ok' && Array.isArray(data.history)) {
        setHistoryRuns(data.history);
      } else {
        // Fallback to /api/detections
        const fallbackRes = await fetch('/api/detections');
        const fallbackData = await fallbackRes.json();
        if (fallbackData.status === 'ok') {
          const mapped = (fallbackData.detections || []).map((d: any) => ({
            id: d.id,
            source_type: d.source_type || 'image',
            original_filename: d.original_filename,
            original_image_url: d.evidence_path,
            annotated_image_url: d.evidence_path,
            thumb_url: d.evidence_path,
            created_at: d.created_at,
            status: 'completed',
            processing_duration_ms: 120,
            model_version: 'YOLOv8s',
            total_detections: 1,
            summary: `Detected ${d.class_name} (${Math.round(d.confidence * 100)}%)`,
            detections: [d]
          }));
          setHistoryRuns(mapped);
        }
      }
    } catch (err) {
      console.error('Failed to load history:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadHistory();
  }, [selectedSourceType, searchTerm]);

  // Export CSV
  const handleExportCsv = () => {
    window.location.href = '/api/analytics/export';
  };

  // Delete record
  const handleDelete = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!confirm(`Are you sure you want to permanently remove inspection run ${id}?`)) return;
    try {
      await fetch(`/api/history/${id}`, { method: 'DELETE' });
      setHistoryRuns((prev) => prev.filter((d) => d.id !== id));
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="p-6 space-y-6 max-w-[1720px] mx-auto">
      {/* Top Filter & Actions Bar */}
      <div className="bg-[#111827] border border-[#1e293b] rounded-2xl p-4 flex flex-wrap items-center justify-between gap-4 shadow-sm">
        {/* Search Input */}
        <div className="relative flex-1 min-w-[280px]">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search by filename, run ID, or hazard summary..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-[#0a0f1d] border border-[#1e293b] text-xs text-white placeholder-slate-500 focus:outline-none focus:border-[#f97316]"
          />
        </div>

        {/* Filters & Actions */}
        <div className="flex flex-wrap items-center gap-2.5">
          {/* Source Type Filter */}
          <select
            value={selectedSourceType}
            onChange={(e) => setSelectedSourceType(e.target.value)}
            className="px-3 py-2 rounded-xl bg-[#0a0f1d] border border-[#1e293b] text-xs text-slate-200 focus:outline-none cursor-pointer"
          >
            <option value="all">All Media (Images &amp; Videos)</option>
            <option value="image">Images Only</option>
            <option value="video">Videos Only</option>
          </select>

          {/* View Mode Toggle */}
          <div className="bg-[#0a0f1d] p-1 rounded-xl border border-[#1e293b] flex items-center gap-1">
            <button
              onClick={() => setViewMode('table')}
              className={`p-1.5 rounded-lg transition-colors cursor-pointer ${
                viewMode === 'table' ? 'bg-[#f97316] text-white' : 'text-slate-400 hover:text-white'
              }`}
              title="Table View"
            >
              <List className="w-4 h-4" />
            </button>
            <button
              onClick={() => setViewMode('grid')}
              className={`p-1.5 rounded-lg transition-colors cursor-pointer ${
                viewMode === 'grid' ? 'bg-[#f97316] text-white' : 'text-slate-400 hover:text-white'
              }`}
              title="Card Grid View"
            >
              <LayoutGrid className="w-4 h-4" />
            </button>
          </div>

          {/* Refresh Button */}
          <button
            onClick={loadHistory}
            className="p-2 rounded-xl bg-[#1e293b] hover:bg-[#334155] text-slate-300 hover:text-white transition-colors cursor-pointer"
            title="Refresh History"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>

          {/* Export Button */}
          <button
            onClick={handleExportCsv}
            className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-[#1e293b] hover:bg-[#334155] border border-[#2a384f] text-slate-200 font-semibold text-xs transition-colors cursor-pointer"
          >
            <Download className="w-3.5 h-3.5 text-[#f97316]" />
            <span>Export CSV</span>
          </button>
        </div>
      </div>

      {/* Main Content Area */}
      {viewMode === 'table' ? (
        <div className="bg-[#111827] border border-[#1e293b] rounded-3xl p-5 overflow-x-auto shadow-sm">
          <table className="w-full text-left text-xs font-mono">
            <thead>
              <tr className="border-b border-[#1e293b] text-[11px] text-slate-400 uppercase tracking-wider">
                <th className="pb-3.5">Timestamp</th>
                <th className="pb-3.5">Inspection Preview</th>
                <th className="pb-3.5">Filename</th>
                <th className="pb-3.5">Media</th>
                <th className="pb-3.5">Model Checkpoint</th>
                <th className="pb-3.5 text-center">Hazards Found</th>
                <th className="pb-3.5">Status</th>
                <th className="pb-3.5 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#172233]">
              {loading && historyRuns.length === 0 ? (
                <tr>
                  <td colSpan={8} className="py-12 text-center text-slate-500 font-sans">
                    <div className="flex flex-col items-center gap-2">
                      <RefreshCw className="w-5 h-5 animate-spin text-[#f97316]" />
                      <span>Loading inspection history...</span>
                    </div>
                  </td>
                </tr>
              ) : historyRuns.length === 0 ? (
                <tr>
                  <td colSpan={8} className="py-12 text-center text-slate-500 font-sans">
                    <div className="flex flex-col items-center gap-2">
                      <History className="w-6 h-6 text-slate-600" />
                      <span className="text-sm font-semibold text-slate-400">No inspection history records found.</span>
                      <span className="text-xs text-slate-500">Run an image inspection or video analysis to populate the database.</span>
                    </div>
                  </td>
                </tr>
              ) : (
                historyRuns.map((row) => {
                  const isSafe = row.total_detections === 0;
                  return (
                    <tr
                      key={row.id}
                      onClick={() => onSelectDetection(row)}
                      className="hover:bg-[#162132] transition-colors cursor-pointer group"
                    >
                      <td className="py-3 text-[11px] text-slate-400 whitespace-nowrap">
                        {new Date(row.created_at).toLocaleString('en-US', {
                          month: 'short',
                          day: 'numeric',
                          hour: '2-digit',
                          minute: '2-digit'
                        })}
                      </td>
                      <td className="py-3">
                        <div className="w-12 h-8 rounded-lg overflow-hidden bg-black border border-[#22334c] flex items-center justify-center">
                          <img
                            src={row.thumb_url || row.annotated_image_url || row.original_image_url}
                            alt={row.original_filename}
                            className="w-full h-full object-cover"
                            onError={(e) => {
                              (e.target as HTMLElement).style.display = 'none';
                              const p = (e.target as HTMLElement).parentElement;
                              if (p) p.innerText = 'NO IMG';
                            }}
                          />
                        </div>
                      </td>
                      <td className="py-3 font-sans font-medium text-slate-200 truncate max-w-[180px]">
                        {row.original_filename}
                      </td>
                      <td className="py-3">
                        <span className="flex items-center gap-1.5 text-slate-400">
                          {row.source_type === 'video' ? (
                            <><Video className="w-3.5 h-3.5 text-blue-400" /> Video</>
                          ) : (
                            <><ImageIcon className="w-3.5 h-3.5 text-[#f97316]" /> Image</>
                          )}
                        </span>
                      </td>
                      <td className="py-3 text-slate-400 truncate max-w-[160px]">
                        {row.model_version || 'YOLOv8s'}
                      </td>
                      <td className="py-3 text-center">
                        <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                          isSafe
                            ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                            : 'bg-red-500/20 text-red-400 border border-red-500/30'
                        }`}>
                          {isSafe ? '0 (Clean)' : `${row.total_detections} Hazards`}
                        </span>
                      </td>
                      <td className="py-3">
                        <span className="text-[10px] px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
                          {row.status}
                        </span>
                      </td>
                      <td className="py-3 text-right">
                        <button
                          onClick={(e) => handleDelete(row.id, e)}
                          className="p-1.5 hover:text-[#ef4444] text-slate-500 transition-colors rounded-lg hover:bg-[#202e46] cursor-pointer"
                          title="Delete entry"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      ) : (
        /* Card Grid View */
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {historyRuns.map((row) => {
            const isSafe = row.total_detections === 0;
            return (
              <div
                key={row.id}
                onClick={() => onSelectDetection(row)}
                className="bg-[#111827] border border-[#1e293b] hover:border-[#f97316]/50 rounded-3xl overflow-hidden transition-all duration-200 cursor-pointer flex flex-col group shadow-sm hover:shadow-xl"
              >
                <div className="aspect-16/10 bg-[#070b14] relative overflow-hidden flex items-center justify-center border-b border-[#1e293b]">
                  <img
                    src={row.thumb_url || row.annotated_image_url || row.original_image_url}
                    alt={row.original_filename}
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                    onError={(e) => {
                      (e.target as HTMLElement).style.display = 'none';
                      const p = (e.target as HTMLElement).parentElement;
                      if (p) {
                        p.className = 'w-full h-full flex items-center justify-center text-slate-500 text-xs font-mono';
                        p.innerText = 'Preview Unavailable';
                      }
                    }}
                  />
                  <div className="absolute top-2.5 left-2.5 flex items-center gap-1.5">
                    <span className="text-[10px] px-2 py-0.5 rounded-lg bg-black/70 backdrop-blur-md text-white font-mono uppercase font-bold flex items-center gap-1">
                      {row.source_type === 'video' ? <Video className="w-3 h-3 text-blue-400" /> : <ImageIcon className="w-3 h-3 text-[#f97316]" />}
                      {row.source_type}
                    </span>
                  </div>
                  <div className="absolute top-2.5 right-2.5">
                    <span className={`text-[10px] px-2 py-0.5 rounded-lg font-mono font-bold ${
                      isSafe ? 'bg-emerald-950/80 text-emerald-400 border border-emerald-500/40' : 'bg-red-950/80 text-red-400 border border-red-500/40'
                    }`}>
                      {isSafe ? '0 Hazards' : `${row.total_detections} Hazards`}
                    </span>
                  </div>
                </div>

                <div className="p-4 space-y-2 flex-1 flex flex-col justify-between font-mono">
                  <div>
                    <h4 className="text-xs font-bold text-white truncate font-sans">
                      {row.original_filename}
                    </h4>
                    <p className="text-[10px] text-slate-400 line-clamp-2 mt-1">
                      {row.summary || 'Completed inference run.'}
                    </p>
                  </div>

                  <div className="pt-2 border-t border-[#1e293b] flex items-center justify-between text-[10px] text-slate-500">
                    <span>{new Date(row.created_at).toLocaleDateString()}</span>
                    <button
                      onClick={(e) => handleDelete(row.id, e)}
                      className="p-1 hover:text-red-400 text-slate-500 transition-colors"
                      title="Delete"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
