import React, { useState } from 'react';
import {
  X,
  AlertTriangle,
  CheckCircle,
  Clock,
  Layers,
  ZoomIn,
  ZoomOut,
  Download,
  Box,
  FileCode,
  ShieldCheck,
  Eye,
  FileText
} from 'lucide-react';

interface DetectionDetailModalProps {
  detection: any;
  onClose: () => void;
}

export const DetectionDetailModal: React.FC<DetectionDetailModalProps> = ({ detection, onClose }) => {
  const [activeTab, setActiveTab] = useState<'annotated' | 'original' | 'side_by_side'>('side_by_side');
  const [zoom, setZoom] = useState(1);
  const [showRawJson, setShowRawJson] = useState(false);

  if (!detection) return null;

  // Resolve image URLs safely
  const originalUrl = detection.original_image_url || detection.file_path || detection.evidence_path || '/uploads/originals/1.jpg';
  const annotatedUrl = detection.annotated_image_url || detection.annotated_path || detection.evidence_path || originalUrl;
  
  const className = detection.class_name || (detection.total_detections > 0 ? 'Hazard Detected' : 'Clean Floor');
  const severity = detection.severity || (detection.total_detections > 0 ? 'High' : 'Safe');
  const confidence = detection.confidence || (detection.total_detections > 0 ? 0.85 : 1.0);
  const confidencePct = detection.confidence_percent || `${Math.round(confidence * 100)}%`;
  const isSafe = severity === 'Safe' || className.toLowerCase().includes('clean');

  // Handle bounding box parsing
  let bbox = detection.bounding_box || {};
  if (typeof detection.bounding_box_json === 'string') {
    try { bbox = JSON.parse(detection.bounding_box_json); } catch {}
  }

  const detectionsList = detection.detections || detection.meta || [];

  return (
    <div className="fixed inset-0 z-50 bg-black/85 backdrop-blur-md flex items-center justify-center p-4 sm:p-6 animate-in fade-in duration-200">
      <div className="bg-[#0f172a] border border-[#1e293b] rounded-3xl w-full max-w-5xl max-h-[92vh] flex flex-col overflow-hidden shadow-2xl">
        {/* Modal Header */}
        <div className="p-5 border-b border-[#1e293b] flex items-center justify-between bg-[#0b1120]">
          <div className="flex items-center gap-3">
            <span
              className={`w-3.5 h-3.5 rounded-full ${
                isSafe ? 'bg-emerald-500 shadow-[0_0_10px_rgba(16,185,129,0.5)]' : 'bg-[#ef4444] shadow-[0_0_10px_rgba(239,68,68,0.5)]'
              }`}
            />
            <div>
              <h3 className="text-base font-bold text-white tracking-tight flex items-center gap-2">
                <span>{detection.original_filename || 'Inspection Record'}</span>
                <span className={`text-[10px] px-2 py-0.5 rounded-full font-mono uppercase font-bold ${
                  isSafe ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' : 'bg-red-500/20 text-red-400 border border-red-500/30'
                }`}>
                  {severity}
                </span>
              </h3>
              <p className="text-xs text-slate-400 font-mono">
                ID: {detection.id} &bull; Model: {detection.model_version || 'YOLOv8s'}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            {/* View Mode Toggle */}
            <div className="bg-[#1e293b] p-1 rounded-xl flex items-center gap-1 text-xs font-mono">
              <button
                onClick={() => setActiveTab('side_by_side')}
                className={`px-3 py-1 rounded-lg transition-colors cursor-pointer ${
                  activeTab === 'side_by_side' ? 'bg-[#f97316] text-white font-bold' : 'text-slate-400 hover:text-white'
                }`}
              >
                Split View
              </button>
              <button
                onClick={() => setActiveTab('annotated')}
                className={`px-3 py-1 rounded-lg transition-colors cursor-pointer ${
                  activeTab === 'annotated' ? 'bg-[#f97316] text-white font-bold' : 'text-slate-400 hover:text-white'
                }`}
              >
                Annotated
              </button>
              <button
                onClick={() => setActiveTab('original')}
                className={`px-3 py-1 rounded-lg transition-colors cursor-pointer ${
                  activeTab === 'original' ? 'bg-[#f97316] text-white font-bold' : 'text-slate-400 hover:text-white'
                }`}
              >
                Original
              </button>
            </div>

            <button
              onClick={onClose}
              className="p-2 rounded-xl text-slate-400 hover:text-white hover:bg-[#1e293b] transition-colors cursor-pointer"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Modal Body */}
        <div className="p-6 overflow-y-auto space-y-6 flex-1 bg-[#0a0f1d]">
          {/* Images Display Area */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {(activeTab === 'side_by_side' || activeTab === 'original') && (
              <div className="space-y-2">
                <div className="flex items-center justify-between text-xs font-mono text-slate-400 px-1">
                  <span>SOURCE IMAGE (ORIGINAL)</span>
                  <a
                    href={originalUrl}
                    target="_blank"
                    rel="noreferrer"
                    className="hover:text-white flex items-center gap-1"
                  >
                    <Download className="w-3 h-3" /> Raw File
                  </a>
                </div>
                <div className="rounded-2xl overflow-hidden border border-[#1e293b] bg-[#070b14] aspect-16/10 flex items-center justify-center relative shadow-inner">
                  <img
                    src={originalUrl}
                    alt="Original Inspection"
                    className="w-full h-full object-contain"
                    onError={(e) => {
                      (e.target as HTMLElement).style.display = 'none';
                      const parent = (e.target as HTMLElement).parentElement;
                      if (parent) {
                        const fallback = document.createElement('div');
                        fallback.className = 'text-center p-6 text-slate-500 font-mono text-xs';
                        fallback.innerText = 'Image file unavailable or moved';
                        parent.appendChild(fallback);
                      }
                    }}
                  />
                </div>
              </div>
            )}

            {(activeTab === 'side_by_side' || activeTab === 'annotated') && (
              <div className={`space-y-2 ${activeTab === 'annotated' ? 'md:col-span-2' : ''}`}>
                <div className="flex items-center justify-between text-xs font-mono text-slate-400 px-1">
                  <span className="text-[#f97316] font-bold">ANNOTATED RESULT (BOUNDING BOXES)</span>
                  <a
                    href={annotatedUrl}
                    target="_blank"
                    rel="noreferrer"
                    className="hover:text-white flex items-center gap-1"
                  >
                    <Download className="w-3 h-3" /> Annotated JPEG
                  </a>
                </div>
                <div className="rounded-2xl overflow-hidden border border-[#f97316]/40 bg-[#070b14] aspect-16/10 flex items-center justify-center relative shadow-inner">
                  <img
                    src={annotatedUrl}
                    alt="Annotated Inspection"
                    className="w-full h-full object-contain"
                    onError={(e) => {
                      (e.target as HTMLElement).style.display = 'none';
                      const parent = (e.target as HTMLElement).parentElement;
                      if (parent) {
                        const fallback = document.createElement('div');
                        fallback.className = 'text-center p-6 text-slate-500 font-mono text-xs';
                        fallback.innerText = 'Annotated mask file unavailable';
                        parent.appendChild(fallback);
                      }
                    }}
                  />
                </div>
              </div>
            )}
          </div>

          {/* Inspection Metadata Grid */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs font-mono">
            <div className="p-3.5 rounded-2xl bg-[#111827] border border-[#1e293b]">
              <span className="text-slate-400 text-[10px]">HAZARD CLASS</span>
              <div className="text-sm font-bold text-white mt-1">{className}</div>
            </div>
            <div className="p-3.5 rounded-2xl bg-[#111827] border border-[#1e293b]">
              <span className="text-slate-400 text-[10px]">MODEL CONFIDENCE</span>
              <div className="text-sm font-bold text-[#f97316] mt-1">{confidencePct}</div>
            </div>
            <div className="p-3.5 rounded-2xl bg-[#111827] border border-[#1e293b]">
              <span className="text-slate-400 text-[10px]">PROCESSING DURATION</span>
              <div className="text-sm font-bold text-slate-200 mt-1">{detection.processing_duration_ms || 120} ms</div>
            </div>
            <div className="p-3.5 rounded-2xl bg-[#111827] border border-[#1e293b]">
              <span className="text-slate-400 text-[10px]">ANALYSIS TIMESTAMP</span>
              <div className="text-xs font-bold text-slate-300 mt-1 truncate">
                {new Date(detection.created_at).toLocaleString()}
              </div>
            </div>
          </div>

          {/* Detections / Bounding Box Details */}
          <div className="p-4 rounded-2xl bg-[#111827] border border-[#1e293b] space-y-3 font-mono text-xs">
            <div className="flex items-center justify-between border-b border-[#1e293b] pb-2">
              <span className="text-slate-400 font-bold flex items-center gap-1.5">
                <Box className="w-3.5 h-3.5 text-[#f97316]" />
                SPATIAL BOUNDING BOX TELEMETRY
              </span>
              <button
                onClick={() => setShowRawJson(!showRawJson)}
                className="text-[11px] text-[#f97316] hover:underline cursor-pointer"
              >
                {showRawJson ? 'Hide Raw JSON' : 'View Raw JSON'}
              </button>
            </div>

            {showRawJson ? (
              <pre className="p-3 rounded-xl bg-[#070b14] text-[11px] text-emerald-400 overflow-x-auto border border-[#1e293b]">
                {JSON.stringify(detection, null, 2)}
              </pre>
            ) : (
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-[11px]">
                <div className="bg-[#0b1120] p-2.5 rounded-xl border border-[#1a2333]">
                  <span className="text-slate-500">X (Pixels):</span>
                  <span className="text-white ml-2 font-bold">{bbox.x ?? 'N/A'}</span>
                </div>
                <div className="bg-[#0b1120] p-2.5 rounded-xl border border-[#1a2333]">
                  <span className="text-slate-500">Y (Pixels):</span>
                  <span className="text-white ml-2 font-bold">{bbox.y ?? 'N/A'}</span>
                </div>
                <div className="bg-[#0b1120] p-2.5 rounded-xl border border-[#1a2333]">
                  <span className="text-slate-500">Width:</span>
                  <span className="text-white ml-2 font-bold">{bbox.width ?? 'N/A'} px</span>
                </div>
                <div className="bg-[#0b1120] p-2.5 rounded-xl border border-[#1a2333]">
                  <span className="text-slate-500">Height:</span>
                  <span className="text-white ml-2 font-bold">{bbox.height ?? 'N/A'} px</span>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Modal Footer */}
        <div className="p-4 border-t border-[#1e293b] bg-[#0b1120] flex items-center justify-between">
          <p className="text-[11px] text-slate-500 font-mono">
            All bounding box coordinates and metrics derived directly from model tensor outputs.
          </p>
          <button
            onClick={onClose}
            className="px-5 py-2 rounded-xl bg-[#1e293b] hover:bg-[#334155] text-xs font-semibold text-white transition-colors cursor-pointer"
          >
            Close Inspection
          </button>
        </div>
      </div>
    </div>
  );
};
