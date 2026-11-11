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
  userName?: string;
  userEmail?: string;
  authProvider?: string;
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
  userRole = 'Senior Facility Safety Officer',
  userName = 'Harini Donthireddy',
  userEmail = 'donthireddyharini@gmail.com',
  authProvider = 'email'
}) => {
  const [showNotifications, setShowNotifications] = useState(false);

  const getInitials = (fullName: string) => {
    if (!fullName) return 'HD';
    const parts = fullName.trim().split(' ').filter(Boolean);
    if (parts.length >= 2) {
      return `${parts[0][0]}${parts[parts.length - 1][0]}`.toUpperCase();
    }
    return fullName.slice(0, 2).toUpperCase();
  };

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
  const initials = getInitials(userName);

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
            {/* User Avatar & Name */}
            <div 
              className="flex items-center gap-2.5 px-3 py-1.5 rounded-xl bg-[#131b29] border border-[#202e46]"
              title={`Logged in as ${userName} (${userEmail})`}
            >
              <div className="w-7 h-7 rounded-full bg-[#1b3a2a] border border-[#22c55e]/40 flex items-center justify-center text-[11px] font-bold text-[#22c55e]">
                {initials}
              </div>
              <div className="hidden sm:block text-left">
                <div className="text-xs font-bold text-slate-200 leading-tight flex items-center gap-1.5">
                  <span>{userName}</span>
                  {authProvider === 'google' && (
                    <svg className="w-3 h-3 shrink-0" viewBox="0 0 24 24" title="Google Verified">
                      <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
                      <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
                      <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z" />
                      <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z" />
                    </svg>
                  )}
                </div>
                <div className="text-[10px] text-[#22c55e] font-mono leading-tight flex items-center gap-1">
                  <ShieldCheck className="w-2.5 h-2.5 inline" />
                  <span>{authProvider === 'google' ? 'Google Verified' : 'Safety Officer'}</span>
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
