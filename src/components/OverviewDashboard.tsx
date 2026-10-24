import React, { useState, useEffect, useRef } from 'react';
import {
  ShieldAlert,
  ShieldCheck,
  AlertTriangle,
  Upload,
  Play,
  ArrowRight,
  Droplets,
  Flame,
  Zap,
  Box,
  CheckCircle,
  Database,
  Layers,
  Activity,
  Cpu,
  BarChart2,
  Clock,
  Eye,
  Maximize2
} from 'lucide-react';
import { NavSection, DetectionItem } from '../types';

interface OverviewDashboardProps {
  onNavigate: (section: NavSection) => void;
  onSelectDetection: (item: any) => void;
  activeModel?: any;
  allModels?: any[];
  onSelectModel?: (modelId: string) => void;
}

export const OverviewDashboard: React.FC<OverviewDashboardProps> = ({
  onNavigate,
  onSelectDetection,
  activeModel,
  allModels = [],
  onSelectModel
}) => {
  const [realStats, setRealStats] = useState<any | null>(null);
  const [isLoadingStats, setIsLoadingStats] = useState<boolean>(true);
  const [selectedSample, setSelectedSample] = useState<string>('water');
  const [isAnalyzing, setIsAnalyzing] = useState<boolean>(false);
  const [currentDetection, setCurrentDetection] = useState<DetectionItem | null>(null);
  const [customFile, setCustomFile] = useState<File | null>(null);
  const [confThreshold, setConfThreshold] = useState<number>(0.25);
  const [modelChoice, setModelChoice] = useState<string>('floorguard-yolov8s-v1.1.0-phase4.2');
  const fileInputRef = useRef<HTMLInputElement>(null);

  const samplePresets: Record<string, { label: string; path: string; icon: any; color: string }> = {
    water: {
      label: 'Water Spill',
      path: '/data/images/sample_water_spill.jpg',
      icon: Droplets,
      color: 'text-amber-400'
    },
    oil: {
      label: 'Oil Spill',
      path: '/data/images/thumb_oil_spill.jpg',
      icon: Flame,
      color: 'text-rose-500'
    },
    glass: {
      label: 'Broken Glass',
      path: '/data/images/thumb_broken_glass.jpg',
      icon: Zap,
      color: 'text-purple-400'
    },
    obstacle: {
      label: 'Obstacle',
      path: '/data/images/thumb_obstacle.jpg',
      icon: Box,
      color: 'text-cyan-400'
    },
    clean: {
      label: 'Clean Floor',
      path: '/data/images/thumb_clean_floor.jpg',
      icon: CheckCircle,
      color: 'text-emerald-400'
    }
  };

  const fetchRealAnalytics = async () => {
    try {
      setIsLoadingStats(true);
      const res = await fetch('/api/analytics/real');
      if (res.ok) {
        const data = await res.json();
        setRealStats(data);
      }
    } catch (err) {
      console.error('Failed to load real analytics:', err);
    } finally {
      setIsLoadingStats(false);
    }
  };

  const runQuickInspection = async (imagePath?: string, fileToUpload?: File) => {
    setIsAnalyzing(true);
    try {
      const formData = new FormData();
      if (fileToUpload) {
        formData.append('image', fileToUpload);
      } else {
        const targetPath = imagePath || samplePresets[selectedSample]?.path || '/data/images/sample_water_spill.jpg';
        formData.append('imagePath', targetPath);
      }
      formData.append('model_id', modelChoice);
      formData.append('confidence', confThreshold.toString());

      const res = await fetch('/api/detect/image', {
        method: 'POST',
        body: formData
      });

      const data = await res.json();
      if (res.ok && data.status === 'ok') {
        setCurrentDetection(data.detection);
        // Refresh real stats as a new run was recorded
        fetchRealAnalytics();
      }
    } catch (err) {
      console.error('Quick inspection error:', err);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleSampleClick = (key: string) => {
    setSelectedSample(key);
    setCustomFile(null);
    runQuickInspection(samplePresets[key].path);
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setCustomFile(file);
      setSelectedSample('');
      runQuickInspection(undefined, file);
    }
  };

  useEffect(() => {
    fetchRealAnalytics();
    runQuickInspection('/data/images/sample_water_spill.jpg');
  }, []);

  const kpis = realStats?.operational_kpis || {
    total_analyses: 0,
    images_analyzed: 0,
    videos_analyzed: 0,
    hazards_detected: 0,
    clean_floors_confirmed: 0,
    safe_pass_rate_pct: 100
  };

  return (
    <div className="p-6 space-y-6 max-w-[1720px] mx-auto text-slate-100">
      {/* Top Banner: Status & Orchestration Hub */}
      <div className="bg-[#111827] border border-slate-800 rounded-2xl p-6 shadow-xl relative overflow-hidden">
        <div className="absolute top-0 right-0 w-96 h-96 bg-orange-500/5 rounded-full blur-3xl pointer-events-none" />
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 relative z-10">
          <div className="space-y-1">
            <div className="flex items-center gap-3">
              <div className="p-2.5 rounded-xl bg-orange-500/10 border border-orange-500/30 text-orange-400">
                <ShieldAlert className="w-5 h-5" />
              </div>
              <div>
                <h1 className="text-xl font-bold tracking-tight text-white flex items-center gap-2">
                  <span>Floor Guard AI &middot; Executive Safety Command</span>
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                    Live Telemetry
                  </span>
                </h1>
                <p className="text-xs text-slate-400 mt-0.5">
                  Real-time floor hazard detection monitoring, computer vision model governance, and physical audit history.
                </p>
              </div>
            </div>
          </div>

          {/* Quick Action Navigation Buttons */}
          <div className="flex flex-wrap items-center gap-2">
            <button
              onClick={() => onNavigate('image_detection')}
              className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-orange-500 hover:bg-orange-600 text-white font-bold text-xs shadow-lg shadow-orange-500/20 transition-all cursor-pointer"
            >
              <Upload className="w-3.5 h-3.5" />
              <span>Image Inspector</span>
            </button>
            <button
              onClick={() => onNavigate('video_analysis')}
              className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs font-semibold transition-all cursor-pointer"
            >
              <Play className="w-3.5 h-3.5" />
              <span>Video Pipeline</span>
            </button>
            <button
              onClick={() => onNavigate('ai_model_lab')}
              className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-orange-400 border border-slate-700 text-xs font-semibold transition-all cursor-pointer"
            >
              <Cpu className="w-3.5 h-3.5" />
              <span>AI Model Lab</span>
            </button>
          </div>
        </div>
      </div>

      {/* Real Database KPI Metrics Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-[#111827] border border-slate-800 rounded-2xl p-5 space-y-2 relative overflow-hidden group hover:border-slate-700 transition-all">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-bold uppercase tracking-wider">Total Inspections</span>
            <Activity className="w-4 h-4 text-orange-400" />
          </div>
          <div className="text-2xl font-bold font-mono text-white tracking-tight">
            {kpis.total_analyses}
          </div>
          <div className="text-[11px] text-slate-500 font-mono flex items-center justify-between">
            <span>{kpis.images_analyzed} Images</span>
            <span>{kpis.videos_analyzed} Videos</span>
          </div>
        </div>

        <div className="bg-[#111827] border border-slate-800 rounded-2xl p-5 space-y-2 relative overflow-hidden group hover:border-slate-700 transition-all">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-bold uppercase tracking-wider">Hazards Identified</span>
            <AlertTriangle className="w-4 h-4 text-rose-400" />
          </div>
          <div className="text-2xl font-bold font-mono text-rose-400 tracking-tight">
            {kpis.hazards_detected}
          </div>
          <div className="text-[11px] text-slate-500 font-mono">
            Active slip, spill, and trip risks
          </div>
        </div>

        <div className="bg-[#111827] border border-slate-800 rounded-2xl p-5 space-y-2 relative overflow-hidden group hover:border-slate-700 transition-all">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-bold uppercase tracking-wider">Safe Floor Confirmations</span>
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-2xl font-bold font-mono text-emerald-400 tracking-tight">
            {kpis.clean_floors_confirmed}
          </div>
          <div className="text-[11px] text-slate-500 font-mono">
            Verified dry surface clearance
          </div>
        </div>

        <div className="bg-[#111827] border border-slate-800 rounded-2xl p-5 space-y-2 relative overflow-hidden group hover:border-slate-700 transition-all">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-bold uppercase tracking-wider">Safe Pass Rate</span>
            <BarChart2 className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="text-2xl font-bold font-mono text-cyan-400 tracking-tight">
            {kpis.safe_pass_rate_pct}%
          </div>
          <div className="text-[11px] text-slate-500 font-mono">
            Zero-hazard audit pass ratio
          </div>
        </div>
      </div>

      {/* Main Workspace Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Left Column (7 cols): Interactive Live Testbed */}
        <div className="lg:col-span-7 bg-[#111827] border border-slate-800 rounded-2xl p-5 space-y-5">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div>
              <h2 className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-2">
                <Eye className="w-4 h-4 text-orange-400" />
                Live Floor Surface Inspection
              </h2>
              <p className="text-[11px] text-slate-500 mt-0.5">
                Execute instant YOLOv8 inference with pixel bounding box telemetry.
              </p>
            </div>

            {/* Model & Conf Controls */}
            <div className="flex items-center gap-3">
              <select
                value={modelChoice}
                onChange={(e) => {
                  setModelChoice(e.target.value);
                  runQuickInspection(undefined, customFile || undefined);
                }}
                className="bg-slate-800 border border-slate-700 text-xs text-white rounded-lg px-2.5 py-1.5 focus:outline-none focus:border-orange-500"
              >
                <option value="floorguard-yolov8s-v1.1.0-phase4.2">FloorGuard Phase 4.2 (Hazards)</option>
                <option value="yolov8s-coco-pretrained">YOLOv8s COCO (80 Classes)</option>
              </select>
            </div>
          </div>

          {/* Quick Sample Selector Bar */}
          <div className="grid grid-cols-3 sm:grid-cols-6 gap-2">
            {Object.entries(samplePresets).map(([key, item]) => {
              const Icon = item.icon;
              return (
                <button
                  key={key}
                  onClick={() => handleSampleClick(key)}
                  className={`p-2 rounded-xl border text-center transition-all cursor-pointer flex flex-col items-center gap-1 ${
                    selectedSample === key && !customFile
                      ? 'border-orange-500 bg-orange-500/10 text-white shadow-md'
                      : 'border-slate-800 bg-slate-900/60 hover:border-slate-700 text-slate-400 hover:text-slate-200'
                  }`}
                >
                  <Icon className={`w-4 h-4 ${item.color}`} />
                  <span className="text-[10px] font-medium truncate w-full">{item.label}</span>
                </button>
              );
            })}

            {/* Upload Button */}
            <button
              onClick={() => fileInputRef.current?.click()}
              className={`p-2 rounded-xl border border-dashed text-center transition-all cursor-pointer flex flex-col items-center gap-1 ${
                customFile
                  ? 'border-orange-500 bg-orange-500/10 text-white'
                  : 'border-slate-700 bg-slate-900/40 hover:border-slate-600 text-slate-400'
              }`}
            >
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                className="hidden"
                onChange={handleFileUpload}
              />
              <Upload className="w-4 h-4 text-orange-400" />
              <span className="text-[10px] font-medium truncate w-full">
                {customFile ? 'Custom' : 'Upload'}
              </span>
            </button>
          </div>

          {/* Canvas Display */}
          <div className="relative rounded-xl overflow-hidden border border-slate-800 bg-black aspect-16/10 flex items-center justify-center group shadow-inner">
            {currentDetection ? (
              <img
                src={currentDetection.annotated_image_url || currentDetection.image_url}
                alt="Inspection Output"
                className="w-full h-full object-contain"
              />
            ) : (
              <div className="text-xs text-slate-500 font-mono">No inspection loaded</div>
            )}

            {isAnalyzing && (
              <div className="absolute inset-0 bg-black/60 backdrop-blur-xs flex items-center justify-center">
                <div className="flex items-center gap-2 px-4 py-2 rounded-xl bg-slate-900 border border-orange-500 text-orange-400 text-xs font-mono">
                  <Activity className="w-4 h-4 animate-spin" />
                  <span>Evaluating image tensors...</span>
                </div>
              </div>
            )}

            {/* Overlay Status Pill */}
            {currentDetection && (
              <div className="absolute top-3 left-3 bg-black/80 backdrop-blur-md px-3 py-1.5 rounded-lg border border-slate-700 text-white font-mono text-xs flex items-center gap-2">
                <span className={`w-2 h-2 rounded-full ${currentDetection.severity === 'Safe' ? 'bg-emerald-400' : 'bg-rose-500'}`} />
                <span className="font-bold uppercase tracking-wider">{currentDetection.class_name.replace(/_/g, ' ')}</span>
                <span className="text-slate-500">|</span>
                <span className="text-orange-400 font-bold">{currentDetection.confidence_percent || `${Math.round(currentDetection.confidence * 100)}%`}</span>
              </div>
            )}

            {/* Latency & Full Detail Action */}
            {currentDetection && (
              <button
                onClick={() => onSelectDetection(currentDetection)}
                className="absolute bottom-3 right-3 bg-slate-900/90 hover:bg-slate-800 border border-slate-700 px-3 py-1.5 rounded-lg text-slate-200 text-xs font-medium flex items-center gap-1.5 shadow-lg cursor-pointer transition-colors"
              >
                <Maximize2 className="w-3.5 h-3.5 text-orange-400" />
                <span>Full Telemetry</span>
              </button>
            )}
          </div>

          {/* Detections List & Recommendation */}
          {currentDetection && (
            <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-white uppercase tracking-wider">
                  OSHA Safety Assessment &amp; Corrective Action
                </span>
                <span className={`text-[10px] font-mono px-2 py-0.5 rounded font-bold ${
                  currentDetection.severity === 'Safe'
                    ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
                    : 'bg-rose-500/10 text-rose-400 border border-rose-500/30'
                }`}>
                  {currentDetection.severity.toUpperCase()} RISK
                </span>
              </div>
              <p className="text-xs text-slate-300 leading-relaxed">
                {currentDetection.recommendation || (currentDetection.severity === 'Safe'
                  ? 'Normal floor surface clearance confirmed. Walkway is free of liquid pooling and obstructions.'
                  : 'Hazard identified in pedestrian pathway. Immediate custodial containment recommended.')}
              </p>
            </div>
          )}
        </div>

        {/* Right Column (5 cols): Recent Facility Inspections Feed */}
        <div className="lg:col-span-5 bg-[#111827] border border-slate-800 rounded-2xl p-5 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-2">
              <Clock className="w-4 h-4 text-orange-400" />
              Recent Database Inspections
            </h2>
            <button
              onClick={() => onNavigate('hazard_history')}
              className="text-[11px] text-orange-400 hover:text-orange-300 flex items-center gap-1 cursor-pointer font-medium"
            >
              <span>View All History</span>
              <ArrowRight className="w-3 h-3" />
            </button>
          </div>

          {/* Runs Feed */}
          <div className="space-y-2.5 max-h-[530px] overflow-y-auto pr-1">
            {realStats?.recent_analyses && realStats.recent_analyses.length > 0 ? (
              realStats.recent_analyses.map((run: any) => (
                <div
                  key={run.id}
                  onClick={() => onSelectDetection(run)}
                  className="p-3 rounded-xl bg-slate-900/60 hover:bg-slate-900 border border-slate-800 hover:border-slate-700 transition-all cursor-pointer flex items-center gap-3 group"
                >
                  <div className="w-12 h-12 rounded-lg overflow-hidden bg-black shrink-0 border border-slate-800">
                    <img
                      src={run.thumb_url}
                      alt={run.original_filename}
                      className="w-full h-full object-cover group-hover:scale-105 transition-transform"
                    />
                  </div>

                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-semibold text-white truncate max-w-[150px]">
                        {run.original_filename}
                      </span>
                      <span
                        className={`text-[9px] font-mono font-bold px-1.5 py-0.2 rounded ${
                          run.total_detections > 0
                            ? 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                            : 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                        }`}
                      >
                        {run.total_detections > 0 ? `${run.total_detections} Hazards` : 'Clean'}
                      </span>
                    </div>

                    <div className="flex items-center justify-between text-[10px] text-slate-500 font-mono mt-1">
                      <span>{new Date(run.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                      <span className="text-slate-400">{run.model_version}</span>
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <div className="p-8 text-center text-xs text-slate-500 font-mono">
                No inspection records logged in database yet.
              </div>
            )}
          </div>

          {/* Model Status Card */}
          <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-2 pt-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-white flex items-center gap-1.5">
                <Cpu className="w-3.5 h-3.5 text-orange-400" />
                <span>Production Governance</span>
              </span>
              <span className="text-[10px] font-mono text-cyan-400">COCO Baseline</span>
            </div>
            <p className="text-[11px] text-slate-400 leading-relaxed">
              Default system deployment remains anchored to Ultralytics YOLOv8s COCO. Floor Guard Phase 4.2 is designated as an experimental candidate detector under active validation.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
