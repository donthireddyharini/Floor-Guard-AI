/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState, useEffect } from 'react';
import { Sidebar } from './components/Sidebar';
import { Header } from './components/Header';
import { HomeView } from './components/HomeView';
import { OverviewDashboard } from './components/OverviewDashboard';
import { ImageDetectionWorkspace } from './components/ImageDetectionWorkspace';
import { VideoAnalysisView } from './components/VideoAnalysisView';
import { DatasetTrainingView } from './components/DatasetTrainingView';
import { HazardHistoryView } from './components/HazardHistoryView';
import { AnalyticsView } from './components/AnalyticsView';
import { SettingsView } from './components/SettingsView';
import { DetectionDetailModal } from './components/DetectionDetailModal';
import { NavSection, AnalyticsSummary } from './types';

class ErrorBoundary extends React.Component<
  { children: React.ReactNode; resetKey?: string },
  { hasError: boolean; error: any }
> {
  constructor(props: { children: React.ReactNode; resetKey?: string }) {
    super(props);
    this.state = { hasError: false, error: null };
  }
  static getDerivedStateFromError(error: any) {
    return { hasError: true, error };
  }
  componentDidCatch(error: any, info: any) {
    console.error('ErrorBoundary caught:', error, info);
  }
  componentDidUpdate(prevProps: { resetKey?: string }) {
    if (this.props.resetKey !== prevProps.resetKey && this.state.hasError) {
      this.setState({ hasError: false, error: null });
    }
  }
  render() {
    if (this.state.hasError) {
      return (
        <div className="flex flex-col items-center justify-center p-12 text-center min-h-[500px]">
          <div className="p-6 rounded-2xl bg-[#131b29] border border-red-500/40 text-red-200 max-w-md shadow-2xl">
            <h3 className="font-bold text-base mb-2 text-white">Floor Guard AI - Session Restored</h3>
            <p className="text-xs text-slate-300 mb-4">
              {this.state.error?.message || 'A rendering state was recovered safely. Click below to continue uninterrupted.'}
            </p>
            <div className="flex items-center justify-center gap-3">
              <button
                onClick={() => this.setState({ hasError: false, error: null })}
                className="px-4 py-2 bg-[#22c55e] hover:bg-[#16a34a] text-black font-bold text-xs rounded-xl shadow-lg transition-colors cursor-pointer"
              >
                Resume Current View
              </button>
              <button
                onClick={() => {
                  this.setState({ hasError: false, error: null });
                  window.location.href = '/';
                }}
                className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white font-medium text-xs rounded-xl border border-slate-700 transition-colors cursor-pointer"
              >
                Return to Overview
              </button>
            </div>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}

export default function App() {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(() => {
    try {
      return localStorage.getItem('floorguard_authenticated') === 'true';
    } catch {
      return false;
    }
  });

  const [userRole, setUserRole] = useState<string>(() => {
    try {
      return localStorage.getItem('floorguard_role') || 'Senior Facility Safety Officer';
    } catch {
      return 'Senior Facility Safety Officer';
    }
  });

  const [activeSection, setActiveSection] = useState<NavSection>(() => {
    try {
      const authed = localStorage.getItem('floorguard_authenticated') === 'true';
      return authed ? 'overview' : 'home';
    } catch {
      return 'home';
    }
  });

  const [selectedDateRange, setSelectedDateRange] = useState('May 20, 2026 – May 26, 2026');
  const [selectedDetection, setSelectedDetection] = useState<any | null>(null);
  const [analyticsData, setAnalyticsData] = useState<AnalyticsSummary | null>(null);
  const [modelStatus, setModelStatus] = useState<any>(null);

  const fetchModelStatus = () => {
    fetch('/api/model/status')
      .then((res) => res.json())
      .then((data) => {
        if (data.status === 'ok') {
          setModelStatus(data);
        }
      })
      .catch((err) => {
        console.error('Failed to load model status:', err);
      });
  };

  // Load backend summary and model status
  useEffect(() => {
    fetch('/api/analytics/summary')
      .then((res) => res.json())
      .then((data) => {
        if (data.status === 'ok') {
          setAnalyticsData(data);
        }
      })
      .catch((err) => {
        console.error('Failed to load analytics summary:', err);
      });

    fetchModelStatus();
  }, []);

  const handleLogin = (role?: string) => {
    const assignedRole = role || 'Senior Facility Safety Officer';
    try {
      localStorage.setItem('floorguard_authenticated', 'true');
      localStorage.setItem('floorguard_role', assignedRole);
    } catch (e) {
      console.warn(e);
    }
    setIsAuthenticated(true);
    setUserRole(assignedRole);
    setActiveSection('overview');
  };

  const handleSignOut = () => {
    try {
      localStorage.removeItem('floorguard_authenticated');
    } catch (e) {
      console.warn(e);
    }
    setIsAuthenticated(false);
    setActiveSection('home');
  };

  const handleSelectSection = (sec: NavSection) => {
    if (!isAuthenticated && sec !== 'home') {
      // User must log in first to access the app interface
      setActiveSection('home');
    } else {
      setActiveSection(sec);
    }
  };

  const handleSelectModel = async (modelId: string) => {
    try {
      const res = await fetch('/api/model/select', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ model_id: modelId })
      });
      const data = await res.json();
      if (data.status === 'ok') {
        fetchModelStatus();
      }
    } catch (err) {
      console.error('Failed to switch model:', err);
    }
  };

  return (
    <div className="min-h-screen bg-[#090e17] text-slate-100 flex font-sans antialiased selection:bg-[#22c55e] selection:text-black">
      {/* Sidebar Navigation */}
      <Sidebar
        activeSection={activeSection}
        onSelectSection={handleSelectSection}
        onOpenModelDetails={() => handleSelectSection('analytics')}
        activeModel={modelStatus?.model}
        isAuthenticated={isAuthenticated}
        onSignOut={handleSignOut}
      />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 overflow-y-auto">
        {/* Header Bar */}
        <Header
          activeSection={activeSection}
          onOpenModelDetails={() => handleSelectSection('analytics')}
          activeModel={modelStatus?.model}
          allModels={modelStatus?.all_models || []}
          onSelectModel={handleSelectModel}
          isAuthenticated={isAuthenticated}
          onSignOut={handleSignOut}
          onOpenLogin={() => setActiveSection('home')}
          userRole={userRole}
        />

        {/* View Routing */}
        <main className="flex-1 pb-12">
          <ErrorBoundary resetKey={activeSection}>
          {activeSection === 'home' && (
            <HomeView
              isAuthenticated={isAuthenticated}
              onLogin={handleLogin}
              onSignOut={handleSignOut}
              onNavigate={handleSelectSection}
              onOpenModelDetails={() => handleSelectSection('analytics')}
            />
          )}

          {activeSection === 'overview' && (
            <OverviewDashboard
              onNavigate={handleSelectSection}
              onSelectDetection={(item) => setSelectedDetection(item)}
              analyticsData={analyticsData}
              activeModel={modelStatus?.model}
              allModels={modelStatus?.all_models || []}
              onSelectModel={handleSelectModel}
            />
          )}

          {activeSection === 'image_detection' && (
            <ImageDetectionWorkspace
              activeModel={modelStatus?.model}
              allModels={modelStatus?.all_models || []}
              onSelectModel={handleSelectModel}
            />
          )}

          {activeSection === 'video_analysis' && <VideoAnalysisView />}

          {activeSection === 'dataset_training' && <DatasetTrainingView />}

          {activeSection === 'hazard_history' && (
            <HazardHistoryView onSelectDetection={(item) => setSelectedDetection(item)} />
          )}

          {activeSection === 'analytics' && <AnalyticsView />}

          {activeSection === 'settings' && (
            <SettingsView
              activeModel={modelStatus?.model}
              allModels={modelStatus?.all_models || []}
              onSelectModel={handleSelectModel}
            />
          )}
          </ErrorBoundary>
        </main>
      </div>

      {/* Inspection Modal */}
      {selectedDetection && (
        <DetectionDetailModal
          detection={selectedDetection}
          onClose={() => setSelectedDetection(null)}
        />
      )}
    </div>
  );
}
