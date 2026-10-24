import React, { useState, useRef } from 'react';
import {
  Upload,
  Play,
  RotateCcw,
  Download,
  ZoomIn,
  ZoomOut,
  Layers,
  ShieldAlert,
  AlertTriangle,
  Sliders,
  FileJson,
  Droplets,
  Flame,
  Zap,
  Box,
  Maximize2,
  ShieldCheck,
  Info,
  AlertCircle,
  Eye,
  CheckCircle2,
  RefreshCw,
  Sparkles
} from 'lucide-react';
import { DetectionItem, ModelItem } from '../types';

interface ImageDetectionWorkspaceProps {
  activeModel?: ModelItem;
  allModels?: ModelItem[];
  onSelectModel?: (modelId: string) => void;
}

export const ImageDetectionWorkspace: React.FC<ImageDetectionWorkspaceProps> = ({
  activeModel,
  allModels = [],
  onSelectModel
}) => {
  const [selectedModelId, setSelectedModelId] = useState<string>(
    activeModel?.id || 'yolov8s-coco-pretrained'
  );
  const [confidenceThreshold, setConfidenceThreshold] = useState<number>(0.25);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [selectedSamplePath, setSelectedSamplePath] = useState<string | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [result, setResult] = useState<DetectionItem | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [showBoundingBoxes, setShowBoundingBoxes] = useState(true);
  const [viewMode, setViewMode] = useState<'annotated' | 'original' | 'split'>('annotated');
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Verified quick test samples from local dataset
  const testSamples = [
    { id: 'water', label: 'Water Spill', path: 'data/processed/images/sample_water_spill.jpg', icon: Droplets, color: '#06b6d4' },
    { id: 'oil', label: 'Oil Spill', path: 'data/processed/images/thumb_oil_spill.jpg', icon: Flame, color: '#f59e0b' },
    { id: 'glass', label: 'Broken Glass', path: 'data/processed/images/thumb_broken_glass.jpg', icon: Zap, color: '#a855f7' },
    { id: 'obstacle', label: 'Obstacle', path: 'data/processed/images/thumb_obstacle.jpg', icon: Box, color: '#ef4444' },
    { id: 'clean', label: 'Clean Floor', path: 'data/processed/images/thumb_clean_floor.jpg', icon: ShieldCheck, color: '#10b981' }
  ];

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setSelectedFile(file);
      setSelectedSamplePath(null);
      setPreviewUrl(URL.createObjectURL(file));
      setResult(null);
      setErrorMessage(null);
    }
  };

  const handleSelectSample = (sample: typeof testSamples[0]) => {
    setSelectedFile(null);
    setSelectedSamplePath(sample.path);
    setPreviewUrl(`/${sample.path}`);
    setResult(null);
    setErrorMessage(null);
  };

  const runInference = async () => {
    if (!selectedFile && !selectedSamplePath) {
      setErrorMessage('Please upload an image or select a test sample first.');
      return;
    }

    setIsProcessing(true);
    setErrorMessage(null);

    try {
      const formData = new FormData();
      if (selectedFile) {
        formData.append('image', selectedFile);
      } else if (selectedSamplePath) {
        formData.append('imagePath', selectedSamplePath);
      }

      formData.append('model_id', selectedModelId);
      formData.append('confidence', confidenceThreshold.toString());

      const res = await fetch('/api/detect/image', {
        method: 'POST',
        body: formData
      });

      const data = await res.json();
      if (data.status === 'ok') {
        setResult(data.detection);
      } else {
        setErrorMessage(data.message || 'Inference execution failed.');
      }
    } catch (err: any) {
      setErrorMessage(`Failed to connect to backend: ${err.message}`);
    } finally {
      setIsProcessing(false);
    }
  };

  const resetWorkspace = () => {
    setSelectedFile(null);
    setSelectedSamplePath(null);
    setPreviewUrl(null);
    setResult(null);
    setErrorMessage(null);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const isCustomModel = selectedModelId.includes('floorguard');

  return (
    <div className="p-6 space-y-6 max-w-[1720px] mx-auto">
      {/* Top Configuration Bar */}
      <div className="bg-[#111827] border border-[#1e293b] rounded-3xl p-5 flex flex-wrap items-center justify-between gap-4 shadow-sm">
        {/* Model Selection */}
        <div className="flex flex-wrap items-center gap-3">
          <label className="text-xs font-mono text-slate-400 uppercase font-semibold">
            Inference Model:
          </label>
          <div className="bg-[#0a0f1d] p-1 rounded-2xl border border-[#1e293b] flex items-center gap-1 font-mono text-xs">
            <button
              onClick={() => setSelectedModelId('yolov8s-coco-pretrained')}
              className={`px-3 py-1.5 rounded-xl transition-all cursor-pointer font-bold ${
                selectedModelId === 'yolov8s-coco-pretrained'
                  ? 'bg-blue-600 text-white shadow-md'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              Production Baseline (COCO-80)
            </button>
            <button
              onClick={() => setSelectedModelId('floorguard-yolov8s-v1.1.0-phase4.2')}
              className={`px-3 py-1.5 rounded-xl transition-all cursor-pointer font-bold flex items-center gap-1.5 ${
                selectedModelId === 'floorguard-yolov8s-v1.1.0-phase4.2'
                  ? 'bg-[#f97316] text-white shadow-md'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              <Sparkles className="w-3.5 h-3.5 text-white" />
              Experimental Floor Hazards (Phase 4.2)
            </button>
          </div>
        </div>

        {/* Confidence Threshold Slider */}
        <div className="flex items-center gap-3 font-mono text-xs bg-[#0a0f1d] px-4 py-2 rounded-2xl border border-[#1e293b]">
          <span className="text-slate-400">Confidence Threshold:</span>
          <input
            type="range"
            min="0.10"
            max="0.90"
            step="0.05"
            value={confidenceThreshold}
            onChange={(e) => setConfidenceThreshold(parseFloat(e.target.value))}
            className="w-28 accent-[#f97316] cursor-pointer"
          />
          <span className="font-bold text-[#f97316] w-9 text-right">
            {Math.round(confidenceThreshold * 100)}%
          </span>
        </div>

        {/* Action Controls */}
        <div className="flex items-center gap-2">
          <button
            onClick={resetWorkspace}
            className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-[#1e293b] hover:bg-[#334155] text-slate-300 text-xs font-semibold transition-colors cursor-pointer"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>Reset</span>
          </button>
          <button
            onClick={runInference}
            disabled={isProcessing || (!selectedFile && !selectedSamplePath)}
            className={`flex items-center gap-2 px-5 py-2 rounded-xl text-xs font-bold transition-all shadow-lg cursor-pointer ${
              isProcessing || (!selectedFile && !selectedSamplePath)
                ? 'bg-slate-800 text-slate-500 cursor-not-allowed'
                : 'bg-[#ea580c] hover:bg-[#f97316] text-white shadow-orange-950/40'
            }`}
          >
            <Play className={`w-3.5 h-3.5 ${isProcessing ? 'animate-spin' : ''}`} />
            <span>{isProcessing ? 'Executing Inference...' : 'Run Hazard Detection'}</span>
          </button>
        </div>
      </div>

      {/* Model Capabilities Notice */}
      <div className={`p-4 rounded-2xl border flex items-start gap-3 font-mono text-xs ${
        isCustomModel
          ? 'bg-orange-950/20 border-orange-500/30 text-orange-200'
          : 'bg-blue-950/20 border-blue-500/30 text-blue-200'
      }`}>
        <Info className="w-4 h-4 shrink-0 mt-0.5" />
        <div className="space-y-1">
          <div className="font-bold">
            {isCustomModel ? 'EXPERIMENTAL HAZARD DETECTOR ACTIVE' : 'PRODUCTION BASELINE DETECTOR ACTIVE'}
          </div>
          <p className="text-[11px] opacity-90 leading-relaxed font-sans">
            {isCustomModel
              ? 'Trained specifically for floor safety hazards: Water Spill, Oil Spill, Broken Glass, and Walkway Obstacles. Verified with zero test contamination.'
              : 'Pretrained on 80 common MS-COCO object categories (boxes, bags, chairs, bottles). Note: Liquid puddles and glass fragments are outside COCO vocabulary.'}
          </p>
        </div>
      </div>

      {/* Workspace Main Area */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Image Canvas & Preview (8 cols) */}
        <div className="lg:col-span-8 space-y-4">
          <div className="bg-[#111827] border border-[#1e293b] rounded-3xl p-5 space-y-4">
            {/* Canvas Header / Controls */}
            <div className="flex flex-wrap items-center justify-between gap-3 border-b border-[#1e293b] pb-3">
              <span className="text-xs font-mono font-bold text-slate-300 flex items-center gap-1.5">
                <Layers className="w-4 h-4 text-[#f97316]" />
                INSPECTION VIEWPORT
              </span>

              {result && (
                <div className="flex items-center gap-2 text-xs font-mono">
                  <div className="bg-[#0a0f1d] p-1 rounded-xl border border-[#1e293b] flex items-center gap-1">
                    <button
                      onClick={() => setViewMode('annotated')}
                      className={`px-2.5 py-1 rounded-lg transition-colors cursor-pointer ${
                        viewMode === 'annotated' ? 'bg-[#f97316] text-white font-bold' : 'text-slate-400 hover:text-white'
                      }`}
                    >
                      Annotated
                    </button>
                    <button
                      onClick={() => setViewMode('original')}
                      className={`px-2.5 py-1 rounded-lg transition-colors cursor-pointer ${
                        viewMode === 'original' ? 'bg-[#f97316] text-white font-bold' : 'text-slate-400 hover:text-white'
                      }`}
                    >
                      Original
                    </button>
                    <button
                      onClick={() => setViewMode('split')}
                      className={`px-2.5 py-1 rounded-lg transition-colors cursor-pointer ${
                        viewMode === 'split' ? 'bg-[#f97316] text-white font-bold' : 'text-slate-400 hover:text-white'
                      }`}
                    >
                      Side by Side
                    </button>
                  </div>
                </div>
              )}
            </div>

            {/* Canvas Container */}
            <div className="relative rounded-2xl overflow-hidden bg-[#070b14] border border-[#1e293b] min-h-[460px] flex items-center justify-center">
              {previewUrl ? (
                viewMode === 'split' && result ? (
                  <div className="w-full h-full grid grid-cols-2 gap-2 p-2 min-h-[460px]">
                    <div className="relative border border-[#1e293b] rounded-xl overflow-hidden flex items-center justify-center bg-black">
                      <img src={previewUrl} alt="Original Input" className="max-h-[440px] object-contain" />
                      <span className="absolute bottom-2 left-2 px-2 py-0.5 rounded bg-black/70 text-[10px] font-mono text-white">
                        ORIGINAL
                      </span>
                    </div>
                    <div className="relative border border-[#f97316]/50 rounded-xl overflow-hidden flex items-center justify-center bg-black">
                      <img
                        src={result.annotated_image_url || previewUrl}
                        alt="Annotated Inference"
                        className="max-h-[440px] object-contain"
                      />
                      <span className="absolute bottom-2 left-2 px-2 py-0.5 rounded bg-black/70 text-[10px] font-mono text-[#f97316]">
                        ANNOTATED MASK
                      </span>
                    </div>
                  </div>
                ) : (
                  <div className="relative w-full h-full flex items-center justify-center p-2">
                    <img
                      src={
                        result && viewMode === 'annotated'
                          ? result.annotated_image_url || previewUrl
                          : previewUrl
                      }
                      alt="Floor Inspection Preview"
                      className="max-h-[500px] w-auto object-contain rounded-xl"
                    />
                  </div>
                )
              ) : (
                /* Empty Upload Dropzone */
                <div
                  onClick={() => fileInputRef.current?.click()}
                  className="w-full h-full p-12 flex flex-col items-center justify-center gap-4 text-center cursor-pointer hover:bg-[#0d1424] transition-colors"
                >
                  <div className="w-16 h-16 rounded-3xl bg-[#131d2e] border border-[#1f2c42] flex items-center justify-center text-[#f97316] shadow-lg shadow-black/40">
                    <Upload className="w-8 h-8" />
                  </div>
                  <div className="space-y-1">
                    <h3 className="text-sm font-bold text-white">Upload Floor Inspection Image</h3>
                    <p className="text-xs text-slate-400">
                      Drag and drop image here or click to browse (JPG, PNG, WebP)
                    </p>
                  </div>
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept="image/*"
                    onChange={handleFileChange}
                    className="hidden"
                  />
                </div>
              )}
            </div>

            {/* Quick Test Samples Picker */}
            <div className="space-y-2 pt-2">
              <span className="text-xs font-mono text-slate-400 uppercase">
                Quick Test Samples from Dataset:
              </span>
              <div className="grid grid-cols-2 sm:grid-cols-5 gap-2">
                {testSamples.map((sample) => {
                  const Icon = sample.icon;
                  const isSelected = selectedSamplePath === sample.path;
                  return (
                    <button
                      key={sample.id}
                      onClick={() => handleSelectSample(sample)}
                      className={`p-2.5 rounded-xl border text-xs font-mono flex items-center gap-2 transition-all cursor-pointer ${
                        isSelected
                          ? 'bg-[#1e130a] border-[#f97316] text-white font-bold shadow-md'
                          : 'bg-[#0a0f1d] border-[#1e293b] text-slate-300 hover:bg-[#161f30]'
                      }`}
                    >
                      <Icon className="w-3.5 h-3.5" style={{ color: sample.color }} />
                      <span className="truncate">{sample.label}</span>
                    </button>
                  );
                })}
              </div>
            </div>
          </div>
        </div>

        {/* Right Column: Inference Results & Telemetry (4 cols) */}
        <div className="lg:col-span-4 space-y-4">
          <div className="bg-[#111827] border border-[#1e293b] rounded-3xl p-5 space-y-4 font-mono text-xs">
            <div className="flex items-center justify-between border-b border-[#1e293b] pb-3">
              <span className="font-bold text-slate-300 flex items-center gap-1.5">
                <ShieldAlert className="w-4 h-4 text-[#f97316]" />
                DETECTION TELEMETRY
              </span>
              {result && (
                <span className="text-[10px] text-emerald-400 flex items-center gap-1">
                  <CheckCircle2 className="w-3 h-3" /> SAVED TO DB
                </span>
              )}
            </div>

            {errorMessage && (
              <div className="p-3 rounded-xl bg-red-950/30 border border-red-500/40 text-red-300 text-xs flex items-start gap-2">
                <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
                <span>{errorMessage}</span>
              </div>
            )}

            {result ? (
              <div className="space-y-4">
                {/* Primary Alert Banner */}
                <div className={`p-4 rounded-2xl border ${
                  result.total_detections && result.total_detections > 0
                    ? 'bg-red-950/20 border-red-500/40 text-red-200'
                    : 'bg-emerald-950/20 border-emerald-500/40 text-emerald-200'
                }`}>
                  <div className="text-[10px] uppercase font-bold text-slate-400">Primary Classification</div>
                  <div className="text-base font-bold mt-0.5 flex items-center justify-between">
                    <span>{result.class_name}</span>
                    <span className="text-sm font-mono text-[#f97316]">{result.confidence_percent}</span>
                  </div>
                  <div className="text-[11px] text-slate-400 mt-2 font-sans">
                    {result.summary}
                  </div>
                </div>

                {/* Key Metrics */}
                <div className="grid grid-cols-2 gap-2 text-[11px]">
                  <div className="p-3 rounded-xl bg-[#0a0f1d] border border-[#1e293b]">
                    <span className="text-slate-500">Latency:</span>
                    <div className="font-bold text-white mt-0.5">{result.inference_duration_ms} ms</div>
                  </div>
                  <div className="p-3 rounded-xl bg-[#0a0f1d] border border-[#1e293b]">
                    <span className="text-slate-500">Objects Count:</span>
                    <div className="font-bold text-white mt-0.5">{result.total_detections} instance(s)</div>
                  </div>
                </div>

                {/* Detected Hazards List */}
                {result.detections && result.detections.length > 0 && (
                  <div className="space-y-2">
                    <span className="text-[11px] text-slate-400 uppercase font-bold">Detected Instances:</span>
                    <div className="space-y-1.5 max-h-48 overflow-y-auto pr-1">
                      {result.detections.map((det, idx) => (
                        <div
                          key={idx}
                          className="p-2.5 rounded-xl bg-[#0a0f1d] border border-[#1e293b] flex items-center justify-between text-xs"
                        >
                          <div>
                            <span className="font-bold text-white">{det.class_name}</span>
                            <div className="text-[10px] text-slate-500 font-mono">
                              Box: {det.bounding_box.width}x{det.bounding_box.height} px
                            </div>
                          </div>
                          <span className="px-2 py-0.5 rounded-md font-bold text-xs bg-[#1e130a] text-[#f97316] border border-[#f97316]/30">
                            {det.confidence_percent}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Academic Disclosure */}
                {result.academic_notice && (
                  <div className="p-3 rounded-xl bg-[#0a0f1d] border border-[#1e293b] text-[10px] text-slate-400 font-sans leading-relaxed">
                    <span className="font-bold font-mono text-slate-300 block mb-0.5">Model Verification Notice:</span>
                    {result.academic_notice}
                  </div>
                )}
              </div>
            ) : (
              <div className="py-16 text-center text-slate-500 space-y-2 font-sans">
                <Box className="w-8 h-8 mx-auto text-slate-600" />
                <p className="text-xs">No analysis executed yet.</p>
                <p className="text-[11px] text-slate-600">Select an image and click "Run Hazard Detection".</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
