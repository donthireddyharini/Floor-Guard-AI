import React from 'react';
import {
  Home,
  LayoutDashboard,
  Image as ImageIcon,
  Video,
  Database,
  History,
  TrendingUp,
  Settings,
  ShieldAlert,
  Cpu,
  ArrowRight,
  Lock,
  Unlock,
  LogOut
} from 'lucide-react';
import { NavSection } from '../types';

interface SidebarProps {
  activeSection: NavSection;
  onSelectSection: (section: NavSection) => void;
  onOpenModelDetails: () => void;
  activeModel?: any;
  isAuthenticated?: boolean;
  onSignOut?: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  activeSection,
  onSelectSection,
  onOpenModelDetails,
  activeModel,
  isAuthenticated = false,
  onSignOut
}) => {
  const navItems = [
    { id: 'home' as NavSection, label: 'Home / Intro', icon: Home, isPublic: true },
    { id: 'overview' as NavSection, label: 'Overview', icon: LayoutDashboard },
    { id: 'image_detection' as NavSection, label: 'Image Detection', icon: ImageIcon },
    { id: 'video_analysis' as NavSection, label: 'Video Analysis', icon: Video },
    { id: 'dataset_training' as NavSection, label: 'Dataset & Training', icon: Database },
    { id: 'hazard_history' as NavSection, label: 'Hazard History', icon: History },
    { id: 'analytics' as NavSection, label: 'Analytics', icon: TrendingUp },
    { id: 'settings' as NavSection, label: 'Settings', icon: Settings },
  ];

  return (
    <aside className="w-64 bg-[#0c121d] border-r border-[#1e293b] flex flex-col justify-between shrink-0 select-none h-screen sticky top-0">
      {/* Brand Header */}
      <div>
        <div 
          onClick={() => onSelectSection('home')} 
          className="p-5 flex items-center gap-3 border-b border-[#182335] cursor-pointer hover:bg-[#111a28] transition-colors"
          title="Floor Guard AI Home"
        >
          <div className="w-10 h-10 rounded-xl bg-[#14231b] border border-[#22c55e]/40 flex items-center justify-center text-[#22c55e] shadow-[0_0_15px_rgba(34,197,94,0.2)]">
            <ShieldAlert className="w-6 h-6 stroke-[2.2]" />
          </div>
          <div>
            <h1 className="text-base font-bold text-white tracking-tight flex items-center gap-1.5">
              Floor Guard <span className="text-[#22c55e]">AI</span>
            </h1>
            <p className="text-[11px] text-slate-400 font-medium">Floor Hazard Detection</p>
          </div>
        </div>

        {/* Navigation Items */}
        <nav className="p-3 space-y-1.5 mt-2">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeSection === item.id;
            const isLocked = !item.isPublic && !isAuthenticated;

            return (
              <button
                key={item.id}
                onClick={() => {
                  if (isLocked) {
                    onSelectSection('home');
                  } else {
                    onSelectSection(item.id);
                  }
                }}
                className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl text-xs font-semibold transition-all duration-200 text-left ${
                  isActive
                    ? 'bg-[#15803d] text-white shadow-lg shadow-green-950/40 font-bold'
                    : isLocked
                      ? 'text-slate-500 hover:text-slate-300 hover:bg-[#121926] opacity-75'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-[#141d2c]'
                }`}
                title={isLocked ? 'Login required to access this section' : item.label}
              >
                <div className="flex items-center gap-3.5">
                  <Icon
                    className={`w-4 h-4 ${
                      isActive ? 'text-white' : isLocked ? 'text-slate-500' : 'text-slate-400 group-hover:text-slate-200'
                    }`}
                  />
                  <span>{item.label}</span>
                </div>
                {isLocked ? (
                  <Lock className="w-3.5 h-3.5 text-amber-500/70" />
                ) : item.id === 'home' && (
                  <span className="text-[9px] font-mono px-1.5 py-0.2 rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                    Intro
                  </span>
                )}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Bottom Area: User Session & Model Card */}
      <div className="p-3 m-3 space-y-2.5">
        {/* Session Status Pill */}
        <div className="p-2.5 rounded-xl bg-[#101724] border border-[#1c283a] flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className={`w-2 h-2 rounded-full ${isAuthenticated ? 'bg-[#22c55e] shadow-[0_0_8px_#22c55e]' : 'bg-amber-400 shadow-[0_0_8px_#fbbf24]'}`} />
            <div className="text-[11px] font-semibold text-slate-300">
              {isAuthenticated ? 'Operator Logged In' : 'Guest / Locked'}
            </div>
          </div>
          {isAuthenticated && onSignOut && (
            <button
              onClick={onSignOut}
              className="text-[10px] text-slate-400 hover:text-red-400 flex items-center gap-1 transition-colors"
              title="Sign Out"
            >
              <LogOut className="w-3 h-3" />
              <span>Exit</span>
            </button>
          )}
        </div>

        {/* Model Card */}
        <div className="p-3 rounded-2xl bg-[#131b29] border border-[#1e2c3f]">
          <div className="flex items-center gap-2.5 mb-2">
            <div className="w-8 h-8 rounded-xl bg-[#173024] border border-[#22c55e]/40 flex items-center justify-center text-[#22c55e]">
              <Cpu className="w-4 h-4" />
            </div>
            <div>
              <div className="text-xs font-semibold text-slate-200">AI Model</div>
              <div className="text-[11px] font-bold text-[#22c55e] flex items-center gap-1">
                Trained &amp; Ready
              </div>
            </div>
          </div>
          <div className="text-[11px] text-slate-400 space-y-0.5 mb-2.5 font-mono">
            <div>Version {activeModel?.version || 'v8.0.0-canonical-13class'}</div>
            <div className="text-[10px] text-slate-500">Status</div>
            <div className="text-[10px] text-[#22c55e] font-bold">12 Hazards + Clean Floor</div>
          </div>
          <button
            onClick={onOpenModelDetails}
            className="w-full flex items-center justify-center gap-1.5 py-1.5 text-[11px] font-semibold text-slate-300 hover:text-white bg-[#192437] hover:bg-[#202e46] border border-[#26374f] rounded-lg transition-colors cursor-pointer"
          >
            <span>View Model Details</span>
            <ArrowRight className="w-3 h-3 text-[#22c55e]" />
          </button>
        </div>
      </div>
    </aside>
  );
};
