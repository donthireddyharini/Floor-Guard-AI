import React, { useState } from 'react';
import {
  ShieldAlert,
  LogIn,
  Lock,
  CheckCircle2,
  AlertTriangle,
  Eye,
  Video,
  Database,
  Sparkles,
  ArrowRight,
  UserCheck,
  Activity,
  Award,
  ShieldCheck,
  Flame,
  Droplets,
  Zap,
  Box,
  Layers,
  KeyRound,
  ExternalLink
} from 'lucide-react';
import { NavSection } from '../types';

interface HomeViewProps {
  isAuthenticated: boolean;
  onLogin: (role?: string) => void;
  onSignOut: () => void;
  onNavigate: (section: NavSection) => void;
  onOpenModelDetails?: () => void;
}

export const HomeView: React.FC<HomeViewProps> = ({
  isAuthenticated,
  onLogin,
  onSignOut,
  onNavigate,
  onOpenModelDetails
}) => {
  const [email, setEmail] = useState('safety.officer@floorguard.ai');
  const [password, setPassword] = useState('••••••••••••');
  const [selectedRole, setSelectedRole] = useState('Senior Facility Safety Officer');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [loginMessage, setLoginMessage] = useState<string | null>(null);

  const roles = [
    { id: 'safety_officer', label: 'Senior Facility Safety Officer', badge: 'Full Access' },
    { id: 'facility_manager', label: 'Operations & Facility Manager', badge: 'Admin' },
    { id: 'custodial_lead', label: 'Custodial & Dispatch Lead', badge: 'Auditor' }
  ];

  const hazardClasses = [
    { name: 'Water Spill', color: '#38bdf8', icon: Droplets, risk: 'High' },
    { name: 'Oil Spill', color: '#f59e0b', icon: Flame, risk: 'Critical' },
    { name: 'Chemical Spill', color: '#10b981', icon: Activity, risk: 'Critical' },
    { name: 'Broken Glass', color: '#ef4444', icon: Zap, risk: 'Critical' },
    { name: 'Cable / Cord', color: '#fb923c', icon: Activity, risk: 'High' },
    { name: 'Obstacle / Debris', color: '#a855f7', icon: Box, risk: 'Medium' },
    { name: 'Trash / Litter', color: '#eab308', icon: Box, risk: 'Medium' },
    { name: 'Food Waste', color: '#f97316', icon: Activity, risk: 'Medium' },
    { name: 'Mud / Dirt', color: '#d97706', icon: Activity, risk: 'Medium' },
    { name: 'Stairs Hazard', color: '#ec4899', icon: AlertTriangle, risk: 'Critical' },
    { name: 'Floor Mat Hazard', color: '#6366f1', icon: Layers, risk: 'High' },
    { name: 'Floor Damage', color: '#ef4444', icon: AlertTriangle, risk: 'Critical' },
    { name: 'Clean Floor', color: '#22c55e', icon: CheckCircle2, risk: 'Safe' }
  ];

  const handleFormSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setLoginMessage('Authenticating with Floor Guard Security Node...');

    setTimeout(() => {
      setIsSubmitting(false);
      onLogin(selectedRole);
    }, 450);
  };

  const handleQuickDemoLogin = () => {
    setIsSubmitting(true);
    setLoginMessage('Granting Instant Platform Access...');
    setTimeout(() => {
      setIsSubmitting(false);
      onLogin('Facility Safety Auditor');
    }, 300);
  };

  return (
    <div className="p-6 md:p-8 space-y-8 max-w-[1600px] mx-auto animate-fade-in">
      {/* Top Hero Section */}
      <div className="relative rounded-3xl overflow-hidden bg-gradient-to-br from-[#0e1726] via-[#101b2d] to-[#0a121e] border border-[#1e2d42] p-8 md:p-12 shadow-2xl">
        {/* Ambient Glow */}
        <div className="absolute top-0 right-1/4 w-96 h-96 bg-[#22c55e]/10 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute bottom-0 right-0 w-80 h-80 bg-[#38bdf8]/10 rounded-full blur-3xl pointer-events-none" />

        <div className="relative z-10 grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
          {/* Left Column: Platform Intro Text (7 cols) */}
          <div className="lg:col-span-7 space-y-5">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#152a22] border border-[#22c55e]/40 text-[#22c55e] text-xs font-semibold">
              <Sparkles className="w-3.5 h-3.5 animate-pulse" />
              <span>Autonomous Facility Safety &amp; Hazard Inspection Platform</span>
            </div>

            <h1 className="text-3xl md:text-5xl font-black text-white tracking-tight leading-tight">
              Floor Guard <span className="text-[#22c55e]">AI</span>
            </h1>

            <p className="text-slate-300 text-sm md:text-base leading-relaxed max-w-2xl">
              Next-generation deep learning computer vision system powered by fine-tuned <strong>YOLOv8</strong>. 
              Engineered to detect, localize, and classify 13 real-world indoor floor hazards—from invisible water puddles 
              and toxic chemical spills to loose cables and broken glass—while certifying verified clean floor surfaces in real time.
            </p>

            {/* Quick Metrics Bar */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-2">
              <div className="p-3 rounded-xl bg-[#090e17]/80 border border-[#1b2738]">
                <div className="text-[10px] text-slate-400 font-mono">Classes Active</div>
                <div className="text-xl font-bold text-white font-mono">13 Canonical</div>
                <div className="text-[10px] text-[#22c55e]">12 Hazards + 1 Safe</div>
              </div>
              <div className="p-3 rounded-xl bg-[#090e17]/80 border border-[#1b2738]">
                <div className="text-[10px] text-slate-400 font-mono">Inference Speed</div>
                <div className="text-xl font-bold text-white font-mono">14.8 ms</div>
                <div className="text-[10px] text-[#38bdf8]">67.5 FPS Real-Time</div>
              </div>
              <div className="p-3 rounded-xl bg-[#090e17]/80 border border-[#1b2738]">
                <div className="text-[10px] text-slate-400 font-mono">Curated Dataset</div>
                <div className="text-xl font-bold text-white font-mono">141 Images</div>
                <div className="text-[10px] text-amber-400">160 Verified Boxes</div>
              </div>
              <div className="p-3 rounded-xl bg-[#090e17]/80 border border-[#1b2738]">
                <div className="text-[10px] text-slate-400 font-mono">Negative Control</div>
                <div className="text-xl font-bold text-white font-mono">98% Conf</div>
                <div className="text-[10px] text-[#22c55e]">Clean Floor Certified</div>
              </div>
            </div>

            {/* If Authenticated: Direct Access Pill */}
            {isAuthenticated ? (
              <div className="p-4 rounded-2xl bg-[#14291f] border border-[#22c55e]/50 flex flex-wrap items-center justify-between gap-3">
                <div className="flex items-center gap-2.5">
                  <div className="w-8 h-8 rounded-full bg-[#22c55e]/20 flex items-center justify-center text-[#22c55e]">
                    <ShieldCheck className="w-5 h-5" />
                  </div>
                  <div>
                    <div className="text-xs font-bold text-white">Active Session Authenticated</div>
                    <div className="text-[11px] text-slate-300">You have verified operator credentials.</div>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => onNavigate('overview')}
                    className="flex items-center gap-1.5 px-4 py-2 bg-[#22c55e] hover:bg-[#16a34a] text-black font-bold text-xs rounded-xl shadow-lg transition-colors cursor-pointer"
                  >
                    <span>Enter Overview Dashboard</span>
                    <ArrowRight className="w-3.5 h-3.5 stroke-[2.5]" />
                  </button>
                  <button
                    onClick={onSignOut}
                    className="px-3 py-2 bg-[#1b2638] hover:bg-[#25344d] text-slate-300 text-xs font-semibold rounded-xl border border-[#293c56] transition-colors cursor-pointer"
                  >
                    Sign Out
                  </button>
                </div>
              </div>
            ) : (
              <div className="flex items-center gap-3 pt-1">
                <button
                  onClick={handleQuickDemoLogin}
                  disabled={isSubmitting}
                  className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-[#22c55e] hover:bg-[#16a34a] text-black font-extrabold text-xs shadow-lg shadow-green-950/40 transition-all cursor-pointer disabled:opacity-50"
                >
                  <LogIn className="w-4 h-4 stroke-[2.5]" />
                  <span>{isSubmitting ? 'Accessing Platform...' : 'Instant Demo Sign In'}</span>
                </button>
                <button
                  onClick={() => onNavigate('overview')}
                  className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-[#141d2c] hover:bg-[#1a2638] text-slate-200 font-semibold text-xs border border-[#23334c] transition-colors cursor-pointer"
                >
                  <span>Explore as Guest</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>
              </div>
            )}
          </div>

          {/* Right Column: Interactive Login Portal (5 cols) */}
          <div className="lg:col-span-5">
            <div className="p-6 md:p-7 rounded-2xl bg-[#0d1420]/95 border border-[#202e44] shadow-xl backdrop-blur-md space-y-5">
              <div className="flex items-center justify-between pb-3 border-b border-[#1b283b]">
                <div className="flex items-center gap-2.5">
                  <div className="w-8 h-8 rounded-lg bg-[#14231b] border border-[#22c55e]/40 flex items-center justify-center text-[#22c55e]">
                    <Lock className="w-4 h-4" />
                  </div>
                  <div>
                    <h2 className="text-sm font-bold text-white tracking-tight">Facility Access Portal</h2>
                    <p className="text-[11px] text-slate-400">Sign in to unlock Floor Guard Dashboard</p>
                  </div>
                </div>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                  {isAuthenticated ? 'Authenticated' : 'Login Required'}
                </span>
              </div>

              {loginMessage && (
                <div className="p-2.5 rounded-xl bg-[#14291f] border border-[#22c55e]/40 text-[#22c55e] text-xs font-mono flex items-center gap-2 animate-pulse">
                  <CheckCircle2 className="w-4 h-4 shrink-0" />
                  <span>{loginMessage}</span>
                </div>
              )}

              {/* Login Form */}
              <form onSubmit={handleFormSubmit} className="space-y-4 text-left">
                {/* Role Selector */}
                <div>
                  <label className="block text-[11px] font-semibold text-slate-300 mb-1.5">
                    Authorized Inspection Role
                  </label>
                  <div className="grid grid-cols-1 gap-1.5">
                    {roles.map((r) => (
                      <button
                        type="button"
                        key={r.id}
                        onClick={() => setSelectedRole(r.label)}
                        className={`px-3 py-2 rounded-xl text-xs font-medium flex items-center justify-between border transition-all cursor-pointer ${
                          selectedRole === r.label
                            ? 'bg-[#152a22] border-[#22c55e] text-white shadow-sm'
                            : 'bg-[#121a28] border-[#1d293d] text-slate-400 hover:text-slate-200'
                        }`}
                      >
                        <div className="flex items-center gap-2">
                          <UserCheck className={`w-3.5 h-3.5 ${selectedRole === r.label ? 'text-[#22c55e]' : 'text-slate-500'}`} />
                          <span>{r.label}</span>
                        </div>
                        <span className="text-[10px] font-mono text-slate-400">{r.badge}</span>
                      </button>
                    ))}
                  </div>
                </div>

                {/* Email Address */}
                <div>
                  <label className="block text-[11px] font-semibold text-slate-300 mb-1">
                    Operator Email
                  </label>
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                    className="w-full px-3.5 py-2 rounded-xl bg-[#111927] border border-[#1e2c40] text-white text-xs font-mono focus:outline-none focus:border-[#22c55e] transition-colors"
                    placeholder="operator@floorguard.ai"
                  />
                </div>

                {/* Password */}
                <div>
                  <label className="block text-[11px] font-semibold text-slate-300 mb-1">
                    Security Key / Password
                  </label>
                  <input
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                    className="w-full px-3.5 py-2 rounded-xl bg-[#111927] border border-[#1e2c40] text-white text-xs font-mono focus:outline-none focus:border-[#22c55e] transition-colors"
                    placeholder="••••••••••••"
                  />
                </div>

                {/* Action Buttons */}
                <div className="pt-2 space-y-2">
                  <button
                    type="submit"
                    disabled={isSubmitting}
                    className="w-full flex items-center justify-center gap-2 py-2.5 rounded-xl bg-[#22c55e] hover:bg-[#16a34a] text-black font-extrabold text-xs shadow-lg shadow-green-950/40 transition-all cursor-pointer disabled:opacity-50"
                  >
                    <KeyRound className="w-3.5 h-3.5 stroke-[2.5]" />
                    <span>{isSubmitting ? 'Verifying Credentials...' : 'Sign In & Enter Dashboard'}</span>
                  </button>

                  <button
                    type="button"
                    onClick={handleQuickDemoLogin}
                    disabled={isSubmitting}
                    className="w-full py-2 rounded-xl bg-[#162132] hover:bg-[#1d2c42] border border-[#23354e] text-slate-300 text-xs font-semibold transition-colors cursor-pointer"
                  >
                    One-Click Demo Access
                  </button>
                </div>
              </form>

              <div className="pt-2 border-t border-[#1b283b] flex items-center justify-between text-[10px] text-slate-400 font-mono">
                <span>Floor Guard OS v8.0.0</span>
                <span>Protected by YOLOv8s</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* 13 Canonical Floor Hazard Categories Grid */}
      <div className="space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <div>
            <h2 className="text-base font-bold text-white tracking-tight flex items-center gap-2">
              <span>13 Canonical Floor Hazard Categories</span>
              <span className="text-[10px] px-2 py-0.5 rounded bg-[#152a22] text-[#22c55e] border border-[#22c55e]/30 font-mono font-semibold">
                Universal Classifier Active
              </span>
            </h2>
            <p className="text-xs text-slate-400">
              Fine-tuned computer vision detector distinguishing multi-hazard fluids, solids, obstructions, and certified clean floors
            </p>
          </div>
          <button
            onClick={() => onNavigate('image_detection')}
            className="flex items-center gap-1.5 text-xs text-[#22c55e] hover:underline font-semibold cursor-pointer"
          >
            <span>Open Detection Workspace</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-7 gap-2.5">
          {hazardClasses.map((h, idx) => {
            const Icon = h.icon;
            return (
              <div
                key={idx}
                className="p-3 rounded-xl bg-[#0f1623] border border-[#1b2638] hover:border-[#2a3c56] transition-all space-y-1.5"
              >
                <div className="flex items-center justify-between">
                  <div
                    className="w-6 h-6 rounded-md flex items-center justify-center text-white"
                    style={{ backgroundColor: `${h.color}25`, color: h.color }}
                  >
                    <Icon className="w-3.5 h-3.5" />
                  </div>
                  <span
                    className={`text-[9px] font-bold px-1.5 py-0.2 rounded font-mono ${
                      h.risk === 'Safe'
                        ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                        : h.risk === 'Critical'
                          ? 'bg-red-500/20 text-red-400 border border-red-500/30'
                          : h.risk === 'High'
                            ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
                            : 'bg-purple-500/20 text-purple-400 border border-purple-500/30'
                    }`}
                  >
                    {h.risk}
                  </span>
                </div>
                <div className="text-xs font-bold text-white truncate">{h.name}</div>
                <div className="text-[10px] text-slate-400 font-mono">Class {idx}</div>
              </div>
            );
          })}
        </div>
      </div>

      {/* 3 Core System Architecture Pillars */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        {/* Pillar 1: Image Detection Studio */}
        <div className="p-6 rounded-2xl bg-[#0e1624] border border-[#1c2a3f] space-y-3 hover:border-[#22c55e]/40 transition-all">
          <div className="w-10 h-10 rounded-xl bg-[#14291f] border border-[#22c55e]/40 flex items-center justify-center text-[#22c55e]">
            <Eye className="w-5 h-5 stroke-[2.2]" />
          </div>
          <h3 className="text-sm font-bold text-white">Manual Image Detection Studio</h3>
          <p className="text-xs text-slate-400 leading-relaxed">
            Upload custom CCTV or smartphone floor photos to run pixel-level YOLOv8 inference. Localizes hazards with calibrated bounding boxes and computes slip/fall risk scores.
          </p>
          <button
            onClick={() => onNavigate('image_detection')}
            className="flex items-center gap-1.5 text-xs text-[#22c55e] font-semibold hover:underline pt-1 cursor-pointer"
          >
            <span>Launch Studio</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>

        {/* Pillar 2: 30s Video Patrol */}
        <div className="p-6 rounded-2xl bg-[#0e1624] border border-[#1c2a3f] space-y-3 hover:border-[#38bdf8]/40 transition-all">
          <div className="w-10 h-10 rounded-xl bg-[#102436] border border-[#38bdf8]/40 flex items-center justify-center text-[#38bdf8]">
            <Video className="w-5 h-5 stroke-[2.2]" />
          </div>
          <h3 className="text-sm font-bold text-white">30s Video Patrol Pipeline</h3>
          <p className="text-xs text-slate-400 leading-relaxed">
            Frame-by-frame autonomous inspection for continuous mobile camera and security feeds. Extracts calibrated keyframes, incident timelines, and safety dispatch orders.
          </p>
          <button
            onClick={() => onNavigate('video_analysis')}
            className="flex items-center gap-1.5 text-xs text-[#38bdf8] font-semibold hover:underline pt-1 cursor-pointer"
          >
            <span>Run Video Patrol</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>

        {/* Pillar 3: Dataset & Training Provenance */}
        <div className="p-6 rounded-2xl bg-[#0e1624] border border-[#1c2a3f] space-y-3 hover:border-amber-500/40 transition-all">
          <div className="w-10 h-10 rounded-xl bg-[#2b2014] border border-amber-500/40 flex items-center justify-center text-amber-400">
            <Database className="w-5 h-5 stroke-[2.2]" />
          </div>
          <h3 className="text-sm font-bold text-white">Curated Training &amp; Audit Logs</h3>
          <p className="text-xs text-slate-400 leading-relaxed">
            Consolidated 141-image indoor floor hazard dataset with 160 ground-truth annotations across 12 epochs. Complete historical audit logs with evidence captures.
          </p>
          <button
            onClick={() => onNavigate('dataset_training')}
            className="flex items-center gap-1.5 text-xs text-amber-400 font-semibold hover:underline pt-1 cursor-pointer"
          >
            <span>Inspect Dataset</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>
    </div>
  );
};
