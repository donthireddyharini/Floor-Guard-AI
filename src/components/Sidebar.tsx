import React from 'react';
import {
  LayoutDashboard,
  ScanEye,
  Video,
  History,
  BarChart3,
  FlaskConical,
  Settings,
  ShieldAlert,
  Cpu,
  ArrowRight,
  Sparkles
} from 'lucide-react';
import { NavSection, ModelItem } from '../types';

interface SidebarProps {
  activeSection: NavSection;
  onSelectSection: (section: NavSection) => void;
  activeModel?: ModelItem;
}

export const Sidebar: React.FC<SidebarProps> = ({
  activeSection,
  onSelectSection,
  activeModel
}) => {
  const navItems = [
    { id: 'overview' as NavSection, label: 'Overview', icon: LayoutDashboard },
    { id: 'image_detection' as NavSection, label: 'Image Inspection', icon: ScanEye },
    { id: 'video_analysis' as NavSection, label: 'Video Analysis', icon: Video },
    { id: 'hazard_history' as NavSection, label: 'Detection History', icon: History },
    { id: 'analytics' as NavSection, label: 'Analytics & Reports', icon: BarChart3 },
    { id: 'ai_model_lab' as NavSection, label: 'AI Model Lab', icon: FlaskConical },
    { id: 'settings' as NavSection, label: 'Settings', icon: Settings },
  ];

  const isCustom = activeModel?.id?.includes('floorguard') || false;

  return (
    <aside className="w-64 bg-[#0a0f1d] border-r border-[#1e293d] flex flex-col justify-between shrink-0 select-none h-screen sticky top-0 z-30">
      {/* Brand Header */}
      <div>
        <div className="p-5 flex items-center gap-3 border-b border-[#182335]">
          <div className="w-10 h-10 rounded-xl bg-[#1e130a] border border-[#f97316]/40 flex items-center justify-center text-[#f97316] shadow-[0_0_15px_rgba(249,115,22,0.25)]">
            <ShieldAlert className="w-6 h-6 stroke-[2.2]" />
          </div>
          <div>
            <h1 className="text-base font-bold text-white tracking-tight flex items-center gap-1.5 font-mono">
              Floor Guard <span className="text-[#f97316]">AI</span>
            </h1>
            <p className="text-[10px] text-slate-400 font-medium uppercase tracking-wider">Industrial Hazard Vision</p>
          </div>
        </div>

        {/* Navigation Items */}
        <nav className="p-3 space-y-1.5 mt-2">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeSection === item.id;
            return (
              <button
                key={item.id}
                onClick={() => onSelectSection(item.id)}
                className={`w-full flex items-center gap-3.5 px-3.5 py-2.5 rounded-xl text-xs font-semibold transition-all duration-200 text-left cursor-pointer ${
                  isActive
                    ? 'bg-[#ea580c] text-white shadow-lg shadow-orange-950/40 font-bold border border-[#f97316]/50'
                    : 'text-slate-400 hover:text-slate-100 hover:bg-[#131d2e] border border-transparent'
                }`}
              >
                <Icon
                  className={`w-4 h-4 shrink-0 ${
                    isActive ? 'text-white' : 'text-slate-400'
                  }`}
                />
                <span className="truncate">{item.label}</span>
                {item.id === 'ai_model_lab' && (
                  <span className="ml-auto text-[9px] px-1.5 py-0.5 rounded bg-orange-500/20 text-orange-400 font-mono border border-orange-500/30">
                    LAB
                  </span>
                )}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Bottom Model Card */}
      <div className="p-3.5 m-3 rounded-2xl bg-[#111827] border border-[#1f293d] space-y-2.5">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-[#1e130a] border border-[#f97316]/40 flex items-center justify-center text-[#f97316]">
            <Cpu className="w-4 h-4" />
          </div>
          <div className="min-w-0">
            <div className="text-[11px] font-semibold text-slate-200 truncate">
              {activeModel?.name || 'YOLOv8s Baseline'}
            </div>
            <div className="text-[10px] font-mono text-[#f97316] flex items-center gap-1">
              <span className="w-1.5 h-1.5 rounded-full bg-[#f97316] animate-pulse" />
              {isCustom ? 'Experimental Detector' : 'Production Baseline'}
            </div>
          </div>
        </div>

        <div className="text-[10px] text-slate-400 space-y-0.5 font-mono bg-[#0a0f1d] p-2 rounded-lg border border-[#1e293d]">
          <div className="flex justify-between">
            <span className="text-slate-500">Classes:</span>
            <span className="text-slate-300">{isCustom ? '4 Hazards' : '80 COCO'}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-500">Device:</span>
            <span className="text-slate-300">Intel i5 (CPU)</span>
          </div>
        </div>

        <button
          onClick={() => onSelectSection('ai_model_lab')}
          className="w-full flex items-center justify-center gap-1.5 py-2 text-[11px] font-semibold text-slate-300 hover:text-white bg-[#1a2333] hover:bg-[#222f46] border border-[#2a384f] rounded-lg transition-colors cursor-pointer"
        >
          <span>Open AI Model Lab</span>
          <ArrowRight className="w-3.5 h-3.5 text-[#f97316]" />
        </button>
      </div>
    </aside>
  );
};
