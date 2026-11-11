import React, { useState } from 'react';
import { Bell, CheckCircle2, LogOut, LogIn, ShieldCheck, Cpu } from 'lucide-react';
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
        {/* Dedicated Active Model Indicator Badge (No unrelated COCO models) */}
        <button
          onClick={onOpenModelDetails}
          className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-[#131b29] border border-[#202e46] hover:border-[#22c55e]/60 transition-all cursor-pointer text-xs font-semibold text-slate-200"
          title="Click to view model architecture and metrics"
        >
          <span className="w-2 h-2 rounded-full bg-[#22c55e] shadow-[0_0_8px_#22c55e] animate-pulse" />
          <span>
            Model: <span className="text-[#22c55e]">FloorGuard-YOLOv8 Canonical (13 Classes)</span>
          </span>
          <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
            Active
          </span>
        </button>

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
