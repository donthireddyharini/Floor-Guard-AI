import React, { useState, useEffect } from 'react';
import {
  ShieldAlert,
  ChevronDown,
  Cpu,
  Calendar,
  Layers,
  Activity,
  AlertTriangle,
  CheckCircle2,
  Sparkles
} from 'lucide-react';
import { NavSection, ModelItem } from '../types';

interface HeaderProps {
  activeSection: NavSection;
  onOpenModelDetails: () => void;
  selectedDateRange: string;
  onSelectDateRange: (range: string) => void;
  activeModel?: ModelItem;
  allModels?: ModelItem[];
  onSelectModel?: (modelId: string) => void;
}

export const Header: React.FC<HeaderProps> = ({
  activeSection,
  onOpenModelDetails,
  selectedDateRange,
  onSelectDateRange,
  activeModel,
  allModels = [],
  onSelectModel
}) => {
  const [showModelDropdown, setShowModelDropdown] = useState(false);
  const [backendHealthy, setBackendHealthy] = useState(true);

  // Poll health status
  useEffect(() => {
    const check = () => {
      fetch('/api/health')
        .then(res => res.json())
        .then(data => setBackendHealthy(data.status === 'ok'))
        .catch(() => setBackendHealthy(false));
    };
    check();
    const interval = setInterval(check, 15000);
    return () => clearInterval(interval);
  }, []);

  const sectionTitles: Record<NavSection, { title: string; subtitle: string }> = {
    overview: {
      title: 'Facility Safety Overview',
      subtitle: 'Real-time hazard telemetry and operational safety metrics'
    },
    image_detection: {
      title: 'Image Hazard Inspection',
      subtitle: 'Execute multi-model computer vision inference on floor imagery'
    },
    video_analysis: {
      title: 'Video Stream Analysis',
      subtitle: 'Per-frame OpenCV video decoding and sequential hazard tracking'
    },
    hazard_history: {
      title: 'Detection History & Audit',
      subtitle: 'Complete database of historical inspections, original frames & annotated masks'
    },
    analytics: {
      title: 'Analytics & Scientific Evaluation',
      subtitle: 'Operational incident distributions and verified benchmark validation telemetry'
    },
    ai_model_lab: {
      title: 'AI Model Lab & Transparency',
      subtitle: 'Step-by-step inference pipeline inspection and dual-model comparison arena'
    },
    settings: {
      title: 'System & Detection Settings',
      subtitle: 'Configure inference thresholds, frame sampling intervals, and storage'
    }
  };

  const current = sectionTitles[activeSection] || sectionTitles.overview;
  const isCustom = activeModel?.id?.includes('floorguard') || false;

  return (
    <header className="bg-[#0e1422] border-b border-[#1e293d] sticky top-0 z-20 px-6 py-4 flex flex-wrap items-center justify-between gap-4">
      {/* Title & Section Breadcrumb */}
      <div>
        <div className="flex items-center gap-2 text-xs font-mono text-slate-400">
          <span>FLOOR GUARD AI</span>
          <span>/</span>
          <span className="text-[#f97316] uppercase font-bold">{activeSection.replace('_', ' ')}</span>
        </div>
        <h2 className="text-lg font-bold text-white tracking-tight mt-0.5">
          {current.title}
        </h2>
        <p className="text-xs text-slate-400">{current.subtitle}</p>
      </div>

      {/* Right Controls */}
      <div className="flex flex-wrap items-center gap-3">
        {/* Backend Health Badge */}
        <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-[#111827] border border-[#1f293d] text-xs font-mono">
          <span className={`w-2 h-2 rounded-full ${backendHealthy ? 'bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]' : 'bg-red-500'}`} />
          <span className="text-slate-300">{backendHealthy ? 'SYSTEM ONLINE' : 'OFFLINE'}</span>
        </div>

        {/* Model Switcher Dropdown */}
        <div className="relative">
          <button
            onClick={() => setShowModelDropdown(!showModelDropdown)}
            className="flex items-center gap-2.5 px-3.5 py-1.5 rounded-xl bg-[#111827] hover:bg-[#192437] border border-[#1f293d] hover:border-[#f97316]/50 text-xs transition-all cursor-pointer shadow-sm"
          >
            <div className={`w-6 h-6 rounded-lg ${isCustom ? 'bg-orange-500/20 text-[#f97316]' : 'bg-blue-500/20 text-blue-400'} flex items-center justify-center`}>
              <Cpu className="w-3.5 h-3.5" />
            </div>
            <div className="text-left font-mono">
              <div className="text-[10px] text-slate-400">ACTIVE DETECTOR</div>
              <div className="font-bold text-white text-[11px] truncate max-w-[170px]">
                {activeModel?.name || 'YOLOv8s Pretrained'}
              </div>
            </div>
            <ChevronDown className="w-3.5 h-3.5 text-slate-400 ml-1" />
          </button>

          {showModelDropdown && (
            <div className="absolute right-0 mt-2 w-80 rounded-2xl bg-[#111827] border border-[#1f293d] shadow-2xl p-2 z-50 space-y-1.5 animate-in fade-in slide-in-from-top-2 duration-150">
              <div className="p-2 border-b border-[#1f293d] text-xs font-mono text-slate-400 flex items-center justify-between">
                <span>SELECT DETECTION MODEL</span>
                <span className="text-[10px] text-[#f97316]">SAFE CONTROL</span>
              </div>
              {allModels.map((m) => {
                const isSelected = m.id === activeModel?.id;
                const isCustomModel = m.id.includes('floorguard');
                return (
                  <button
                    key={m.id}
                    onClick={() => {
                      if (onSelectModel) onSelectModel(m.id);
                      setShowModelDropdown(false);
                    }}
                    className={`w-full text-left p-3 rounded-xl transition-all cursor-pointer flex flex-col gap-1 border ${
                      isSelected
                        ? 'bg-[#1e130a] border-[#f97316]/50 text-white'
                        : 'hover:bg-[#161f30] border-transparent text-slate-300'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-xs flex items-center gap-1.5">
                        {isCustomModel && <Sparkles className="w-3 h-3 text-[#f97316]" />}
                        {m.name}
                      </span>
                      <span className={`text-[9px] px-1.5 py-0.5 rounded font-mono ${
                        isCustomModel ? 'bg-orange-500/20 text-orange-400' : 'bg-blue-500/20 text-blue-400'
                      }`}>
                        {isCustomModel ? 'EXPERIMENTAL' : 'PRODUCTION'}
                      </span>
                    </div>
                    <p className="text-[10px] text-slate-400 font-sans line-clamp-1">
                      {m.description || (isCustomModel ? 'Trained for water, oil, glass, obstacle hazards' : 'Pretrained on 80 COCO common object classes')}
                    </p>
                  </button>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </header>
  );
};
