import React, { useState, useEffect, useRef } from 'react';
import {
  Cpu,
  Layers,
  ArrowRight,
  ShieldCheck,
  AlertTriangle,
  Info,
  CheckCircle2,
  Sliders,
  Image as ImageIcon,
  Upload,
  RefreshCw,
  Zap,
  Scale,
  Sparkles,
  ExternalLink
} from 'lucide-react';
import { ModelItem } from '../types';

interface AiModelLabViewProps {
  models?: ModelItem[];
  activeModelId?: string;
  onModelSelect?: (modelId: string) => void;
}

export const AiModelLabView: React.FC<AiModelLabViewProps> = ({
  models = [],
  activeModelId = 'yolov8s-coco-pretrained',
  onModelSelect
}) => {
  const [activeTab, setActiveTab] = useState<'comparison' | 'pipeline' | 'registry'>('comparison');
  const [compareImage, setCompareImage] = useState<string>('/data/images/sample_water_spill.jpg');
  const [customFile, setCustomFile] = useState<File | null>(null);
  const [customFilePreview, setCustomFilePreview] = useState<string | null>(null);
  const [confThreshold, setConfThreshold] = useState<number>(0.25);
  const [isComparing, setIsComparing] = useState<boolean>(false);
  const [compareResult, setCompareResult] = useState<any | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const sampleImages = [
    { name: 'Water Spill Sample', path: '/data/images/sample_water_spill.jpg', type: 'water' },
    { name: 'Oil Spill Sample', path: '/data/images/thumb_oil_spill.jpg', type: 'oil' },
    { name: 'Broken Glass Sample', path: '/data/images/thumb_broken_glass.jpg', type: 'glass' },
    { name: 'Walkway Obstacle', path: '/data/images/thumb_obstacle.jpg', type: 'obstacle' },
    { name: 'Clean Floor Surface', path: '/data/images/thumb_clean_floor.jpg', type: 'clean' }
  ];

  const handleSelectSample = (path: string) => {
    setCompareImage(path);
    setCustomFile(null);
    setCustomFilePreview(null);
    setErrorMessage(null);
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setCustomFile(file);
      setCustomFilePreview(URL.createObjectURL(file));
      setCompareImage('');
      setErrorMessage(null);
    }
  };

  const runComparison = async () => {
    setIsComparing(true);
    setErrorMessage(null);
    try {
      const formData = new FormData();
      if (customFile) {
        formData.append('image', customFile);
      } else {
        formData.append('imagePath', compareImage);
      }
      formData.append('confidence', confThreshold.toString());

      const resp = await fetch('/api/model/compare', {
        method: 'POST',
        body: formData
      });

      const data = await resp.json();
      if (!resp.ok || data.status === 'error') {
        throw new Error(data.message || `Comparison failed with status ${resp.status}`);
      }

      setCompareResult(data);
    } catch (err: any) {
      console.error('Comparison error:', err);
      setErrorMessage(err.message || 'Failed to execute dual-model comparison.');
    } finally {
      setIsComparing(false);
    }
  };

  useEffect(() => {
    // Run initial comparison on mount
    runComparison();
  }, []);

  return (
    <div className="p-6 space-y-6 max-w-[1720px] mx-auto text-slate-100">
      {/* Header Banner */}
      <div className="bg-[#111827] border border-slate-800 rounded-2xl p-6 shadow-xl relative overflow-hidden">
        <div className="absolute top-0 right-0 w-96 h-96 bg-orange-500/5 rounded-full blur-3xl pointer-events-none" />
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 relative z-10">
          <div className="space-y-1">
            <div className="flex items-center gap-3">
              <div className="p-2.5 rounded-xl bg-orange-500/10 border border-orange-500/30 text-orange-400">
                <Cpu className="w-5 h-5" />
              </div>
              <h1 className="text-xl font-bold tracking-tight text-white">AI Model Lab & Transparency Suite</h1>
              <span className="text-[11px] font-mono px-2.5 py-0.5 rounded-full bg-slate-800 text-slate-300 border border-slate-700">
                Inference Explainability
              </span>
            </div>
            <p className="text-xs text-slate-400 max-w-3xl leading-relaxed">
              Demystifying computer vision inference: compare the COCO baseline against the Floor Guard custom hazard detector, inspect feature extraction steps, and explore architectural metrics.
            </p>
          </div>

          {/* Navigation Pill Tabs */}
          <div className="flex items-center gap-1.5 p-1 rounded-xl bg-slate-900 border border-slate-800">
            <button
              onClick={() => setActiveTab('comparison')}
              className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all cursor-pointer ${
                activeTab === 'comparison'
                  ? 'bg-orange-500 text-white shadow-md'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              Model Comparison Arena
            </button>
            <button
              onClick={() => setActiveTab('pipeline')}
              className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all cursor-pointer ${
                activeTab === 'pipeline'
                  ? 'bg-orange-500 text-white shadow-md'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              6-Step Inference Pipeline
            </button>
            <button
              onClick={() => setActiveTab('registry')}
              className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all cursor-pointer ${
                activeTab === 'registry'
                  ? 'bg-orange-500 text-white shadow-md'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              Model Registry & Checkpoints
            </button>
          </div>
        </div>
      </div>

      {/* TAB 1: MODEL COMPARISON ARENA */}
      {activeTab === 'comparison' && (
        <div className="space-y-6">
          {/* Controls Bar */}
          <div className="bg-[#111827] border border-slate-800 rounded-2xl p-5 space-y-4">
            <div className="flex flex-wrap items-center justify-between gap-4">
              <div>
                <h2 className="text-xs font-bold uppercase tracking-wider text-slate-400">
                  Select Evaluation Image
                </h2>
                <p className="text-[11px] text-slate-500 mt-0.5">
                  Run both models simultaneously on the exact same pixel tensor without altering production settings.
                </p>
              </div>

              <div className="flex items-center gap-4">
                <div className="flex items-center gap-2">
                  <span className="text-[11px] text-slate-400 font-mono">Confidence:</span>
                  <span className="text-xs font-mono font-bold text-orange-400">
                    {Math.round(confThreshold * 100)}%
                  </span>
                  <input
                    type="range"
                    min="0.10"
                    max="0.80"
                    step="0.05"
                    value={confThreshold}
                    onChange={(e) => setConfThreshold(parseFloat(e.target.value))}
                    className="w-24 accent-orange-500 bg-slate-800 h-1.5 rounded-lg appearance-none cursor-pointer"
                  />
                </div>

                <button
                  onClick={runComparison}
                  disabled={isComparing}
                  className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold shadow-lg transition-all cursor-pointer ${
                    isComparing
                      ? 'bg-slate-700 text-slate-400 cursor-not-allowed'
                      : 'bg-orange-500 hover:bg-orange-600 text-white shadow-orange-500/20 active:scale-[0.98]'
                  }`}
                >
                  <Zap className={`w-3.5 h-3.5 ${isComparing ? 'animate-spin' : 'fill-current'}`} />
                  <span>{isComparing ? 'Running Dual Inference...' : 'Compare Models'}</span>
                </button>
              </div>
            </div>

            {/* Quick Sample Selector */}
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-2">
              {sampleImages.map((s, idx) => (
                <button
                  key={idx}
                  onClick={() => handleSelectSample(s.path)}
                  className={`p-2 rounded-xl border text-left transition-all cursor-pointer flex items-center gap-2 ${
                    compareImage === s.path && !customFile
                      ? 'border-orange-500 bg-orange-500/10 text-white'
                      : 'border-slate-800 bg-slate-900/60 hover:border-slate-700 text-slate-400 hover:text-slate-200'
                  }`}
                >
                  <div className="w-8 h-8 rounded-lg overflow-hidden bg-black shrink-0">
                    <img src={s.path} alt={s.name} className="w-full h-full object-cover" />
                  </div>
                  <div className="text-[11px] truncate font-medium">{s.name}</div>
                </button>
              ))}

              {/* Upload Custom */}
              <button
                onClick={() => fileInputRef.current?.click()}
                className={`p-2 rounded-xl border border-dashed text-left transition-all cursor-pointer flex items-center gap-2 ${
                  customFile
                    ? 'border-orange-500 bg-orange-500/10 text-white'
                    : 'border-slate-700 bg-slate-900/40 hover:border-slate-600 text-slate-400'
                }`}
              >
                <input
                  ref={fileInputRef}
                  type="file"
                  accept="image/jpeg,image/png,image/webp"
                  className="hidden"
                  onChange={handleFileChange}
                />
                <div className="w-8 h-8 rounded-lg bg-slate-800 flex items-center justify-center text-orange-400 shrink-0">
                  <Upload className="w-4 h-4" />
                </div>
                <div className="text-[11px] truncate font-medium">
                  {customFile ? customFile.name : 'Upload Custom'}
                </div>
              </button>
            </div>
          </div>

          {errorMessage && (
            <div className="p-3.5 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 shrink-0" />
              <span>{errorMessage}</span>
            </div>
          )}

          {/* Comparison Side-by-Side Arena */}
          {compareResult && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Left Side: Model A (COCO Baseline) */}
              <div className="bg-[#111827] border border-slate-800 rounded-2xl p-5 space-y-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2.5">
                    <span className="w-2.5 h-2.5 rounded-full bg-cyan-400" />
                    <div>
                      <h3 className="text-sm font-bold text-white">Model A: YOLOv8s COCO Pretrained</h3>
                      <div className="text-[10px] text-slate-400 font-mono">Production Baseline (80 General Classes)</div>
                    </div>
                  </div>
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-cyan-500/10 text-cyan-400 border border-cyan-500/30">
                    Production Active
                  </span>
                </div>

                {/* Annotated Output Preview */}
                <div className="relative rounded-xl overflow-hidden border border-slate-800 bg-black aspect-16/10 flex items-center justify-center">
                  <img
                    src={compareResult.model_a_coco?.annotated_image_url || compareResult.model_a_coco?.image_url}
                    alt="COCO Inference Output"
                    className="w-full h-full object-contain"
                  />
                  <div className="absolute top-2.5 left-2.5 bg-black/80 backdrop-blur-md px-2.5 py-1 rounded border border-slate-700 text-white font-mono text-[10px]">
                    Latency: {compareResult.model_a_coco?.inference_duration_ms || 85}ms
                  </div>
                  <div className="absolute bottom-2.5 right-2.5 bg-black/80 backdrop-blur-md px-2.5 py-1 rounded border border-slate-700 text-slate-300 font-mono text-[10px]">
                    {compareResult.model_a_coco?.detections?.length || 0} objects detected
                  </div>
                </div>

                {/* Detections List */}
                <div className="space-y-2">
                  <div className="text-[11px] font-bold uppercase tracking-wider text-slate-400">
                    Detections Found:
                  </div>
                  {compareResult.model_a_coco?.detections && compareResult.model_a_coco.detections.length > 0 ? (
                    <div className="space-y-1.5 max-h-48 overflow-y-auto pr-1">
                      {compareResult.model_a_coco.detections.map((det: any, dIdx: number) => (
                        <div
                          key={dIdx}
                          className="p-2.5 rounded-lg bg-slate-900 border border-slate-800 flex items-center justify-between text-xs font-mono"
                        >
                          <div className="flex items-center gap-2">
                            <span className="text-cyan-400 font-bold capitalize">{det.class_name}</span>
                            <span className="text-[10px] text-slate-500">
                              [{det.bounding_box.x}, {det.bounding_box.y}, {det.bounding_box.width}x{det.bounding_box.height}]
                            </span>
                          </div>
                          <div className="text-slate-300 font-bold">{det.confidence_percent}</div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="p-3 rounded-lg bg-slate-900/60 border border-slate-800 text-slate-400 text-xs font-mono">
                      No COCO objects detected at {Math.round(confThreshold * 100)}% confidence threshold.
                    </div>
                  )}
                </div>

                {/* Architectural Assessment */}
                <div className="p-3 rounded-xl bg-slate-900 border border-slate-800 space-y-1.5">
                  <div className="text-[11px] font-bold text-cyan-400 flex items-center gap-1.5">
                    <Info className="w-3.5 h-3.5" />
                    <span>Baseline Behavior Analysis</span>
                  </div>
                  <p className="text-[11px] text-slate-300 leading-relaxed">
                    Trained on standard COCO 80 categories (bottles, chairs, persons, backpacks). It does not have specialized classes for liquid spills, puddle sheen, or glass shards. It may map floor debris to objects like bowls or suitcases.
                  </p>
                </div>
              </div>

              {/* Right Side: Model B (Custom Floor Guard Detector) */}
              <div className="bg-[#111827] border border-orange-500/30 rounded-2xl p-5 space-y-4 relative shadow-lg shadow-orange-500/5">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2.5">
                    <span className="w-2.5 h-2.5 rounded-full bg-orange-400" />
                    <div>
                      <h3 className="text-sm font-bold text-white">Model B: Floor Guard YOLOv8s Phase 4.2</h3>
                      <div className="text-[10px] text-orange-400 font-mono">Specialized Hazard Detector (4 Classes)</div>
                    </div>
                  </div>
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-orange-500/10 text-orange-400 border border-orange-500/30">
                    Candidate Detector
                  </span>
                </div>

                {/* Annotated Output Preview */}
                <div className="relative rounded-xl overflow-hidden border border-slate-800 bg-black aspect-16/10 flex items-center justify-center">
                  <img
                    src={compareResult.model_b_custom?.annotated_image_url || compareResult.model_b_custom?.image_url}
                    alt="Custom Model Output"
                    className="w-full h-full object-contain"
                  />
                  <div className="absolute top-2.5 left-2.5 bg-black/80 backdrop-blur-md px-2.5 py-1 rounded border border-slate-700 text-white font-mono text-[10px]">
                    Latency: {compareResult.model_b_custom?.inference_duration_ms || 92}ms
                  </div>
                  <div className="absolute bottom-2.5 right-2.5 bg-black/80 backdrop-blur-md px-2.5 py-1 rounded border border-slate-700 text-orange-400 font-mono text-[10px] font-bold">
                    {compareResult.model_b_custom?.detections?.length || 0} hazards detected
                  </div>
                </div>

                {/* Detections List */}
                <div className="space-y-2">
                  <div className="text-[11px] font-bold uppercase tracking-wider text-slate-400">
                    Floor Hazards Identified:
                  </div>
                  {compareResult.model_b_custom?.detections && compareResult.model_b_custom.detections.length > 0 ? (
                    <div className="space-y-1.5 max-h-48 overflow-y-auto pr-1">
                      {compareResult.model_b_custom.detections.map((det: any, dIdx: number) => (
                        <div
                          key={dIdx}
                          className="p-2.5 rounded-lg bg-orange-500/5 border border-orange-500/20 flex items-center justify-between text-xs font-mono"
                        >
                          <div className="flex items-center gap-2">
                            <span className="text-orange-400 font-bold capitalize">
                              {det.class_name.replace(/_/g, ' ')}
                            </span>
                            <span className="text-[10px] text-slate-400">
                              [{det.bounding_box.x}, {det.bounding_box.y}, {det.bounding_box.width}x{det.bounding_box.height}]
                            </span>
                          </div>
                          <div className="flex items-center gap-2">
                            <span className="text-rose-400 font-semibold text-[10px]">{det.severity}</span>
                            <span className="text-white font-bold">{det.confidence_percent}</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="p-3 rounded-lg bg-slate-900/60 border border-slate-800 text-slate-400 text-xs font-mono">
                      No floor hazards detected at {Math.round(confThreshold * 100)}% threshold.
                    </div>
                  )}
                </div>

                {/* Architectural Assessment */}
                <div className="p-3 rounded-xl bg-orange-500/10 border border-orange-500/20 space-y-1.5">
                  <div className="text-[11px] font-bold text-orange-400 flex items-center gap-1.5">
                    <ShieldCheck className="w-3.5 h-3.5" />
                    <span>Specialist Behavior Analysis</span>
                  </div>
                  <p className="text-[11px] text-slate-300 leading-relaxed">
                    Custom-trained with transfer learning across 100 epochs for floor slips/trips. Demonstrates high sensitivity to broken glass shard clusters and obstacles. Note: liquid puddle boundaries experience attenuation under extreme specular reflection.
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* TAB 2: 6-STEP INFERENCE PIPELINE */}
      {activeTab === 'pipeline' && (
        <div className="space-y-6">
          <div className="bg-[#111827] border border-slate-800 rounded-2xl p-6 space-y-4">
            <div>
              <h2 className="text-sm font-bold text-white tracking-tight flex items-center gap-2">
                <Layers className="w-4 h-4 text-orange-400" />
                The Complete Floor Guard AI Inference Journey
              </h2>
              <p className="text-xs text-slate-400 mt-1 max-w-2xl">
                Every uploaded image or video keyframe undergoes an exact 6-stage mathematical transformation before a hazard alert is published.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 pt-2">
              {/* Step 1 */}
              <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-3 relative group hover:border-orange-500/40 transition-colors">
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-orange-500/10 text-orange-400 border border-orange-500/30">
                    STAGE 01
                  </span>
                  <span className="text-xs font-mono text-slate-500">I/O Ingestion</span>
                </div>
                <h3 className="text-xs font-bold text-white">Input Acquisition & Validation</h3>
                <p className="text-[11px] text-slate-400 leading-relaxed">
                  The client submits an image or video stream. Pillow (PIL) decodes the file buffer into an uncompressed RGB bitmap array, verifying image integrity and recording physical dimensions (e.g. 1920x1080).
                </p>
              </div>

              {/* Step 2 */}
              <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-3 relative group hover:border-orange-500/40 transition-colors">
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-orange-500/10 text-orange-400 border border-orange-500/30">
                    STAGE 02
                  </span>
                  <span className="text-xs font-mono text-slate-500">Tensor Prep</span>
                </div>
                <h3 className="text-xs font-bold text-white">Letterbox Resize & Normalization</h3>
                <p className="text-[11px] text-slate-400 leading-relaxed">
                  Preserving aspect ratio, the image is scaled to 640x640 with bilinear padding. Integer pixel values [0, 255] are transformed into float32 tensors normalized to [0.0, 1.0] with layout (1, 3, 640, 640).
                </p>
              </div>

              {/* Step 3 */}
              <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-3 relative group hover:border-orange-500/40 transition-colors">
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-orange-500/10 text-orange-400 border border-orange-500/30">
                    STAGE 03
                  </span>
                  <span className="text-xs font-mono text-slate-500">Feature Pyramids</span>
                </div>
                <h3 className="text-xs font-bold text-white">CSPDarknet & PANet Backbone</h3>
                <p className="text-[11px] text-slate-400 leading-relaxed">
                  Cross-Stage Partial connections extract hierarchical spatial features. PANet feature pyramids merge high-resolution edge details (glass shards) with semantic contextual maps (fluid puddles).
                </p>
              </div>

              {/* Step 4 */}
              <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-3 relative group hover:border-orange-500/40 transition-colors">
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-orange-500/10 text-orange-400 border border-orange-500/30">
                    STAGE 04
                  </span>
                  <span className="text-xs font-mono text-slate-500">Anchor-Free Heads</span>
                </div>
                <h3 className="text-xs font-bold text-white">Decoupled Head Predictions</h3>
                <p className="text-[11px] text-slate-400 leading-relaxed">
                  Decoupled classification and regression branches evaluate candidate coordinates directly without predefined anchor box bias, producing bounding-box offsets and class probability logits.
                </p>
              </div>

              {/* Step 5 */}
              <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-3 relative group hover:border-orange-500/40 transition-colors">
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-orange-500/10 text-orange-400 border border-orange-500/30">
                    STAGE 05
                  </span>
                  <span className="text-xs font-mono text-slate-500">Suppression</span>
                </div>
                <h3 className="text-xs font-bold text-white">Non-Maximum Suppression (NMS)</h3>
                <p className="text-[11px] text-slate-400 leading-relaxed">
                  Candidate boxes below the confidence threshold (e.g. 25%) are eliminated. Overlapping boxes covering the same physical hazard are clustered via IoU intersection-over-union suppression (IoU &gt; 0.45).
                </p>
              </div>

              {/* Step 6 */}
              <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-3 relative group hover:border-orange-500/40 transition-colors">
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-orange-500/10 text-orange-400 border border-orange-500/30">
                    STAGE 06
                  </span>
                  <span className="text-xs font-mono text-slate-500">Persistence</span>
                </div>
                <h3 className="text-xs font-bold text-white">Pixel Mapping & DB Persistence</h3>
                <p className="text-[11px] text-slate-400 leading-relaxed">
                  Normalized coordinates are scaled back to the source image's native resolution. Annotated overlay images are rendered via PIL and saved to disk, while telemetry records are saved to SQLite.
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* TAB 3: MODEL REGISTRY & CHECKPOINTS */}
      {activeTab === 'registry' && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Model Card 1 */}
            <div className="bg-[#111827] border border-slate-800 rounded-2xl p-6 space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Cpu className="w-5 h-5 text-cyan-400" />
                  <h3 className="text-base font-bold text-white">Ultralytics YOLOv8s COCO</h3>
                </div>
                <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-cyan-500/10 text-cyan-400 border border-cyan-500/30">
                  Production Default
                </span>
              </div>

              <p className="text-xs text-slate-400 leading-relaxed">
                Official pretrained PyTorch checkpoint from Ultralytics. Serves as the reliable, stable baseline for general object detection across 80 common categories.
              </p>

              <div className="p-3 rounded-xl bg-slate-900 border border-slate-800 space-y-2 text-xs font-mono">
                <div className="flex justify-between">
                  <span className="text-slate-500">Weights Path:</span>
                  <span className="text-slate-200">models/pretrained/yolov8s.pt</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Parameters:</span>
                  <span className="text-slate-200">11.2M</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Input Resolution:</span>
                  <span className="text-slate-200">640x640</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Classes Supported:</span>
                  <span className="text-cyan-400 font-bold">80 Categories</span>
                </div>
              </div>
            </div>

            {/* Model Card 2 */}
            <div className="bg-[#111827] border border-orange-500/30 rounded-2xl p-6 space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <ShieldCheck className="w-5 h-5 text-orange-400" />
                  <h3 className="text-base font-bold text-white">Floor Guard YOLOv8s Phase 4.2</h3>
                </div>
                <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-orange-500/10 text-orange-400 border border-orange-500/30">
                  Candidate Detector
                </span>
              </div>

              <p className="text-xs text-slate-400 leading-relaxed">
                Custom transfer-learned detector trained for 100 epochs on verified floor hazard images with synthetic liquid augmentation and clean-floor background samples.
              </p>

              <div className="p-3 rounded-xl bg-slate-900 border border-slate-800 space-y-2 text-xs font-mono">
                <div className="flex justify-between">
                  <span className="text-slate-500">Weights Path:</span>
                  <span className="text-slate-200 truncate max-w-[220px]">
                    models/detection/floorguard_yolov8s_phase4_2_best.pt
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Validation mAP@0.5:</span>
                  <span className="text-orange-400 font-bold">67.3% (Phase 4.2 Benchmark)</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Clean Floor False Positive:</span>
                  <span className="text-emerald-400 font-bold">0.0% (Clean Floor Hardened)</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Target Classes:</span>
                  <span className="text-orange-400 font-bold">water, oil, glass, obstacle</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
