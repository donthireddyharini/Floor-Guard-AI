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
import { AiModelLabView } from './components/AiModelLabView';
import { HazardHistoryView } from './components/HazardHistoryView';
import { AnalyticsView } from './components/AnalyticsView';
import { SettingsView } from './components/SettingsView';
import { DetectionDetailModal } from './components/DetectionDetailModal';
import { NavSection, AnalyticsSummary } from './types';

export default function App() {
  const [activeSection, setActiveSection] = useState<NavSection>('overview');
  const [selectedDateRange, setSelectedDateRange] = useState('May 20, 2026 – May 26, 2026');
  const [selectedDetection, setSelectedDetection] = useState<any | null>(null);
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

  useEffect(() => {
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
    <div className="min-h-screen bg-[#0a0f1d] text-slate-100 flex font-sans antialiased selection:bg-orange-500 selection:text-white">
      {/* Sidebar Navigation */}
      <Sidebar
        activeSection={activeSection}
        onSelectSection={(sec) => setActiveSection(sec)}
        onOpenModelDetails={() => setActiveSection('ai_model_lab')}
      />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 overflow-y-auto">
        {/* Header Bar */}
        <Header
          activeSection={activeSection}
          onOpenModelDetails={() => setActiveSection('ai_model_lab')}
          selectedDateRange={selectedDateRange}
          onSelectDateRange={setSelectedDateRange}
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

          {activeSection === 'video_analysis' && (
            <VideoAnalysisView
              onOpenDetail={(id) => setSelectedDetection({ id })}
            />
          )}

          {activeSection === 'hazard_history' && (
            <HazardHistoryView
              onSelectDetection={(item) => setSelectedDetection(item)}
            />
          )}

          {activeSection === 'analytics' && <AnalyticsView />}

          {activeSection === 'ai_model_lab' && (
            <AiModelLabView
              models={modelStatus?.all_models || []}
              activeModelId={modelStatus?.active_model_id}
              onModelSelect={handleSelectModel}
            />
          )}

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
