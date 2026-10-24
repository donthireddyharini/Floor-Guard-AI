import React, { useState, useEffect } from 'react';
import {
  Settings,
  Sliders,
  Shield,
  Database,
  Trash2,
  RefreshCw,
  CheckCircle2,
  AlertTriangle,
  Cpu,
  Layers,
  Save,
  HardDrive
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
  const [confThreshold, setConfThreshold] = useState(25);
  const [highRiskThreshold, setHighRiskThreshold] = useState(70);
  const [videoInterval, setVideoInterval] = useState(1.0);
  const [savedNotice, setSavedNotice] = useState(false);
  const [activeModelId, setActiveModelId] = useState<string>(activeModel?.id || 'yolov8s-coco-pretrained');

  useEffect(() => {
    if (activeModel?.id) {
      setActiveModelId(activeModel.id);
    }
  }, [activeModel]);

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

      await fetch('/api/settings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          key: 'video_interval',
          value: { interval: videoInterval }
        })
      });

      setSavedNotice(true);
      setTimeout(() => setSavedNotice(false), 2500);
    } catch (err) {
      console.error('Failed to save settings:', err);
    }
  };

  const handleSwitchModel = async (modelId: string) => {
    try {
      const resp = await fetch('/api/model/select', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ model_id: modelId })
      });
      const data = await resp.json();
      if (resp.ok && data.status === 'ok') {
        setActiveModelId(modelId);
        if (onSelectModel) {
          onSelectModel(modelId);
        }
      }
    } catch (err) {
      console.error('Failed to switch model:', err);
    }
  };

  return (
    <div className="p-6 space-y-6 max-w-[1280px] mx-auto text-slate-100">
      {/* Header */}
      <div className="bg-[#111827] border border-slate-800 rounded-2xl p-6 shadow-xl relative overflow-hidden">
        <div className="absolute top-0 right-0 w-96 h-96 bg-orange-500/5 rounded-full blur-3xl pointer-events-none" />
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 relative z-10">
          <div className="space-y-1">
            <div className="flex items-center gap-3">
              <div className="p-2.5 rounded-xl bg-orange-500/10 border border-orange-500/30 text-orange-400">
                <Settings className="w-5 h-5" />
              </div>
              <h1 className="text-xl font-bold tracking-tight text-white">System Settings & Governance</h1>
            </div>
            <p className="text-xs text-slate-400 max-w-2xl leading-relaxed">
              Configure system-wide inference thresholds, computer vision model registry targets, and disk storage parameters.
            </p>
          </div>

          <button
            onClick={handleSave}
            className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-orange-500 hover:bg-orange-600 text-white font-bold text-xs shadow-lg shadow-orange-500/20 transition-all cursor-pointer"
          >
            <Save className="w-4 h-4" />
            <span>{savedNotice ? 'Saved Successfully!' : 'Save Configuration'}</span>
          </button>
        </div>
      </div>

      {/* Model Governance Card */}
      <div className="bg-[#111827] border border-slate-800 rounded-2xl p-6 space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-slate-800">
          <div>
            <h2 className="text-sm font-bold text-white tracking-tight flex items-center gap-2">
              <Cpu className="w-4 h-4 text-orange-400" />
              Active Production Inference Engine
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Select the active model used by default across the dashboard and API endpoints.
            </p>
          </div>
          <span className="text-xs font-mono px-3 py-1 rounded-full bg-slate-900 border border-slate-700 text-orange-400">
            Active: {activeModel?.name || activeModelId}
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
          {/* Model Option 1: COCO Baseline */}
          <div
            onClick={() => handleSwitchModel('yolov8s-coco-pretrained')}
            className={`p-4 rounded-xl border transition-all cursor-pointer flex flex-col justify-between ${
              activeModelId === 'yolov8s-coco-pretrained'
                ? 'bg-slate-900/90 border-cyan-500 shadow-md shadow-cyan-500/10'
                : 'bg-slate-900/40 border-slate-800 hover:border-slate-700'
            }`}
          >
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-white flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-cyan-400" />
                  Ultralytics YOLOv8s COCO
                </span>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-cyan-500/10 text-cyan-400 border border-cyan-500/30">
                  Production Default
                </span>
              </div>
              <p className="text-xs text-slate-400 leading-relaxed">
                Pretrained on 80 standard COCO classes. Reliable physical obstacle and pedestrian detection baseline.
              </p>
            </div>
            <div className="pt-3 text-[11px] font-mono text-slate-500 flex justify-between">
              <span>Weights: yolov8s.pt</span>
              <span className="text-cyan-400 font-bold">
                {activeModelId === 'yolov8s-coco-pretrained' ? '● Active' : 'Select'}
              </span>
            </div>
          </div>

          {/* Model Option 2: Phase 4.2 Custom */}
          <div
            onClick={() => handleSwitchModel('floorguard-yolov8s-v1.1.0-phase4.2')}
            className={`p-4 rounded-xl border transition-all cursor-pointer flex flex-col justify-between ${
              activeModelId === 'floorguard-yolov8s-v1.1.0-phase4.2'
                ? 'bg-slate-900/90 border-orange-500 shadow-md shadow-orange-500/10'
                : 'bg-slate-900/40 border-slate-800 hover:border-slate-700'
            }`}
          >
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-white flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-orange-400" />
                  Floor Guard YOLOv8s Phase 4.2
                </span>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-orange-500/10 text-orange-400 border border-orange-500/30">
                  Hazard Specialist
                </span>
              </div>
              <p className="text-xs text-slate-400 leading-relaxed">
                Specialized detector trained on verified water spills, oil pools, broken glass shards, and obstacles.
              </p>
            </div>
            <div className="pt-3 text-[11px] font-mono text-slate-500 flex justify-between">
              <span>Weights: floorguard_yolov8s_phase4_2_best.pt</span>
              <span className="text-orange-400 font-bold">
                {activeModelId === 'floorguard-yolov8s-v1.1.0-phase4.2' ? '● Active' : 'Select'}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Inference Parameters */}
      <div className="bg-[#111827] border border-slate-800 rounded-2xl p-6 space-y-5">
        <h2 className="text-sm font-bold text-white tracking-tight flex items-center gap-2 pb-3 border-b border-slate-800">
          <Sliders className="w-4 h-4 text-orange-400" />
          Inference Engine Defaults
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Confidence Slider */}
          <div className="space-y-2">
            <div className="flex justify-between text-xs">
              <span className="text-slate-300 font-medium">Default Detection Confidence Threshold</span>
              <span className="text-orange-400 font-mono font-bold">{confThreshold}%</span>
            </div>
            <input
              type="range"
              min="10"
              max="90"
              value={confThreshold}
              onChange={(e) => setConfThreshold(parseInt(e.target.value))}
              className="w-full accent-orange-500 bg-slate-800 h-2 rounded-lg appearance-none cursor-pointer"
            />
            <p className="text-[11px] text-slate-500 leading-relaxed">
              Detections with confidence below this cutoff are suppressed by NMS post-processing.
            </p>
          </div>

          {/* Video Interval */}
          <div className="space-y-2">
            <div className="flex justify-between text-xs">
              <span className="text-slate-300 font-medium">Video Offline Keyframe Sampling Interval</span>
              <span className="text-orange-400 font-mono font-bold">{videoInterval.toFixed(1)} seconds</span>
            </div>
            <div className="grid grid-cols-3 gap-2">
              {[0.5, 1.0, 2.0].map((val) => (
                <button
                  key={val}
                  type="button"
                  onClick={() => setVideoInterval(val)}
                  className={`py-2 text-xs rounded-xl font-mono border transition-all cursor-pointer ${
                    videoInterval === val
                      ? 'border-orange-500 bg-orange-500/20 text-orange-300 font-bold'
                      : 'border-slate-800 bg-slate-900/60 text-slate-400 hover:text-white'
                  }`}
                >
                  {val}s interval
                </button>
              ))}
            </div>
            <p className="text-[11px] text-slate-500 leading-relaxed">
              OpenCV extracts one frame every {videoInterval}s during video hazard inspection.
            </p>
          </div>
        </div>
      </div>

      {/* Storage and Audit Retention */}
      <div className="bg-[#111827] border border-slate-800 rounded-2xl p-6 space-y-4">
        <h2 className="text-sm font-bold text-white tracking-tight flex items-center gap-2 pb-3 border-b border-slate-800">
          <HardDrive className="w-4 h-4 text-orange-400" />
          Disk Storage &amp; Database Telemetry
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs font-mono">
          <div className="p-3.5 rounded-xl bg-slate-900 border border-slate-800 space-y-1">
            <div className="text-slate-500">Database Engine:</div>
            <div className="text-white font-bold">SQLite 3 (WAL Mode)</div>
            <div className="text-[10px] text-slate-400">data/database.sqlite</div>
          </div>

          <div className="p-3.5 rounded-xl bg-slate-900 border border-slate-800 space-y-1">
            <div className="text-slate-500">Annotated Artifacts:</div>
            <div className="text-white font-bold">uploads/annotated/</div>
            <div className="text-[10px] text-slate-400">PIL Bounding Box JPEGs</div>
          </div>

          <div className="p-3.5 rounded-xl bg-slate-900 border border-slate-800 space-y-1">
            <div className="text-slate-500">Model Checkpoints:</div>
            <div className="text-white font-bold">models/detection/</div>
            <div className="text-[10px] text-slate-400">PyTorch .pt Checkpoints</div>
          </div>
        </div>
      </div>
    </div>
  );
};
