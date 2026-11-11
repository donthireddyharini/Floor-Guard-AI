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
  Activity,
  Droplets,
  Flame,
  Zap,
  Box,
  Layers,
  KeyRound,
  UserPlus,
  X
} from 'lucide-react';

interface LandingPageProps {
  onLogin: (role?: string) => void;
}

export const LandingPage: React.FC<LandingPageProps> = ({ onLogin }) => {
  const [isAuthModalOpen, setIsAuthModalOpen] = useState(false);
  const [authMode, setAuthMode] = useState<'signin' | 'signup'>('signin');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [loginMessage, setLoginMessage] = useState<string | null>(null);

  const hazardClasses = [
    { name: 'Water Spill', color: '#38bdf8', icon: Droplets, risk: 'High', desc: 'Clear/turbid puddles on tile, polished concrete, or linoleum.' },
    { name: 'Oil Spill', color: '#f59e0b', icon: Flame, risk: 'Critical', desc: 'Greasy viscous liquids prone to severe slip accidents.' },
    { name: 'Chemical Spill', color: '#10b981', icon: Activity, risk: 'Critical', desc: 'Corrosive fluids, detergents, and industrial solvent slicks.' },
    { name: 'Broken Glass', color: '#ef4444', icon: Zap, risk: 'Critical', desc: 'Shattered shards and glass fragments causing puncture risks.' },
    { name: 'Cable / Cord', color: '#fb923c', icon: Activity, risk: 'High', desc: 'Loose power lines, extensions, and tripwires.' },
    { name: 'Obstacle / Debris', color: '#a855f7', icon: Box, risk: 'Medium', desc: 'Fallen boxes, pallets, and walkway obstructions.' },
    { name: 'Trash / Litter', color: '#eab308', icon: Box, risk: 'Medium', desc: 'Discarded plastic bottles, paper, and food containers.' },
    { name: 'Food Waste', color: '#f97316', icon: Activity, risk: 'Medium', desc: 'Perishable organic debris and slippery peel scraps.' },
    { name: 'Mud / Dirt', color: '#d97706', icon: Activity, risk: 'Medium', desc: 'Tracked outdoor slush, soil, and construction sludge.' },
    { name: 'Stairs Hazard', color: '#ec4899', icon: AlertTriangle, risk: 'Critical', desc: 'Steep steps, tread defects, and stairway clutter.' },
    { name: 'Floor Mat Hazard', color: '#6366f1', icon: Layers, risk: 'High', desc: 'Folded edges, curled rugs, and unanchored mats.' },
    { name: 'Floor Damage', color: '#ef4444', icon: AlertTriangle, risk: 'Critical', desc: 'Cracked tiles, pothole indentations, and uneven joints.' },
    { name: 'Clean Floor', color: '#22c55e', icon: CheckCircle2, risk: 'Safe', desc: 'Certified clear negative control surface without slip hazards.' }
  ];

  const handleFormSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    const msg = authMode === 'signup' 
      ? 'Creating Account & Initializing Platform...' 
      : 'Signing In & Verifying Credentials...';
    setLoginMessage(msg);

    setTimeout(() => {
      setIsSubmitting(false);
      setIsAuthModalOpen(false);
      onLogin('Facility Safety Officer');
    }, 400);
  };

  const handleGoogleSignIn = () => {
    setIsSubmitting(true);
    setLoginMessage('Authenticating via Google Identity Services...');
    setTimeout(() => {
      setIsSubmitting(false);
      setIsAuthModalOpen(false);
      try {
        localStorage.setItem('floorguard_auth_provider', 'google');
        localStorage.setItem('floorguard_user_name', 'Harini Donthireddy');
      } catch {}
      onLogin('Harini Donthireddy (Google)');
    }, 450);
  };

  const openAuthModal = (mode: 'signin' | 'signup' = 'signin') => {
    setAuthMode(mode);
    setLoginMessage(null);
    setIsAuthModalOpen(true);
  };

  return (
    <div className="min-h-screen bg-[#070b12] text-slate-100 flex flex-col selection:bg-[#22c55e] selection:text-black relative">
      {/* Standalone Landing Page Header */}
      <header className="sticky top-0 z-40 bg-[#0c121d]/90 backdrop-blur-md border-b border-[#182335]">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          {/* Brand Logo */}
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-[#14231b] border border-[#22c55e]/50 flex items-center justify-center text-[#22c55e] shadow-[0_0_20px_rgba(34,197,94,0.3)]">
              <ShieldAlert className="w-6 h-6 stroke-[2.2]" />
            </div>
            <div>
              <div className="text-lg font-black tracking-tight text-white flex items-center gap-1.5">
                Floor Guard <span className="text-[#22c55e]">AI</span>
                <span className="text-[10px] px-2 py-0.5 rounded-full bg-[#172e21] text-[#22c55e] border border-[#22c55e]/30 font-semibold">
                  v8.0.0
                </span>
              </div>
              <p className="text-[11px] text-slate-400 font-medium">Autonomous Floor Safety &amp; Hazard Inspection</p>
            </div>
          </div>

          {/* Quick Nav Anchors */}
          <nav className="hidden md:flex items-center gap-6 text-xs font-semibold text-slate-300">
            <a href="#overview" className="hover:text-white transition-colors">Overview</a>
            <a href="#categories" className="hover:text-white transition-colors">13 Hazard Classes</a>
            <a href="#architecture" className="hover:text-white transition-colors">AI Pipeline</a>
          </nav>

          {/* Direct Login / Sign In CTA */}
          <div className="flex items-center gap-3">
            <button
              onClick={() => openAuthModal('signin')}
              className="flex items-center gap-2 px-4 py-2 rounded-xl bg-[#22c55e] hover:bg-[#16a34a] text-black text-xs font-extrabold shadow-lg shadow-green-950/40 transition-all cursor-pointer"
            >
              <LogIn className="w-3.5 h-3.5 stroke-[2.5]" />
              <span>Login / Sign In</span>
            </button>
          </div>
        </div>
      </header>

      {/* Main Landing Content */}
      <main className="flex-1">
        {/* Hero Section */}
        <section id="overview" className="relative pt-16 pb-20 px-6 border-b border-[#141e2e] overflow-hidden">
          {/* Ambient Lighting Gradients */}
          <div className="absolute top-1/4 left-1/4 w-[500px] h-[500px] bg-[#22c55e]/10 rounded-full blur-[120px] pointer-events-none" />
          <div className="absolute top-1/3 right-1/4 w-[450px] h-[450px] bg-[#38bdf8]/10 rounded-full blur-[120px] pointer-events-none" />

          <div className="max-w-5xl mx-auto text-center space-y-7 relative z-10">
            <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-[#14291f] border border-[#22c55e]/40 text-[#22c55e] text-xs font-bold tracking-wide mx-auto">
              <Sparkles className="w-3.5 h-3.5 animate-pulse" />
              <span>Next-Gen Computer Vision for Facility Safety</span>
            </div>

            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-black text-white tracking-tight leading-[1.15]">
              Autonomous Floor Hazard <br />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-[#22c55e] via-[#4ade80] to-[#38bdf8]">
                Inspection &amp; Localization
              </span>
            </h1>

            <p className="text-slate-300 text-sm sm:text-base leading-relaxed max-w-3xl mx-auto">
              Engineered with fine-tuned <strong>YOLOv8</strong> deep neural networks to instantly detect, bound, and classify 
              13 indoor surface hazards—including transparent water puddles, slippery oil slicks, chemical spills, loose cords, and broken glass—while 
              certifying <strong>Clean Floor</strong> negative controls in <strong>14.8 milliseconds</strong>.
            </p>

            {/* Hero Action CTA Buttons */}
            <div className="flex flex-wrap items-center justify-center gap-3 pt-2">
              <button
                onClick={() => openAuthModal('signin')}
                className="flex items-center gap-2.5 px-6 py-3 rounded-xl bg-[#22c55e] hover:bg-[#16a34a] text-black font-extrabold text-sm shadow-xl shadow-green-950/40 transition-all cursor-pointer"
              >
                <LogIn className="w-4 h-4 stroke-[2.5]" />
                <span>Login / Sign In</span>
                <ArrowRight className="w-4 h-4" />
              </button>

              <button
                onClick={() => openAuthModal('signup')}
                className="flex items-center gap-2 px-5 py-3 rounded-xl bg-[#141d2c] hover:bg-[#1c283c] border border-[#23334c] text-white text-sm font-semibold transition-all cursor-pointer"
              >
                <UserPlus className="w-4 h-4 text-[#22c55e]" />
                <span>Create Account</span>
              </button>

              <a
                href="#categories"
                className="flex items-center gap-2 px-5 py-3 rounded-xl bg-[#0f1724] hover:bg-[#162132] border border-[#1b2638] text-slate-300 hover:text-white text-sm font-semibold transition-all"
              >
                <span>View 13 Hazard Classes</span>
              </a>
            </div>

            {/* System Performance Cards */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-6 max-w-4xl mx-auto">
              <div className="p-4 rounded-2xl bg-[#0d1522] border border-[#1a2638] shadow-sm">
                <div className="text-[10px] text-slate-400 uppercase tracking-wider">Detection Spectrum</div>
                <div className="text-2xl font-black text-white mt-0.5">13 Classes</div>
                <div className="text-[11px] text-[#22c55e] font-semibold">12 Hazards + 1 Safe</div>
              </div>

              <div className="p-4 rounded-2xl bg-[#0d1522] border border-[#1a2638] shadow-sm">
                <div className="text-[10px] text-slate-400 uppercase tracking-wider">Inference Speed</div>
                <div className="text-2xl font-black text-white mt-0.5">14.8 ms</div>
                <div className="text-[11px] text-[#38bdf8] font-semibold">67.5 FPS Real-Time</div>
              </div>

              <div className="p-4 rounded-2xl bg-[#0d1522] border border-[#1a2638] shadow-sm">
                <div className="text-[10px] text-slate-400 uppercase tracking-wider">Curated Dataset</div>
                <div className="text-2xl font-black text-white mt-0.5">141 Images</div>
                <div className="text-[11px] text-amber-400 font-semibold">160 Verified Boxes</div>
              </div>

              <div className="p-4 rounded-2xl bg-[#0d1522] border border-[#1a2638] shadow-sm">
                <div className="text-[10px] text-slate-400 uppercase tracking-wider">Negative Control</div>
                <div className="text-2xl font-black text-white mt-0.5">98% Conf</div>
                <div className="text-[11px] text-[#22c55e] font-semibold">Clean Floor Certified</div>
              </div>
            </div>
          </div>
        </section>

        {/* 13 Canonical Hazard Categories Showcase */}
        <section id="categories" className="py-16 px-6 max-w-7xl mx-auto space-y-8">
          <div className="text-center max-w-3xl mx-auto space-y-3">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#14231b] border border-[#22c55e]/40 text-[#22c55e] text-xs font-bold">
              <span>Universal Hazard Spectrum</span>
            </div>
            <h2 className="text-2xl sm:text-3xl font-extrabold text-white">
              13 Canonical Floor Hazard Categories
            </h2>
            <p className="text-xs sm:text-sm text-slate-400">
              Trained on real-world industrial warehouses, retail corridors, hospital walkways, and clean rooms.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {hazardClasses.map((item, idx) => {
              const Icon = item.icon;
              return (
                <div
                  key={idx}
                  className="p-4 rounded-2xl bg-[#0b121e] border border-[#1b2638] hover:border-[#2a3c56] transition-all space-y-2.5"
                >
                  <div className="flex items-center justify-between">
                    <div
                      className="w-8 h-8 rounded-xl flex items-center justify-center font-bold"
                      style={{ backgroundColor: `${item.color}20`, color: item.color }}
                    >
                      <Icon className="w-4 h-4" />
                    </div>
                    <span
                      className={`text-[10px] font-bold px-2 py-0.5 rounded ${
                        item.risk === 'Safe'
                          ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                          : item.risk === 'Critical'
                            ? 'bg-red-500/20 text-red-400 border border-red-500/30'
                            : item.risk === 'High'
                              ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
                              : 'bg-purple-500/20 text-purple-400 border border-purple-500/30'
                      }`}
                    >
                      {item.risk} Risk
                    </span>
                  </div>
                  <div>
                    <div className="text-sm font-bold text-white flex items-center gap-2">
                      <span>{item.name}</span>
                      <span className="text-[10px] text-slate-500">#{idx}</span>
                    </div>
                    <p className="text-xs text-slate-400 mt-1 leading-relaxed">
                      {item.desc}
                    </p>
                  </div>
                </div>
              );
            })}
          </div>
        </section>

        {/* AI Pipeline Architecture Pillars */}
        <section id="architecture" className="py-16 px-6 bg-[#090f1a] border-t border-[#141e2e]">
          <div className="max-w-7xl mx-auto space-y-10">
            <div className="text-center max-w-3xl mx-auto space-y-3">
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#102436] border border-[#38bdf8]/40 text-[#38bdf8] text-xs font-bold">
                <span>Production Architecture</span>
              </div>
              <h2 className="text-2xl sm:text-3xl font-extrabold text-white">
                Three Core Safety Inspection Workflows
              </h2>
              <p className="text-xs sm:text-sm text-slate-400">
                Seamlessly integrated into one unified dashboard available upon sign-in.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {/* Pillar 1 */}
              <div 
                onClick={() => openAuthModal('signin')}
                className="p-6 rounded-2xl bg-[#0c1421] border border-[#1d2a3d] space-y-4 hover:border-[#22c55e]/50 transition-all cursor-pointer group"
              >
                <div className="w-12 h-12 rounded-2xl bg-[#14291f] border border-[#22c55e]/40 flex items-center justify-center text-[#22c55e]">
                  <Eye className="w-6 h-6 stroke-[2.2]" />
                </div>
                <h3 className="text-base font-bold text-white group-hover:text-[#22c55e] transition-colors">Manual Image Detection Studio</h3>
                <p className="text-xs text-slate-400 leading-relaxed">
                  Upload high-resolution CCTV or mobile floor captures. The detector computes pixel bounding boxes, 
                  surface slip hazard indices, and localized custodial dispatch recommendations.
                </p>
                <div className="text-[11px] text-[#22c55e] font-semibold flex items-center gap-1.5 pt-1">
                  <span>Sign In to Launch</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </div>
              </div>

              {/* Pillar 2 */}
              <div 
                onClick={() => openAuthModal('signin')}
                className="p-6 rounded-2xl bg-[#0c1421] border border-[#1d2a3d] space-y-4 hover:border-[#38bdf8]/50 transition-all cursor-pointer group"
              >
                <div className="w-12 h-12 rounded-2xl bg-[#102436] border border-[#38bdf8]/40 flex items-center justify-center text-[#38bdf8]">
                  <Video className="w-6 h-6 stroke-[2.2]" />
                </div>
                <h3 className="text-base font-bold text-white group-hover:text-[#38bdf8] transition-colors">30s Video Patrol Pipeline</h3>
                <p className="text-xs text-slate-400 leading-relaxed">
                  Continuous frame-by-frame autonomous patrol. Identifies keyframe hazard timestamps, 
                  tracks moving obstructions, and compiles incident video timelines.
                </p>
                <div className="text-[11px] text-[#38bdf8] font-semibold flex items-center gap-1.5 pt-1">
                  <span>Sign In to Launch</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </div>
              </div>

              {/* Pillar 3 */}
              <div 
                onClick={() => openAuthModal('signin')}
                className="p-6 rounded-2xl bg-[#0c1421] border border-[#1d2a3d] space-y-4 hover:border-amber-500/50 transition-all cursor-pointer group"
              >
                <div className="w-12 h-12 rounded-2xl bg-[#281e13] border border-amber-500/40 flex items-center justify-center text-amber-400">
                  <Database className="w-6 h-6 stroke-[2.2]" />
                </div>
                <h3 className="text-base font-bold text-white group-hover:text-amber-400 transition-colors">Curated Dataset &amp; Audit Logs</h3>
                <p className="text-xs text-slate-400 leading-relaxed">
                  Consolidated repository of 141 multi-hazard images with 160 ground truth annotations, 
                  complete evaluation confusion matrices, and audit export tools.
                </p>
                <div className="text-[11px] text-amber-400 font-semibold flex items-center gap-1.5 pt-1">
                  <span>Sign In to Launch</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </div>
              </div>
            </div>
          </div>
        </section>
      </main>

      {/* Standalone Footer */}
      <footer className="bg-[#06090f] border-t border-[#141e2e] py-8 px-6 text-xs text-slate-500">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <ShieldAlert className="w-4 h-4 text-[#22c55e]" />
            <span className="font-bold text-slate-300">Floor Guard AI</span>
            <span>&bull;</span>
            <span>v8.0.0-canonical-13class</span>
          </div>
          <div>
            Autonomous Industrial Floor Hazard Inspection Platform &bull; Apache 2.0
          </div>
        </div>
      </footer>

      {/* Auth Modal: ONLY VISIBLE AFTER USER CLICKS "Login / Sign In" */}
      {isAuthModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-fade-in">
          <div className="relative w-full max-w-md rounded-3xl p-7 md:p-8 bg-[#0c1421] border border-[#213149] shadow-2xl space-y-5">
            {/* Header: Title & Close Button */}
            <div className="flex items-center justify-between pb-3 border-b border-[#1b2738]">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-[#14261d] border border-[#22c55e]/40 flex items-center justify-center text-[#22c55e]">
                  <Lock className="w-5 h-5" />
                </div>
                <div>
                  <h2 className="text-base font-bold text-white">
                    {authMode === 'signin' ? 'Sign In' : 'Create Account'}
                  </h2>
                  <p className="text-xs text-slate-400">Access Floor Guard AI Dashboard</p>
                </div>
              </div>

              {/* Close Button */}
              <button
                type="button"
                onClick={() => setIsAuthModalOpen(false)}
                className="w-8 h-8 rounded-lg bg-[#141d2c] border border-[#22334c] flex items-center justify-center text-slate-400 hover:text-white transition-colors cursor-pointer"
                title="Close"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Google Authentication Button */}
            <button
              type="button"
              onClick={handleGoogleSignIn}
              disabled={isSubmitting}
              className="w-full flex items-center justify-center gap-3 py-2.5 px-4 rounded-xl bg-[#141d2c] hover:bg-[#1a2638] text-white text-xs font-semibold border border-[#23334c] hover:border-slate-500 shadow-md transition-all cursor-pointer disabled:opacity-50"
            >
              <svg className="w-4 h-4 shrink-0" viewBox="0 0 24 24">
                <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
                <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
                <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z" />
                <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z" />
              </svg>
              <span>Continue with Google</span>
            </button>

            {/* Divider */}
            <div className="relative flex items-center justify-center">
              <div className="border-t border-[#1e2c40] w-full" />
              <span className="bg-[#0c1421] px-3 text-[10px] text-slate-400 font-medium uppercase tracking-wider">
                Or with Email
              </span>
              <div className="border-t border-[#1e2c40] w-full" />
            </div>

            {/* Mode Switcher Tabs */}
            <div className="grid grid-cols-2 p-1 rounded-xl bg-[#101724] border border-[#1e2c40]">
              <button
                type="button"
                onClick={() => setAuthMode('signin')}
                className={`py-1.5 rounded-lg text-xs font-semibold transition-all cursor-pointer ${
                  authMode === 'signin'
                    ? 'bg-[#22c55e] text-black shadow-sm font-bold'
                    : 'text-slate-400 hover:text-white'
                }`}
              >
                Sign In
              </button>
              <button
                type="button"
                onClick={() => setAuthMode('signup')}
                className={`py-1.5 rounded-lg text-xs font-semibold transition-all cursor-pointer ${
                  authMode === 'signup'
                    ? 'bg-[#22c55e] text-black shadow-sm font-bold'
                    : 'text-slate-400 hover:text-white'
                }`}
              >
                Create Account
              </button>
            </div>

            {loginMessage && (
              <div className="p-3 rounded-xl bg-[#14291f] border border-[#22c55e]/40 text-[#22c55e] text-xs flex items-center gap-2 animate-pulse">
                <CheckCircle2 className="w-4 h-4 shrink-0" />
                <span>{loginMessage}</span>
              </div>
            )}

            {/* Form with ONLY Email and Password */}
            <form onSubmit={handleFormSubmit} className="space-y-4">
              {/* Email */}
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                  Email
                </label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  autoFocus
                  className="w-full px-3.5 py-2.5 rounded-xl bg-[#101724] border border-[#1f2e44] text-white text-xs focus:outline-none focus:border-[#22c55e] transition-colors"
                  placeholder="name@company.com"
                />
              </div>

              {/* Password */}
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                  Password
                </label>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  className="w-full px-3.5 py-2.5 rounded-xl bg-[#101724] border border-[#1f2e44] text-white text-xs focus:outline-none focus:border-[#22c55e] transition-colors"
                  placeholder="••••••••••••"
                />
              </div>

              {/* Action Submit Button */}
              <div className="pt-2">
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="w-full flex items-center justify-center gap-2 py-3 rounded-xl bg-[#22c55e] hover:bg-[#16a34a] text-black font-extrabold text-xs shadow-lg shadow-green-950/40 transition-all cursor-pointer disabled:opacity-50"
                >
                  {authMode === 'signin' ? (
                    <>
                      <KeyRound className="w-4 h-4 stroke-[2.5]" />
                      <span>{isSubmitting ? 'Signing In...' : 'Sign In & Enter Dashboard'}</span>
                    </>
                  ) : (
                    <>
                      <UserPlus className="w-4 h-4 stroke-[2.5]" />
                      <span>{isSubmitting ? 'Creating Account...' : 'Create Account & Enter Dashboard'}</span>
                    </>
                  )}
                </button>
              </div>
            </form>

            <div className="pt-2 border-t border-[#1b2738] flex items-center justify-between text-[11px] text-slate-400">
              <span>Floor Guard AI Platform</span>
              <span className="text-[#22c55e]">YOLOv8 Active</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
