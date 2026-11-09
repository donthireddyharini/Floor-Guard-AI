import React from 'react';
import { X, AlertTriangle, CheckCircle, Clock, MapPin, Maximize2, Download } from 'lucide-react';

interface DetectionDetailModalProps {
  detection: any;
  onClose: () => void;
}

export const DetectionDetailModal: React.FC<DetectionDetailModalProps> = ({ detection, onClose }) => {
  if (!detection) return null;

  return (
    <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-[#131b29] border border-[#1e2c3f] rounded-2xl w-full max-w-2xl overflow-hidden shadow-2xl space-y-4">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-[#1b2738]">
          <div className="flex items-center gap-2">
            <span
              className={`w-3 h-3 rounded-full ${
                detection.severity === 'Safe' ? 'bg-[#22c55e]' : 'bg-[#ef4444]'
              }`}
            />
            <h3 className="text-sm font-bold text-white tracking-tight">
              {detection.cls || detection.class_name || 'Hazard Inspection'}
            </h3>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-[#1a2536] transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Content */}
        <div className="p-4 space-y-4">
          <div className="relative rounded-xl overflow-hidden border border-[#202d42] bg-[#090e17] aspect-16/10 flex items-center justify-center">
            <img
              src={detection.thumb || detection.evidence_path || '/assets/samples/water_spill_main.jpg'}
              alt={detection.cls || detection.class_name}
              className="w-full h-full object-cover"
            />
          </div>

          <div className="grid grid-cols-2 gap-3 text-xs font-mono">
            <div className="p-3 rounded-lg bg-[#0d131f] border border-[#182335]">
              <span className="text-slate-400">Recorded Confidence</span>
              <div className="text-base font-bold text-white mt-0.5">
                {detection.conf || `${Math.round((detection.confidence || 0.9) * 100)}%`}
              </div>
            </div>
            <div className="p-3 rounded-lg bg-[#0d131f] border border-[#182335]">
              <span className="text-slate-400">Risk Assessment</span>
              <div
                className={`text-base font-bold mt-0.5 ${
                  detection.severity === 'Safe' ? 'text-[#22c55e]' : 'text-[#ef4444]'
                }`}
              >
                {detection.severity || 'High'}
              </div>
            </div>
          </div>

          <div className="p-3 rounded-lg bg-[#0d131f] border border-[#182335] text-xs font-mono space-y-1.5">
            <div className="flex justify-between">
              <span className="text-slate-400">Timestamp:</span>
              <span className="text-white">{detection.time || detection.created_at || 'May 26, 2026, 10:24 AM'}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Model Detector:</span>
              <span className="text-white">FloorGuard-YOLOv8s (v1.0.0)</span>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-[#1b2738] flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded-lg bg-[#192437] hover:bg-[#202e46] text-xs font-semibold text-slate-200"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
