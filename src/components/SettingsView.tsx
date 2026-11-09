import React, { useState } from 'react';
import {
  Settings,
  Sliders,
  Shield,
  Database,
  Trash2,
  RefreshCw,
  CheckCircle2,
  AlertTriangle
} from 'lucide-react';

interface SettingsViewProps {
  activeModel?: any;
  allModels?: any[];
  onSelectModel?: (modelId: string) => void;
}

export const SettingsView: React.FC<SettingsViewProps> = ({
  activeModel,
  allModels = [],
  onSelectModel
}) => {
  const [confThreshold, setConfThreshold] = useState(50);
  const [highRiskThreshold, setHighRiskThreshold] = useState(80);
  const [maxUpload, setMaxUpload] = useState(50);
  const [enablePolygon, setEnablePolygon] = useState(true);
  const [retentionDays, setRetentionDays] = useState(90);
  const [savedNotice, setSavedNotice] = useState(false);

  const handleSave = async () => {
    try {
      await fetch('/api/settings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          key: 'confidence_threshold',
          value: { value: confThreshold / 100 }
        })
      });
      setSavedNotice(true);
      setTimeout(() => setSavedNotice(false), 2000);
    } catch (err) {
      console.error(err);
    }
  };

  const handleResetDatabase = async () => {
    if (!confirm('Reset local SQLite database to pristine reference state?')) return;
    try {
      await fetch('/api/settings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ key: 'reset_trigger', value: { reset: true } })
      });
      window.location.reload();
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="p-6 space-y-6 max-w-[1200px] mx-auto">
      {/* Model Selection Card */}
      <div className="bg-[#131b29] border border-[#1e2c3f] rounded-2xl p-6 space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-[#1b2738]">
          <div>
            <h2 className="text-base font-bold text-white tracking-tight">Active Inference Engine</h2>
            <p className="text-xs text-slate-400 mt-0.5">Toggle between multi-hazard object detection and binary classification.</p>
          </div>
          <span className="text-xs font-mono text-[#22c55e] bg-[#14291f] border border-[#22c55e]/30 px-2.5 py-1 rounded-lg">
            Active: {activeModel?.name || 'FloorGuard-YOLOv8s'}
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-1">
          {allModels.map((m) => {
            const isSelected = m.id === activeModel?.id;
            const isClassifier = m.task === 'classification';
            return (
              <div
                key={m.id}
                className={`p-4 rounded-xl border transition-all ${
                  isSelected
                    ? isClassifier
                      ? 'bg-[#14233a] border-[#38bdf8] shadow-md'
                      : 'bg-[#152a22] border-[#22c55e] shadow-md'
                    : 'bg-[#0f1724] border-[#1d2b40] hover:border-slate-500'
                }`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span
                      className={`w-2.5 h-2.5 rounded-full ${
                        isClassifier ? 'bg-[#38bdf8] shadow-[0_0_8px_#38bdf8]' : 'bg-[#22c55e] shadow-[0_0_8px_#22c55e]'
                      }`}
                    />
                    <h3 className="text-sm font-bold text-white">{m.name}</h3>
                  </div>
                  <span
                    className={`text-[9px] font-mono uppercase px-2 py-0.5 rounded ${
                      isClassifier ? 'bg-[#0284c7]/30 text-[#38bdf8]' : 'bg-[#16a34a]/30 text-[#22c55e]'
                    }`}
                  >
                    {isClassifier ? 'Classification' : 'Object Detection'}
                  </span>
                </div>

                <p className="text-xs text-slate-300 mt-2 leading-relaxed">
                  {m.description}
                </p>

                <div className="grid grid-cols-2 gap-2 mt-3 p-2.5 rounded-lg bg-black/30 text-[11px] font-mono text-slate-300">
                  <div>
                    <span className="text-slate-500 block text-[10px]">Architecture</span>
                    {m.architecture}
                  </div>
                  <div>
                    <span className="text-slate-500 block text-[10px]">Parameters</span>
                    {m.parameters_count || '11.2M'}
                  </div>
                  <div>
                    <span className="text-slate-500 block text-[10px]">Metric</span>
                    {isClassifier ? `Acc: ${(m.metrics.accuracy * 100).toFixed(1)}%` : `mAP50: ${(m.metrics.mAP50 * 100).toFixed(1)}%`}
                  </div>
                  <div>
                    <span className="text-slate-500 block text-[10px]">Latency</span>
                    {m.metrics.latency_batch1_ms} ms / frame
                  </div>
                </div>

                <div className="mt-3.5 flex items-center justify-between pt-2 border-t border-white/10">
                  <span className="text-[11px] text-slate-400">
                    Classes: <strong className="text-white">{m.classes.length}</strong> ({m.classes.slice(0, 2).join(', ')}...)
                  </span>
                  <button
                    onClick={() => onSelectModel && onSelectModel(m.id)}
                    disabled={isSelected}
                    className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all cursor-pointer ${
                      isSelected
                        ? isClassifier
                          ? 'bg-[#38bdf8] text-black cursor-default'
                          : 'bg-[#22c55e] text-black cursor-default'
                        : 'bg-[#1e2c3f] hover:bg-[#2a3c56] text-white border border-[#2d3d52]'
                    }`}
                  >
                    {isSelected ? '✓ Current Active' : 'Activate Engine'}
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      <div className="bg-[#131b29] border border-[#1e2c3f] rounded-2xl p-6 space-y-6">
        <div className="flex items-center justify-between pb-4 border-b border-[#1b2738]">
          <div>
            <h2 className="text-base font-bold text-white tracking-tight">System &amp; Detection Parameters</h2>
            <p className="text-xs text-slate-400 mt-0.5">Configure model inference thresholds, file ingestion limits, and database retention.</p>
          </div>
          {savedNotice && (
            <div className="flex items-center gap-1.5 px-3 py-1 rounded-lg bg-[#14291f] border border-[#22c55e]/40 text-[#22c55e] text-xs font-semibold">
              <CheckCircle2 className="w-3.5 h-3.5" />
              <span>Settings Saved</span>
            </div>
          )}
        </div>

        {/* Sliders */}
        <div className="space-y-6">
          {/* Confidence Slider */}
          <div className="space-y-2">
            <div className="flex items-center justify-between text-xs">
              <label className="font-semibold text-slate-200">Minimum Hazard Confidence Threshold</label>
              <span className="font-mono font-bold text-[#22c55e]">{confThreshold}%</span>
            </div>
            <input
              type="range"
              min="20"
              max="95"
              value={confThreshold}
              onChange={(e) => setConfThreshold(Number(e.target.value))}
              className="w-full accent-[#22c55e] cursor-pointer"
            />
            <p className="text-[11px] text-slate-400">Detections below this cutoff will be treated as low-confidence and flagged for manual review.</p>
          </div>

          {/* High Risk Slider */}
          <div className="space-y-2">
            <div className="flex items-center justify-between text-xs">
              <label className="font-semibold text-slate-200">High Risk Classification Threshold</label>
              <span className="font-mono font-bold text-[#ef4444]">{highRiskThreshold}%</span>
            </div>
            <input
              type="range"
              min="50"
              max="99"
              value={highRiskThreshold}
              onChange={(e) => setHighRiskThreshold(Number(e.target.value))}
              className="w-full accent-[#ef4444] cursor-pointer"
            />
            <p className="text-[11px] text-slate-400">Confidence above this level immediately flags the incident with High/Critical severity alerts.</p>
          </div>

          {/* File Upload Limits */}
          <div className="space-y-2">
            <div className="flex items-center justify-between text-xs">
              <label className="font-semibold text-slate-200">Max Upload Size Limit</label>
              <span className="font-mono font-bold text-white">{maxUpload} MB</span>
            </div>
            <input
              type="range"
              min="10"
              max="100"
              value={maxUpload}
              onChange={(e) => setMaxUpload(Number(e.target.value))}
              className="w-full accent-[#38bdf8] cursor-pointer"
            />
          </div>

          {/* Segmentation Toggle */}
          <div className="flex items-center justify-between pt-2">
            <div>
              <div className="text-xs font-semibold text-slate-200">Render Segmentation Polygons</div>
              <div className="text-[11px] text-slate-400">Overlay polygon contours on detected fluid puddles</div>
            </div>
            <input
              type="checkbox"
              checked={enablePolygon}
              onChange={(e) => setEnablePolygon(e.target.checked)}
              className="w-4 h-4 accent-[#22c55e] cursor-pointer"
            />
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center justify-between pt-4 border-t border-[#1b2738]">
          <button
            onClick={handleResetDatabase}
            className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-[#231519] border border-[#ef4444]/40 text-[#ef4444] hover:bg-[#2b181a] text-xs font-semibold transition-colors cursor-pointer"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>Reset Demo Database</span>
          </button>

          <button
            onClick={handleSave}
            className="px-5 py-2 rounded-xl bg-[#22c55e] hover:bg-[#16a34a] text-black text-xs font-bold shadow-md transition-colors cursor-pointer"
          >
            Save Configuration
          </button>
        </div>
      </div>
    </div>
  );
};
