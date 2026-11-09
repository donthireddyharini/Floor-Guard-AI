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
  Video,
  Image as ImageIcon,
  Layers
} from 'lucide-react';
import { RecentDetectionRow } from '../types';
import { getLocalHistory, removeLocalHistoryItem } from '../utils/historyStore';

interface HazardHistoryViewProps {
  onSelectDetection: (item: any) => void;
}

export const HazardHistoryView: React.FC<HazardHistoryViewProps> = ({ onSelectDetection }) => {
  const [detections, setDetections] = useState<RecentDetectionRow[]>([]);
  const [activeSourceTab, setActiveSourceTab] = useState<'all' | 'image' | 'video'>('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedClass, setSelectedClass] = useState('all');
  const [selectedSeverity, setSelectedSeverity] = useState('all');
  const [loading, setLoading] = useState(false);

  // Load records from backend API + persistent localStorage
  const loadDetections = async () => {
    setLoading(true);
    try {
      const localItems = getLocalHistory();
      let apiItems: any[] = [];
      try {
        const url = new URL('/api/detections', window.location.origin);
        if (activeSourceTab !== 'all') url.searchParams.set('source_type', activeSourceTab);
        if (selectedClass !== 'all') url.searchParams.set('className', selectedClass);
        if (selectedSeverity !== 'all') url.searchParams.set('severity', selectedSeverity);
        if (searchTerm) url.searchParams.set('search', searchTerm);

        const res = await fetch(url.toString());
        if (res.ok) {
          const data = await res.json();
          if (data.status === 'ok' && Array.isArray(data.detections)) {
            apiItems = data.detections;
          }
        }
      } catch (e) {
        console.warn('Backend detections endpoint unavailable, loading local history store');
      }

      // Merge local items and API items, deduplicating by ID
      const seenIds = new Set<string>();
      const combined: any[] = [];
      for (const item of [...localItems, ...apiItems]) {
        if (!seenIds.has(item.id)) {
          seenIds.add(item.id);
          combined.push(item);
        }
      }

      // Apply client-side filters
      const filtered = combined.filter((row: any) => {
        if (activeSourceTab !== 'all' && (row.source_type || 'image') !== activeSourceTab) return false;
        if (selectedClass !== 'all' && !(row.class_name || '').toLowerCase().includes(selectedClass.toLowerCase())) return false;
        if (selectedSeverity !== 'all' && row.severity !== selectedSeverity) return false;
        if (searchTerm) {
          const q = searchTerm.toLowerCase();
          const matchFilename = (row.original_filename || '').toLowerCase().includes(q);
          const matchClass = (row.class_name || '').toLowerCase().includes(q);
          const matchLoc = (row.location || '').toLowerCase().includes(q);
          if (!matchFilename && !matchClass && !matchLoc) return false;
        }
        return true;
      });

      filtered.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());
      setDetections(filtered);
    } catch (err) {
      console.error('Error loading hazard detections history:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDetections();
    const handleUpdate = () => loadDetections();
    window.addEventListener('floorguard:history_updated', handleUpdate);
    return () => window.removeEventListener('floorguard:history_updated', handleUpdate);
  }, [activeSourceTab, selectedClass, selectedSeverity, searchTerm]);

  // Export CSV
  const handleExportCsv = () => {
    window.location.href = '/api/analytics/export';
  };

  // Delete record
  const handleDelete = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!confirm('Are you sure you want to remove this detection log?')) return;
    removeLocalHistoryItem(id);
    try {
      await fetch(`/api/detections/${id}`, { method: 'DELETE' });
    } catch (err) {
      // ignore
    }
    setDetections((prev) => prev.filter((d) => d.id !== id));
  };

  const imageCount = detections.filter(d => (d as any).source_type === 'image').length;
  const videoCount = detections.filter(d => (d as any).source_type === 'video').length;

  return (
    <div className="p-6 space-y-6 max-w-[1720px] mx-auto">
      {/* Top Source Tabs: Separate Video Analysis History & Image History */}
      <div className="flex flex-wrap items-center justify-between gap-4 bg-[#131b29] border border-[#1e2c3f] rounded-2xl p-3">
        <div className="flex items-center gap-2">
          <button
            onClick={() => setActiveSourceTab('all')}
            className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold transition-all cursor-pointer ${
              activeSourceTab === 'all'
                ? 'bg-[#22c55e] text-black shadow-md'
                : 'bg-[#182335] text-slate-300 hover:bg-[#202e44] border border-[#283952]'
            }`}
          >
            <Layers className="w-3.5 h-3.5" />
            <span>All Hazard Records</span>
          </button>

          <button
            onClick={() => setActiveSourceTab('image')}
            className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold transition-all cursor-pointer ${
              activeSourceTab === 'image'
                ? 'bg-[#38bdf8] text-black shadow-md'
                : 'bg-[#182335] text-slate-300 hover:bg-[#202e44] border border-[#283952]'
            }`}
          >
            <ImageIcon className="w-3.5 h-3.5" />
            <span>Image Hazard History</span>
          </button>

          <button
            onClick={() => setActiveSourceTab('video')}
            className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold transition-all cursor-pointer ${
              activeSourceTab === 'video'
                ? 'bg-[#f59e0b] text-black shadow-md'
                : 'bg-[#182335] text-slate-300 hover:bg-[#202e44] border border-[#283952]'
            }`}
          >
            <Video className="w-3.5 h-3.5" />
            <span>Video Analysis History</span>
            <span className="ml-1 text-[10px] bg-black/30 px-1.5 py-0.5 rounded-full font-mono">
              Dedicated
            </span>
          </button>
        </div>

        <div className="text-xs text-slate-400 font-mono">
          Showing {detections.length} recorded incident(s)
        </div>
      </div>

      {/* Filter Bar */}
      <div className="bg-[#131b29] border border-[#1e2c3f] rounded-2xl p-4 flex flex-wrap items-center justify-between gap-4">
        {/* Search Input */}
        <div className="relative flex-1 min-w-[260px]">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder={
              activeSourceTab === 'video'
                ? 'Search video inspection keyframes, filenames, or locations...'
                : 'Search by filename, location, or class...'
            }
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 rounded-xl bg-[#0d131f] border border-[#1e2c3f] text-xs text-white placeholder-slate-500 focus:outline-none focus:border-[#22c55e]"
          />
        </div>

        {/* Filters & Export */}
        <div className="flex flex-wrap items-center gap-3">
          {/* Class Filter with all 12 classes */}
          <select
            value={selectedClass}
            onChange={(e) => setSelectedClass(e.target.value)}
            className="px-3 py-2 rounded-xl bg-[#0d131f] border border-[#1e2c3f] text-xs text-slate-200 focus:outline-none"
          >
            <option value="all">All 12 Hazard Classes</option>
            <option value="Water Spill">Water Spill</option>
            <option value="Oil Spill">Oil Spill</option>
            <option value="Chemical Spill">Chemical Spill</option>
            <option value="Broken Glass">Broken Glass</option>
            <option value="Food Waste">Food Waste & Sauce</option>
            <option value="Cable Cord">Cable / Wire Hazard</option>
            <option value="Floor Crack">Floor Crack & Pothole</option>
            <option value="Improper Mat">Curled / Improper Mat</option>
            <option value="Obstacle Debris">Obstacle / Pallet</option>
            <option value="Trash Litter">Trash / Litter</option>
            <option value="Mud Dirt">Mud / Dirt</option>
            <option value="Stairs Hazard">Stairs Hazard</option>
            <option value="Clean Floor">Clean Floor</option>
          </select>

          {/* Severity Filter */}
          <select
            value={selectedSeverity}
            onChange={(e) => setSelectedSeverity(e.target.value)}
            className="px-3 py-2 rounded-xl bg-[#0d131f] border border-[#1e2c3f] text-xs text-slate-200 focus:outline-none"
          >
            <option value="all">All Severities</option>
            <option value="Safe">Safe</option>
            <option value="Medium">Medium</option>
            <option value="High">High</option>
            <option value="Critical">Critical</option>
          </select>

          {/* Export Button */}
          <button
            onClick={handleExportCsv}
            className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-[#192437] hover:bg-[#202e46] border border-[#2a3c56] text-slate-200 font-semibold text-xs transition-colors cursor-pointer"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Export CSV</span>
          </button>
        </div>
      </div>

      {/* History Table */}
      <div className="bg-[#131b29] border border-[#1e2c3f] rounded-2xl p-5 overflow-x-auto shadow-sm">
        <table className="w-full text-left text-xs font-mono">
          <thead>
            <tr className="border-b border-[#1b2738] text-[10px] text-slate-400">
              <th className="pb-3">Timestamp</th>
              <th className="pb-3">Source Type</th>
              <th className="pb-3">Evidence Thumbnail</th>
              <th className="pb-3">Inspection Asset</th>
              <th className="pb-3">Class</th>
              <th className="pb-3 text-right">Confidence</th>
              <th className="pb-3 text-right">Area</th>
              <th className="pb-3 text-right">Severity</th>
              <th className="pb-3 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[#172335]">
            {detections.length === 0 ? (
              <tr>
                <td colSpan={9} className="py-8 text-center text-slate-500 font-sans">
                  No {activeSourceTab === 'video' ? 'video analysis' : activeSourceTab === 'image' ? 'image detection' : ''} logs found matching query.
                </td>
              </tr>
            ) : (
              detections.map((row) => (
                <tr
                  key={row.id}
                  onClick={() => onSelectDetection(row)}
                  className="hover:bg-[#182335] transition-colors cursor-pointer group"
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
                    {(row as any).source_type === 'video' ? (
                      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-bold bg-amber-500/20 text-amber-400 border border-amber-500/30">
                        <Video className="w-3 h-3" />
                        Video
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-bold bg-sky-500/20 text-sky-400 border border-sky-500/30">
                        <ImageIcon className="w-3 h-3" />
                        Image
                      </span>
                    )}
                  </td>
                  <td className="py-3">
                    <div className="w-10 h-7 rounded overflow-hidden bg-black border border-[#22334c] relative group-hover:scale-105 transition-transform">
                      <img
                        src={row.evidence_path || '/assets/samples/thumb_water_spill.jpg'}
                        alt={row.class_name}
                        className="w-full h-full object-cover"
                        onError={(e) => {
                          (e.target as HTMLImageElement).src = '/assets/samples/thumb_water_spill.jpg';
                        }}
                      />
                    </div>
                  </td>
                  <td className="py-3 text-[11px] font-sans text-slate-300 truncate max-w-[180px]">
                    <div className="font-semibold">{row.original_filename}</div>
                    <div className="text-[10px] text-slate-400 font-mono">{row.location}</div>
                  </td>
                  <td className="py-3 font-sans font-semibold text-white">
                    {row.class_name}
                  </td>
                  <td className="py-3 text-right font-bold text-white tabular-nums">
                    {Math.round(row.confidence * 100)}%
                  </td>
                  <td className="py-3 text-right text-slate-400 tabular-nums">
                    {row.estimated_area ? `${row.estimated_area} m²` : '—'}
                  </td>
                  <td className="py-3 text-right">
                    <span
                      className={`px-2 py-0.5 rounded text-[10px] font-bold text-white ${
                        row.severity === 'Safe'
                          ? 'bg-[#15803d]'
                          : row.severity === 'Medium'
                          ? 'bg-[#eab308]'
                          : 'bg-[#ef4444]'
                      }`}
                    >
                      {row.severity}
                    </span>
                  </td>
                  <td className="py-3 text-right">
                    <button
                      onClick={(e) => handleDelete(row.id, e)}
                      className="p-1 hover:text-[#ef4444] text-slate-500 transition-colors"
                      title="Delete entry"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};
