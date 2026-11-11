import React, { useState } from 'react';
import { ChevronDown, Bell, CheckCircle2, LogOut, LogIn, ShieldCheck, Lock } from 'lucide-react';
import { NavSection } from '../types';

interface HeaderProps {
  activeSection: NavSection;
  onOpenModelDetails: () => void;
  selectedDateRange?: string;
  onSelectDateRange?: (range: string) => void;
  activeModel?: any;
  allModels?: any[];
  onSelectModel?: (modelId: string) => void;
  isAuthenticated?: boolean;
  onSignOut?: () => void;
  onOpenLogin?: () => void;
  userRole?: string;
}

export const Header: React.FC<HeaderProps> = ({
  activeSection,
  onOpenModelDetails,
  activeModel,
  allModels = [],
  onSelectModel,
  isAuthenticated = false,
  onSignOut,
  onOpenLogin,
  userRole = 'Senior Facility Safety Officer'
}) => {
  const [showModelDropdown, setShowModelDropdown] = useState(false);
  const [showNotifications, setShowNotifications] = useState(false);

  const titles: Record<NavSection, { title: string; subtitle: string }> = {
    home: {
      title: 'Floor Guard AI — Platform Intro',
      subtitle: 'Autonomous facility floor hazard inspection, computer vision pipeline, and operator login portal'
    },
    overview: {
      title: 'Floor Hazard Overview',
      subtitle: 'AI-powered detection of water spills, oil spills, broken glass and floor obstacles'
    },
    image_detection: {
      title: 'Detection Workspace',
      subtitle: 'Detailed computer vision hazard localization, bounding box annotation, and risk analysis'
    },
    video_analysis: {
      title: 'Video Analysis Pipeline',
      subtitle: 'Offline frame-by-frame hazard localization with keyframe timestamps and incident summaries'
    },
    dataset_training: {
      title: 'Dataset & Model Training',
      subtitle: 'Dataset provenance, class distributions, train/val/test splits, and Ultralytics YOLOv8 metrics'
    },
    hazard_history: {
      title: 'Hazard Detection History',
      subtitle: 'Search, filter, inspect evidence images, and export verified hazard logs'
    },
    analytics: {
      title: 'Safety Risk Analytics',
      subtitle: 'Historical incident trends, diurnal heatmap distributions, and model performance matrix'
    },
    settings: {
      title: 'System Settings',
      subtitle: 'Configure hazard confidence thresholds, risk rules, and detection parameters'
    }
  };

  const current = titles[activeSection] || titles.home;

  return (
    <header className="px-6 py-4 border-b border-[#182335] bg-[#0c121d]/90 backdrop-blur-md sticky top-0 z-30 flex items-center justify-between gap-4">
      {/* Title & Subtitle */}
      <div>
        <h2 className="text-xl font-bold text-white tracking-tight">{current.title}</h2>
        <p className="text-xs text-slate-400 font-medium mt-0.5">{current.subtitle}</p>
      </div>

      {/* Right Controls */}
      <div className="flex items-center gap-3 shrink-0">
        {/* Interactive Model Selector Dropdown */}
        <div className="relative">
          <button
            onClick={() => setShowModelDropdown(!showModelDropdown)}
            className={`flex items-center gap-2 px-3 py-1.5 rounded-lg bg-[#131b29] border transition-all cursor-pointer text-xs font-semibold ${
              activeModel?.task === 'classification'
                ? 'border-[#38bdf8]/40 hover:border-[#38bdf8] text-slate-200'
                : 'border-[#202e46] hover:border-[#22c55e]/60 text-slate-200'
            }`}
          >
            <span
              className={`w-2 h-2 rounded-full ${
                activeModel?.task === 'classification'
                  ? 'bg-[#38bdf8] shadow-[0_0_8px_#38bdf8]'
                  : 'bg-[#22c55e] shadow-[0_0_8px_#22c55e]'
              }`}
            />
            <span>
              Model:{' '}
              <span className={activeModel?.task === 'classification' ? 'text-[#38bdf8]' : 'text-[#22c55e]'}>
                {activeModel?.name?.replace(' Detector', '').replace(' Classifier', '') || 'YOLOv8s'}
              </span>
            </span>
            <ChevronDown className="w-3.5 h-3.5 text-slate-400" />
          </button>

          {showModelDropdown && (
            <div className="absolute right-0 mt-2 w-80 rounded-xl bg-[#141d2c] border border-[#22334c] shadow-2xl p-2 z-50 space-y-1.5">
              <div className="px-2 py-1.5 text-[11px] font-semibold text-slate-400 border-b border-[#1f2d42] flex items-center justify-between">
                <span>Active Safety Checkpoints</span>
                <span className="text-[10px] text-[#22c55e]">YOLOv8s Loaded</span>
              </div>

              {allModels.map((m: any) => {
                const isSelected = (activeModel?.id || 'm1') === m.id;
                return (
                  <button
                    key={m.id}
                    onClick={() => {
                      if (onSelectModel) onSelectModel(m.id);
                      setShowModelDropdown(false);
                    }}
                    className={`w-full text-left p-2.5 rounded-lg transition-all flex items-start justify-between cursor-pointer ${
                      isSelected
                        ? 'bg-[#1b2a3d] border border-[#22c55e]/50'
                        : 'hover:bg-[#192437] border border-transparent'
                    }`}
                  >
                    <div>
                      <div className="flex items-center gap-1.5">
                        <span className="text-xs font-bold text-white">{m.name}</span>
                        {isSelected && (
                          <CheckCircle2 className="w-3.5 h-3.5 text-[#22c55e] shrink-0" />
                        )}
                      </div>
                      <div className="text-[10px] text-slate-400 mt-0.5 line-clamp-1">
                        {m.description || 'Ultralytics floor hazard detector'}
                      </div>
                      <div className="flex items-center gap-2 mt-1.5 text-[10px] font-mono text-slate-400">
                        <span>mAP50: <span className="text-[#22c55e]">{(m.metrics?.mAP50 * 100).toFixed(1)}%</span></span>
                        <span>•</span>
                        <span>Lat: <span className="text-[#38bdf8]">{m.metrics?.latency_batch1_ms}ms</span></span>
                      </div>
                    </div>
                    <div className="text-right shrink-0">
                      <span className={`text-[10px] px-1.5 py-0.5 rounded font-mono ${
                        isSelected
                          ? 'bg-[#22c55e]/20 text-[#22c55e]'
                          : 'bg-slate-800 text-slate-400'
                      }`}>
                        {isSelected ? '✓ Active' : 'Switch'}
                      </span>
                    </div>
                  </button>
                );
              })}

              <button
                onClick={() => {
                  onOpenModelDetails();
                  setShowModelDropdown(false);
                }}
                className="w-full text-center py-1.5 text-[11px] font-semibold text-slate-400 hover:text-white transition-colors cursor-pointer"
              >
                Inspect Full Evaluation Matrix &rarr;
              </button>
            </div>
          )}
        </div>

        {/* Notification Bell */}
        <div className="relative">
          <button
            onClick={() => setShowNotifications(!showNotifications)}
            className="w-9 h-9 rounded-lg bg-[#131b29] border border-[#202e46] flex items-center justify-center text-slate-300 hover:text-white hover:border-slate-600 transition-colors relative"
            aria-label="Notifications"
          >
            <Bell className="w-4 h-4" />
            <span className="absolute -top-1 -right-1 w-4 h-4 rounded-full bg-[#ef4444] text-[10px] font-bold text-white flex items-center justify-center shadow-md">
              1
            </span>
          </button>

          {showNotifications && (
            <div className="absolute right-0 mt-1 w-80 rounded-xl bg-[#141d2c] border border-[#22334c] shadow-2xl p-3 z-50">
              <div className="flex items-center justify-between pb-2 border-b border-[#1f2d42]">
                <span className="text-xs font-bold text-white">System Alerts</span>
                <span className="text-[10px] text-slate-400">1 Unread</span>
              </div>
              <div className="mt-2.5 p-2.5 rounded-lg bg-[#1a2436] border border-[#ef4444]/30 flex items-start gap-2.5">
                <span className="w-2 h-2 rounded-full bg-[#ef4444] mt-1 shrink-0" />
                <div className="text-[11px]">
                  <div className="font-semibold text-white">High Severity Hazard Detected</div>
                  <div className="text-slate-400 mt-0.5">Water spill identified on Lobby Entrance surface. Maintenance notified.</div>
                  <div className="text-[10px] text-slate-500 mt-1 font-mono">May 26, 10:24 AM</div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* User Auth Status & Controls */}
        {isAuthenticated ? (
          <div className="flex items-center gap-2 pl-1 border-l border-[#1c283a]">
            {/* User Avatar & Role */}
            <div 
              className="flex items-center gap-2 px-2.5 py-1 rounded-xl bg-[#131b29] border border-[#202e46]"
              title={`Logged in as ${userRole}`}
            >
              <div className="w-7 h-7 rounded-full bg-[#1b3a2a] border border-[#22c55e]/40 flex items-center justify-center text-[11px] font-bold text-[#22c55e]">
                DH
              </div>
              <div className="hidden sm:block text-left">
                <div className="text-[11px] font-bold text-slate-200 leading-tight">Operator DH</div>
                <div className="text-[9px] text-[#22c55e] font-mono leading-tight flex items-center gap-1">
                  <ShieldCheck className="w-2.5 h-2.5 inline" />
                  <span>Authenticated</span>
                </div>
              </div>
            </div>

            {/* Sign Out Button */}
            {onSignOut && (
              <button
                onClick={onSignOut}
                className="flex items-center gap-1 px-2.5 py-1.5 rounded-lg bg-[#1a2230] hover:bg-red-950/40 text-slate-400 hover:text-red-300 border border-[#24334a] hover:border-red-500/40 text-xs font-medium transition-colors cursor-pointer"
                title="Sign Out of Floor Guard AI"
              >
                <LogOut className="w-3.5 h-3.5" />
                <span className="hidden md:inline">Sign Out</span>
              </button>
            )}
          </div>
        ) : (
          <div className="flex items-center gap-2 pl-1 border-l border-[#1c283a]">
            <button
              onClick={onOpenLogin}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[#22c55e] hover:bg-[#16a34a] text-black text-xs font-bold shadow-md shadow-green-950/30 transition-all cursor-pointer"
            >
              <LogIn className="w-3.5 h-3.5 stroke-[2.5]" />
              <span>Sign In</span>
            </button>
          </div>
        )}
      </div>
    </header>
  );
};
