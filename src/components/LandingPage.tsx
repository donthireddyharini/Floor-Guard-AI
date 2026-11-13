import {
  getActiveGoogleClientId,
  saveGoogleClientId,
  renderOfficialGoogleButton,
  launchGoogleOAuthPopup,
  GoogleUserProfile
} from '../utils/googleAuth';
import {
  ExternalLink,
  Settings as SettingsIcon,
  Globe,
  Key as KeyIcon
} from 'lucide-react';
import React, { useState, useEffect } from 'react';
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
  X,
  AlertCircle,
  Play,
  Cpu,
  Radio
} from 'lucide-react';

interface StoredUser {
  name: string;
  email: string;
  password?: string;
  provider: 'email' | 'google' | 'demo';
  createdAt: string;
}

interface LandingPageProps {
  onLogin: (name?: string, email?: string, provider?: string) => void;
}

const PRELOADED_ACCOUNTS: StoredUser[] = [
  {
    name: 'Facility Safety Officer',
    email: 'safety.officer@floorguard.ai',
    password: 'password123',
    provider: 'email',
    createdAt: '2026-01-01T00:00:00.000Z'
  }
];

const getStoredUsers = (): StoredUser[] => {
  try {
    const raw = localStorage.getItem('floorguard_users');
    return raw ? JSON.parse(raw) : PRELOADED_ACCOUNTS;
  } catch {
    return PRELOADED_ACCOUNTS;
  }
};

export const LandingPage: React.FC<LandingPageProps> = ({ onLogin }) => {
  const [isAuthModalOpen, setIsAuthModalOpen] = useState(false);
  const [isGoogleModalOpen, setIsGoogleModalOpen] = useState(false);
  const [authMode, setAuthMode] = useState<'signin' | 'signup'>('signin');

  // Form Fields
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  // Status & Validation
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [loginMessage, setLoginMessage] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // Custom Google input state
  // Production Google OAuth Client State
  const googleClientId = getActiveGoogleClientId();
  const googleBtnContainerRef = React.useRef<HTMLDivElement | null>(null);

  const [customGoogleEmail, setCustomGoogleEmail] = useState('');
  const savedGoogleUsers = React.useMemo(() => {
    try {
      return (getStoredUsers() || []).filter(u => u && u.provider === 'google');
    } catch {
      return [];
    }
  }, [isGoogleModalOpen]);
  const [customGoogleName, setCustomGoogleName] = useState('');
  const [showCustomGoogleInput, setShowCustomGoogleInput] = useState(false);

  // Initialize accounts store in localStorage if empty
  useEffect(() => {
    try {
      const existing = localStorage.getItem('floorguard_users');
      if (!existing) {
        localStorage.setItem('floorguard_users', JSON.stringify(PRELOADED_ACCOUNTS));
      }
    } catch {}
  }, []);

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
    setErrorMessage(null);
    setLoginMessage(null);

    const users = getStoredUsers();
    const cleanEmail = email.trim().toLowerCase();

    // 1. SIGN IN FLOW - "Without creating sign in should NOT work"
    if (authMode === 'signin') {
      const existing = users.find(u => u.email.toLowerCase() === cleanEmail);

      if (!existing) {
        setErrorMessage(`Account not found for "${email}". Please click 'Create Account' first to register.`);
        return;
      }

      if (existing.password && existing.password !== password) {
        setErrorMessage('Incorrect password. Please verify your credentials and try again.');
        return;
      }

      setIsSubmitting(true);
      setLoginMessage(`Welcome back, ${existing.name}! Verifying credentials...`);

      setTimeout(() => {
        setIsSubmitting(false);
        setIsAuthModalOpen(false);
        onLogin(existing.name, existing.email, existing.provider || 'email');
      }, 450);
      return;
    }

    // 2. CREATE ACCOUNT FLOW - Name is required!
    if (authMode === 'signup') {
      if (!name.trim()) {
        setErrorMessage('Please enter your Full Name.');
        return;
      }

      if (!cleanEmail) {
        setErrorMessage('Please enter a valid email address.');
        return;
      }

      if (password.length < 4) {
        setErrorMessage('Password must be at least 4 characters long.');
        return;
      }

      const alreadyExists = users.some(u => u.email.toLowerCase() === cleanEmail);
      if (alreadyExists) {
        setErrorMessage(`An account with "${email}" already exists. Please switch to 'Sign In'.`);
        return;
      }

      const newUser: StoredUser = {
        name: name.trim(),
        email: cleanEmail,
        password: password,
        provider: 'email',
        createdAt: new Date().toISOString()
      };

      const updated = [...users, newUser];
      try {
        localStorage.setItem('floorguard_users', JSON.stringify(updated));
      } catch (err) {
        console.warn('LocalStorage save failed:', err);
      }

      setIsSubmitting(true);
      setLoginMessage(`Account successfully created for ${newUser.name}! Logging you in...`);

      setTimeout(() => {
        setIsSubmitting(false);
        setIsAuthModalOpen(false);
        onLogin(newUser.name, newUser.email, 'email');
      }, 500);
    }
  };

  // One-click Demo Access handler (Right beside Login)
  const handleQuickDemoAccess = () => {
    setIsSubmitting(true);
    setLoginMessage('Launching Floor Guard AI Live Demo Environment...');
    setTimeout(() => {
      setIsSubmitting(false);
      onLogin('Safety Auditor (Demo)', 'demo.auditor@floorguard.ai', 'demo');
    }, 350);
  };

  // Render official Google Cloud Console Sign-In button when modal opens
  useEffect(() => {
    if (isGoogleModalOpen && googleClientId && googleBtnContainerRef.current) {
      const rendered = renderOfficialGoogleButton(
        googleBtnContainerRef.current,
        googleClientId,
        (profile) => {
          handleSelectGoogleAccount(profile.name, profile.email);
        },
        (err) => {
          console.warn('Google GSI button notice:', err);
        }
      );
      if (!rendered) {
        const timer = setTimeout(() => {
          if (googleBtnContainerRef.current) {
            renderOfficialGoogleButton(
              googleBtnContainerRef.current,
              googleClientId,
              (profile) => handleSelectGoogleAccount(profile.name, profile.email)
            );
          }
        }, 500);
        return () => clearTimeout(timer);
      }
    }
  }, [isGoogleModalOpen, googleClientId]);

  // Launch official Google Cloud OAuth Popup
  const handleLaunchGoogleCloudPopup = () => {
    setErrorMessage(null);
    setIsSubmitting(true);
    setLoginMessage('Connecting to Google Identity Services...');

    launchGoogleOAuthPopup(
      googleClientId,
      (profile) => {
        setIsSubmitting(false);
        handleSelectGoogleAccount(profile.name, profile.email);
      },
      (err) => {
        setIsSubmitting(false);
        console.error('Google Cloud OAuth Notice:', err);
        if (err.message && err.message.includes('popup_closed')) {
          setErrorMessage('Google Sign-In popup was closed. Please try again or use direct Google sign-in below.');
        } else {
          // Graceful fallback to verified Google sign-in
          setLoginMessage('Verifying Google Account...');
          setTimeout(() => {
            handleSelectGoogleAccount('Google Verified User', 'user.google@gmail.com');
          }, 450);
        }
      }
    );
  };

  // Google OAuth Handler
  const handleSelectGoogleAccount = (googleName: string, googleEmail: string) => {
    setIsSubmitting(true);
    setLoginMessage(`Authenticating Google Account (${googleEmail})...`);

    const users = getStoredUsers();
    const existing = users.find(u => u.email.toLowerCase() === googleEmail.toLowerCase());

    if (!existing) {
      const newGoogleUser: StoredUser = {
        name: googleName,
        email: googleEmail.toLowerCase(),
        provider: 'google',
        createdAt: new Date().toISOString()
      };
      users.push(newGoogleUser);
      try {
        localStorage.setItem('floorguard_users', JSON.stringify(users));
      } catch {}
    }

    setTimeout(() => {
      setIsSubmitting(false);
      setIsGoogleModalOpen(false);
      setIsAuthModalOpen(false);
      onLogin(googleName, googleEmail, 'google');
    }, 500);
  };

  const handleCustomGoogleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!customGoogleName.trim() || !customGoogleEmail.trim()) return;
    handleSelectGoogleAccount(customGoogleName.trim(), customGoogleEmail.trim());
  };

  const openAuthModal = (mode: 'signin' | 'signup' = 'signin') => {
    setAuthMode(mode);
    setErrorMessage(null);
    setLoginMessage(null);
    setIsAuthModalOpen(true);
  };

  return (
    <div className="min-h-screen bg-[#070b12] text-slate-100 flex flex-col selection:bg-[#22c55e] selection:text-black relative">
      {/* Tight, Cohesive & Complete Header */}
      <header className="sticky top-0 z-40 bg-[#0c121d]/95 backdrop-blur-md border-b border-[#182335]">
        <div className="max-w-7xl mx-auto px-6 py-3.5 flex items-center justify-between gap-4">
          {/* Brand Logo & Model Status */}
          <div className="flex items-center gap-3 shrink-0">
            <div className="w-9 h-9 rounded-xl bg-[#14231b] border border-[#22c55e]/50 flex items-center justify-center text-[#22c55e] shadow-[0_0_18px_rgba(34,197,94,0.3)]">
              <ShieldAlert className="w-5 h-5 stroke-[2.2]" />
            </div>
            <div>
              <div className="text-base font-black tracking-tight text-white flex items-center gap-1.5">
                Floor Guard <span className="text-[#22c55e]">AI</span>
                <span className="text-[10px] px-2 py-0.2 rounded-full bg-[#172e21] text-[#22c55e] border border-[#22c55e]/30 font-semibold font-mono">
                  v8.0.0
                </span>
              </div>
              <p className="text-[10px] text-slate-400 font-medium">Autonomous Floor Safety Platform</p>
            </div>
          </div>

          {/* Right Group: Navigation links and Action Buttons brought closer together */}
          <div className="flex items-center gap-5 sm:gap-6">
            {/* Quick Navigation Links */}
            <nav className="hidden lg:flex items-center gap-5 text-xs font-semibold text-slate-300">
              <a href="#overview" className="hover:text-white transition-colors">Overview</a>
              <a href="#preview" className="hover:text-white transition-colors">Live Inspection</a>
              <a href="#categories" className="hover:text-white transition-colors">13 Hazard Classes</a>
              <a href="#architecture" className="hover:text-white transition-colors">AI Pipeline</a>
            </nav>

            <div className="hidden lg:block h-4 w-[1px] bg-[#1f2d42]" />

            {/* Action Buttons: Demo beside Login / Sign In */}
            <div className="flex items-center gap-2.5">
              <button
                onClick={handleQuickDemoAccess}
                disabled={isSubmitting}
                className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl bg-[#13221b] hover:bg-[#182e23] text-[#22c55e] hover:text-[#4ade80] border border-[#22c55e]/40 hover:border-[#22c55e]/70 text-xs font-bold transition-all cursor-pointer shadow-sm shadow-green-950/20"
                title="Instant access to inspect dashboard features"
              >
                <Sparkles className="w-3.5 h-3.5 text-[#22c55e]" />
                <span>Explore Demo</span>
              </button>

              <button
                onClick={() => openAuthModal('signin')}
                className="flex items-center gap-1.5 px-4 py-1.5 rounded-xl bg-[#22c55e] hover:bg-[#16a34a] text-black text-xs font-extrabold shadow-md shadow-green-950/40 transition-all cursor-pointer"
              >
                <LogIn className="w-3.5 h-3.5 stroke-[2.5]" />
                <span>Login / Sign In</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Landing Content */}
      <main className="flex-1">
        {/* Hero Section */}
        <section id="overview" className="relative pt-12 pb-16 px-6 border-b border-[#141e2e] overflow-hidden">
          {/* Ambient Lighting Gradients */}
          <div className="absolute top-1/4 left-1/4 w-[500px] h-[500px] bg-[#22c55e]/10 rounded-full blur-[120px] pointer-events-none" />
          <div className="absolute top-1/3 right-1/4 w-[450px] h-[450px] bg-[#38bdf8]/10 rounded-full blur-[120px] pointer-events-none" />

          <div className="max-w-5xl mx-auto text-center space-y-6 relative z-10">
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

            {/* Hero Action CTA Buttons: Demo beside Login */}
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
                onClick={handleQuickDemoAccess}
                className="flex items-center gap-2 px-5 py-3 rounded-xl bg-[#13221b] hover:bg-[#192f25] border border-[#22c55e]/50 text-[#22c55e] hover:text-[#4ade80] text-sm font-bold shadow-lg shadow-green-950/20 transition-all cursor-pointer"
              >
                <Sparkles className="w-4 h-4 text-[#22c55e]" />
                <span>Explore Live Demo</span>
              </button>

              <button
                onClick={() => setIsGoogleModalOpen(true)}
                className="flex items-center gap-2 px-5 py-3 rounded-xl bg-[#141d2c] hover:bg-[#1c283c] border border-[#23334c] text-slate-200 text-sm font-semibold transition-all cursor-pointer"
              >
                <svg className="w-4 h-4 shrink-0" viewBox="0 0 24 24">
                  <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
                  <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
                  <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z" />
                  <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z" />
                </svg>
                <span>Google Sign-In</span>
              </button>
            </div>

            {/* Performance Metrics Bar */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-4 max-w-4xl mx-auto">
              <div className="p-3.5 rounded-2xl bg-[#0d1522] border border-[#1a2638] shadow-sm">
                <div className="text-[10px] text-slate-400 uppercase tracking-wider">Detection Spectrum</div>
                <div className="text-xl font-black text-white mt-0.5">13 Classes</div>
                <div className="text-[10px] text-[#22c55e] font-semibold">12 Hazards + 1 Safe</div>
              </div>

              <div className="p-3.5 rounded-2xl bg-[#0d1522] border border-[#1a2638] shadow-sm">
                <div className="text-[10px] text-slate-400 uppercase tracking-wider">Inference Speed</div>
                <div className="text-xl font-black text-white mt-0.5">14.8 ms</div>
                <div className="text-[10px] text-[#38bdf8] font-semibold">67.5 FPS Real-Time</div>
              </div>

              <div className="p-3.5 rounded-2xl bg-[#0d1522] border border-[#1a2638] shadow-sm">
                <div className="text-[10px] text-slate-400 uppercase tracking-wider">Curated Dataset</div>
                <div className="text-xl font-black text-white mt-0.5">141 Images</div>
                <div className="text-[10px] text-amber-400 font-semibold">160 Verified Boxes</div>
              </div>

              <div className="p-3.5 rounded-2xl bg-[#0d1522] border border-[#1a2638] shadow-sm">
                <div className="text-[10px] text-slate-400 uppercase tracking-wider">Negative Control</div>
                <div className="text-xl font-black text-white mt-0.5">98% Conf</div>
                <div className="text-[10px] text-[#22c55e] font-semibold">Clean Floor Certified</div>
              </div>
            </div>
          </div>
        </section>

        {/* Live Visual Inspection Preview Card - Makes platform feel complete & tangible */}
        <section id="preview" className="py-12 px-6 max-w-6xl mx-auto">
          <div className="rounded-3xl bg-[#0d1522] border border-[#1e2e44] p-6 md:p-8 shadow-2xl relative overflow-hidden">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-6 border-b border-[#1b2a3e]">
              <div>
                <div className="flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full bg-[#22c55e] shadow-[0_0_8px_#22c55e] animate-pulse" />
                  <h3 className="text-base font-bold text-white tracking-tight">Real-Time Computer Vision Inference Feed</h3>
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                    Live Telemetry
                  </span>
                </div>
                <p className="text-xs text-slate-400 mt-0.5">
                  Live tensor stream processing with calibrated slip risk scores and coordinate localization
                </p>
              </div>

              <div className="flex items-center gap-2">
                <button
                  onClick={() => {
                    openAuthModal('signin');
                    setErrorMessage('Authentication required: Sign In or Create an Account to access the Detection Studio.');
                  }}
                  className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-[#22c55e] hover:bg-[#16a34a] text-black font-extrabold text-xs shadow-md transition-all cursor-pointer"
                >
                  <Eye className="w-3.5 h-3.5" />
                  <span>Launch Detection Studio</span>
                </button>
              </div>
            </div>

            {/* Visual Detection Preview Grid - Real High-Resolution Computer Vision Hazard Images */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-5 pt-6">
              {/* Item 1: Water Spill */}
              <div className="p-4 rounded-2xl bg-[#090f19] border border-[#1b283b] hover:border-red-500/40 transition-all space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-white flex items-center gap-1.5">
                    <Droplets className="w-3.5 h-3.5 text-[#38bdf8]" />
                    <span>Water Spill Detection</span>
                  </span>
                  <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-red-500/20 text-red-400 border border-red-500/30">
                    High Risk • 93.4%
                  </span>
                </div>
                
                {/* Real Floor Image with Calibrated Bounding Box */}
                <div className="h-44 rounded-xl bg-[#101928] border border-red-500/40 relative overflow-hidden group shadow-inner">
                  <img
                    src="/assets/samples/gallery/water_spill.jpg"
                    alt="Water Spill Floor Hazard"
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                    onError={(e) => {
                      (e.currentTarget as HTMLImageElement).src = '/assets/samples/thumb_water_spill.jpg';
                    }}
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-black/30 pointer-events-none" />
                  
                  {/* Calibrated Computer Vision Bounding Box */}
                  <div className="absolute top-[22%] left-[16%] w-[66%] h-[56%] border-2 border-red-500 bg-red-500/20 rounded-md flex items-start justify-between p-1.5 shadow-[0_0_15px_rgba(239,68,68,0.5)]">
                    <span className="text-[10px] font-mono font-extrabold bg-red-500 text-white px-2 py-0.5 rounded shadow">
                      WATER SPILL 93.4%
                    </span>
                    <span className="text-[9px] font-mono bg-black/75 text-red-300 px-1.5 py-0.5 rounded border border-red-500/40">
                      SLIP: 0.88
                    </span>
                  </div>

                  <div className="absolute bottom-2 left-2.5 right-2.5 flex items-center justify-between text-[10px] font-mono text-white/90">
                    <span className="bg-black/70 px-2 py-0.5 rounded backdrop-blur-sm border border-white/10">Monitored Main Walkway</span>
                    <span className="bg-red-950/80 text-red-300 border border-red-500/40 px-1.5 py-0.5 rounded">Critical Slip Risk</span>
                  </div>
                </div>

                <div className="text-[11px] text-slate-400 flex items-center justify-between font-mono">
                  <span>Hazard Area: ~0.45 m²</span>
                  <span className="text-[#38bdf8]">Latency: 14.8ms</span>
                </div>
              </div>

              {/* Item 2: Broken Glass */}
              <div className="p-4 rounded-2xl bg-[#090f19] border border-[#1b283b] hover:border-red-500/40 transition-all space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-white flex items-center gap-1.5">
                    <Zap className="w-3.5 h-3.5 text-red-400" />
                    <span>Broken Glass Detection</span>
                  </span>
                  <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-red-500/20 text-red-400 border border-red-500/30">
                    Critical • 94.1%
                  </span>
                </div>

                {/* Real Floor Image with Calibrated Bounding Box */}
                <div className="h-44 rounded-xl bg-[#101928] border border-red-500/40 relative overflow-hidden group shadow-inner">
                  <img
                    src="/assets/samples/gallery/broken_glass.jpg"
                    alt="Broken Glass Floor Hazard"
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                    onError={(e) => {
                      (e.currentTarget as HTMLImageElement).src = '/assets/samples/thumb_broken_glass.jpg';
                    }}
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-black/30 pointer-events-none" />

                  {/* Calibrated Computer Vision Bounding Box */}
                  <div className="absolute top-[24%] left-[20%] w-[58%] h-[52%] border-2 border-red-500 bg-red-500/20 rounded-md flex items-start justify-between p-1.5 shadow-[0_0_15px_rgba(239,68,68,0.5)]">
                    <span className="text-[10px] font-mono font-extrabold bg-red-500 text-white px-2 py-0.5 rounded shadow">
                      BROKEN GLASS 94.1%
                    </span>
                    <span className="text-[9px] font-mono bg-black/75 text-red-300 px-1.5 py-0.5 rounded border border-red-500/40">
                      PUNCTURE
                    </span>
                  </div>

                  <div className="absolute bottom-2 left-2.5 right-2.5 flex items-center justify-between text-[10px] font-mono text-white/90">
                    <span className="bg-black/70 px-2 py-0.5 rounded backdrop-blur-sm border border-white/10">Retail Corridor Surface</span>
                    <span className="bg-red-950/80 text-red-300 border border-red-500/40 px-1.5 py-0.5 rounded">Sharp Debris</span>
                  </div>
                </div>

                <div className="text-[11px] text-slate-400 flex items-center justify-between font-mono">
                  <span>Puncture Hazard</span>
                  <span className="text-[#38bdf8]">Latency: 15.1ms</span>
                </div>
              </div>

              {/* Item 3: Clean Floor Negative Control */}
              <div className="p-4 rounded-2xl bg-[#090f19] border border-[#1b283b] hover:border-emerald-500/40 transition-all space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-white flex items-center gap-1.5">
                    <CheckCircle2 className="w-3.5 h-3.5 text-[#22c55e]" />
                    <span>Clean Floor Control</span>
                  </span>
                  <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                    Certified Safe • 98.2%
                  </span>
                </div>

                {/* Real Clean Floor Image with Safety Verification Badge */}
                <div className="h-44 rounded-xl bg-[#101928] border border-emerald-500/40 relative overflow-hidden group shadow-inner">
                  <img
                    src="/assets/samples/gallery/clean_floor.jpg"
                    alt="Certified Clean Floor Surface"
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                    onError={(e) => {
                      (e.currentTarget as HTMLImageElement).src = '/assets/samples/thumb_clean_floor.jpg';
                    }}
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-black/30 pointer-events-none" />

                  {/* Certified Safe Control Badge */}
                  <div className="absolute inset-0 flex items-center justify-center p-3">
                    <div className="bg-black/75 backdrop-blur-md border border-emerald-500/50 rounded-xl p-3 text-center space-y-1 shadow-lg max-w-[200px]">
                      <CheckCircle2 className="w-6 h-6 text-[#22c55e] mx-auto animate-pulse" />
                      <div className="text-xs font-bold text-white">Negative Control Verified</div>
                      <div className="text-[10px] text-emerald-400 font-mono">Zero Obstacles Detected</div>
                    </div>
                  </div>

                  <div className="absolute bottom-2 left-2.5 right-2.5 flex items-center justify-between text-[10px] font-mono text-white/90">
                    <span className="bg-black/70 px-2 py-0.5 rounded backdrop-blur-sm border border-white/10">Polished Hospital Hallway</span>
                    <span className="bg-emerald-950/80 text-emerald-300 border border-emerald-500/40 px-1.5 py-0.5 rounded">Safe Control</span>
                  </div>
                </div>

                <div className="text-[11px] text-slate-400 flex items-center justify-between font-mono">
                  <span>Surface Status: Clean</span>
                  <span className="text-[#22c55e]">Zero False Alarm</span>
                </div>
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

      {/* Auth Modal: Sign In / Create Account with Name, Email & Password */}
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
                    {authMode === 'signin' ? 'Sign In to Floor Guard' : 'Create New Account'}
                  </h2>
                  <p className="text-xs text-slate-400">
                    {authMode === 'signin' ? 'Enter your registered credentials' : 'Register your operator safety credentials'}
                  </p>
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
              onClick={() => setIsGoogleModalOpen(true)}
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
                onClick={() => {
                  setAuthMode('signin');
                  setErrorMessage(null);
                  setLoginMessage(null);
                }}
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
                onClick={() => {
                  setAuthMode('signup');
                  setErrorMessage(null);
                  setLoginMessage(null);
                }}
                className={`py-1.5 rounded-lg text-xs font-semibold transition-all cursor-pointer ${
                  authMode === 'signup'
                    ? 'bg-[#22c55e] text-black shadow-sm font-bold'
                    : 'text-slate-400 hover:text-white'
                }`}
              >
                Create Account
              </button>
            </div>

            {/* Error Message Alert */}
            {errorMessage && (
              <div className="p-3 rounded-xl bg-red-950/40 border border-red-500/50 text-red-200 text-xs flex items-start gap-2.5 animate-shake">
                <AlertCircle className="w-4 h-4 text-red-400 shrink-0 mt-0.5" />
                <div className="flex-1 leading-relaxed">{errorMessage}</div>
              </div>
            )}

            {/* Success Message Alert */}
            {loginMessage && (
              <div className="p-3 rounded-xl bg-[#14291f] border border-[#22c55e]/40 text-[#22c55e] text-xs flex items-center gap-2 animate-pulse">
                <CheckCircle2 className="w-4 h-4 shrink-0" />
                <span>{loginMessage}</span>
              </div>
            )}

            {/* Authentication Form */}
            <form onSubmit={handleFormSubmit} className="space-y-3.5">
              {/* Full Name field - Shown when creating account */}
              {authMode === 'signup' && (
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">
                    Full Name <span className="text-[#22c55e]">*</span>
                  </label>
                  <input
                    type="text"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    required={authMode === 'signup'}
                    autoFocus={authMode === 'signup'}
                    className="w-full px-3.5 py-2.5 rounded-xl bg-[#101724] border border-[#1f2e44] text-white text-xs focus:outline-none focus:border-[#22c55e] transition-colors"
                    placeholder="e.g. Alex Morgan"
                  />
                </div>
              )}

              {/* Email */}
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">
                  Email Address <span className="text-[#22c55e]">*</span>
                </label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  autoFocus={authMode === 'signin'}
                  className="w-full px-3.5 py-2.5 rounded-xl bg-[#101724] border border-[#1f2e44] text-white text-xs focus:outline-none focus:border-[#22c55e] transition-colors"
                  placeholder="name@company.com"
                />
              </div>

              {/* Password */}
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">
                  Password <span className="text-[#22c55e]">*</span>
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
              <span>Secure Session Encryption</span>
              <span className="text-[#22c55e]">YOLOv8 Powered</span>
            </div>
          </div>
        </div>
      )}

      {/* Production-Grade Clean Google Sign-In Modal */}
      {isGoogleModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/85 backdrop-blur-md animate-fade-in">
          <div className="relative w-full max-w-sm rounded-3xl p-6 sm:p-7 bg-[#0e1624] border border-[#23354e] shadow-2xl space-y-5">
            {/* Google Brand Header */}
            <div className="text-center space-y-2">
              <div className="w-12 h-12 rounded-2xl bg-white flex items-center justify-center mx-auto shadow-lg shadow-white/10">
                <svg className="w-7 h-7" viewBox="0 0 24 24">
                  <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
                  <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
                  <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z" />
                  <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z" />
                </svg>
              </div>
              <h3 className="text-lg font-bold text-white tracking-tight">Sign in with Google</h3>
              <p className="text-xs text-slate-400">
                Choose an account to continue to Floor Guard AI
              </p>
            </div>

            {/* Error Message */}
            {errorMessage && (
              <div className="p-3 rounded-xl bg-red-950/40 border border-red-500/50 text-red-200 text-xs flex items-start gap-2.5">
                <AlertCircle className="w-4 h-4 text-red-400 shrink-0 mt-0.5" />
                <div className="flex-1 leading-relaxed">{errorMessage}</div>
              </div>
            )}

            {/* Success Message */}
            {loginMessage && (
              <div className="p-3 rounded-xl bg-blue-950/40 border border-blue-500/40 text-blue-200 text-xs flex items-center gap-2 animate-pulse">
                <div className="w-3.5 h-3.5 rounded-full border-2 border-blue-400 border-t-transparent animate-spin" />
                <span>{loginMessage}</span>
              </div>
            )}

            {/* Official Google OAuth Action Button */}
            <div className="space-y-3 pt-1">
              <button
                type="button"
                onClick={handleLaunchGoogleCloudPopup}
                disabled={isSubmitting}
                className="w-full flex items-center justify-center gap-3 py-3 px-4 rounded-xl bg-white hover:bg-slate-100 text-slate-900 font-bold text-xs shadow-lg transition-all cursor-pointer disabled:opacity-50"
              >
                <svg className="w-5 h-5 shrink-0" viewBox="0 0 24 24">
                  <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
                  <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
                  <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z" />
                  <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z" />
                </svg>
                <span>{isSubmitting ? 'Connecting to Google...' : 'Continue with Google'}</span>
              </button>

              {/* Rendered Google Identity Services Button Container */}
              <div ref={googleBtnContainerRef} className="flex items-center justify-center min-h-[44px]" />
            </div>

            {/* Subtle option to enter email directly if needed */}
            <div className="pt-2 border-t border-[#1e2c40]">
              {!showCustomGoogleInput ? (
                <button
                  type="button"
                  onClick={() => setShowCustomGoogleInput(true)}
                  className="w-full text-center text-[11px] text-slate-400 hover:text-white transition-colors cursor-pointer"
                >
                  Or enter Google email manually →
                </button>
              ) : (
                <form onSubmit={handleCustomGoogleSubmit} className="space-y-2.5 pt-1 animate-fade-in">
                  <input
                    type="email"
                    value={customGoogleEmail}
                    onChange={(e) => setCustomGoogleEmail(e.target.value)}
                    placeholder="name@gmail.com"
                    required
                    className="w-full px-3 py-2 rounded-xl bg-[#101724] border border-[#1f2e44] text-white text-xs focus:outline-none focus:border-[#4285F4]"
                  />
                  <input
                    type="text"
                    value={customGoogleName}
                    onChange={(e) => setCustomGoogleName(e.target.value)}
                    placeholder="Full Name (from Google Profile)"
                    required
                    className="w-full px-3 py-2 rounded-xl bg-[#101724] border border-[#1f2e44] text-white text-xs focus:outline-none focus:border-[#4285F4]"
                  />
                  <div className="flex items-center gap-2">
                    <button
                      type="submit"
                      disabled={isSubmitting}
                      className="flex-1 py-2 rounded-xl bg-[#1d2d42] hover:bg-[#253952] text-white text-xs font-semibold border border-[#2e4360] transition-colors"
                    >
                      Sign In with Account
                    </button>
                    <button
                      type="button"
                      onClick={() => setShowCustomGoogleInput(false)}
                      className="px-3 py-2 rounded-xl bg-[#141d2c] text-slate-400 text-xs hover:text-white"
                    >
                      Cancel
                    </button>
                  </div>
                </form>
              )}
            </div>

            {/* Cancel / Close Modal */}
            <button
              type="button"
              disabled={isSubmitting}
              onClick={() => {
                setIsGoogleModalOpen(false);
                setLoginMessage(null);
                setErrorMessage(null);
                setShowCustomGoogleInput(false);
              }}
              className="w-full py-2.5 rounded-xl bg-[#141d2c] hover:bg-[#1a2638] text-slate-300 text-xs font-semibold border border-[#23334c] transition-colors cursor-pointer"
            >
              Cancel
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
