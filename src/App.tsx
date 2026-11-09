/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState, useEffect } from 'react';
import { Sidebar } from './components/Sidebar';
import { Header } from './components/Header';
import { OverviewDashboard } from './components/OverviewDashboard';
import { ImageDetectionWorkspace } from './components/ImageDetectionWorkspace';
import { VideoAnalysisView } from './components/VideoAnalysisView';
import { DatasetTrainingView } from './components/DatasetTrainingView';
import { HazardHistoryView } from './components/HazardHistoryView';
import { AnalyticsView } from './components/AnalyticsView';
import { SettingsView } from './components/SettingsView';
import { DetectionDetailModal } from './components/DetectionDetailModal';
import { NavSection, AnalyticsSummary } from './types';

export default function App() {
  const [activeSection, setActiveSection] = useState<NavSection>('overview');
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
        onSelectSection={(sec) => setActiveSection(sec)}
        onOpenModelDetails={() => setActiveSection('analytics')}
        activeModel={modelStatus?.model}
      />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 overflow-y-auto">
        {/* Header Bar */}
        <Header
          activeSection={activeSection}
          onOpenModelDetails={() => setActiveSection('analytics')}
          activeModel={modelStatus?.model}
          allModels={modelStatus?.all_models || []}
          onSelectModel={handleSelectModel}
        />

        {/* View Routing */}
        <main className="flex-1 pb-12">
          {activeSection === 'overview' && (
            <OverviewDashboard
              onNavigate={(sec) => setActiveSection(sec)}
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
