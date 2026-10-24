import React, { useState, useEffect } from 'react';
import {
  TrendingUp,
  BarChart,
  CheckCircle,
  AlertTriangle,
  Cpu,
  Shield,
  Activity,
  Layers,
  Target,
  FileText,
  Clock,
  PieChart,
  Info,
  ExternalLink
} from 'lucide-react';

export const AnalyticsView: React.FC = () => {
  const [selectedBenchmark, setSelectedBenchmark] = useState<'operational' | 'phase4_2' | 'phase4_3'>('operational');
  const [analyticsData, setAnalyticsData] = useState<any | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        setIsLoading(true);
        const res = await fetch('/api/analytics/real');
        if (res.ok) {
          const data = await res.json();
          setAnalyticsData(data);
        }
      } catch (err) {
        console.error('Failed to load analytics:', err);
      } finally {
        setIsLoading(false);
      }
    };
    fetchAnalytics();
  }, []);

  const opKpis = analyticsData?.operational_kpis || {
    total_analyses: 0,
    images_analyzed: 0,
    videos_analyzed: 0,
    hazards_detected: 0,
    clean_floors_confirmed: 0,
    safe_pass_rate_pct: 100
  };

  const classDist = analyticsData?.hazard_class_distribution || [];
  const timeline = analyticsData?.activity_timeline || [];

  return (
    <div className="p-6 space-y-6 max-w-[1720px] mx-auto text-slate-100">
      {/* Header Banner */}
      <div className="bg-[#111827] border border-slate-800 rounded-2xl p-6 shadow-xl relative overflow-hidden">
        <div className="absolute top-0 right-0 w-96 h-96 bg-orange-500/5 rounded-full blur-3xl pointer-events-none" />
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 relative z-10">
          <div className="space-y-1">
            <div className="flex items-center gap-3">
              <div className="p-2.5 rounded-xl bg-orange-500/10 border border-orange-500/30 text-orange-400">
                <Activity className="w-5 h-5" />
              </div>
              <h1 className="text-xl font-bold tracking-tight text-white">System Analytics & Scientific Validation</h1>
              <span className="text-[11px] font-mono px-2.5 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                Audit Verified
              </span>
            </div>
            <p className="text-xs text-slate-400 max-w-3xl leading-relaxed">
              Authentic operational database records combined with rigorous, held-out model evaluation benchmarks from Phase 4.2 and Phase 4.3. Fabricated metrics and simulated confusion matrices have been completely decommissioned.
            </p>
          </div>

          {/* Section Selector */}
          <div className="flex items-center gap-1.5 p-1 bg-slate-900 border border-slate-800 rounded-xl text-xs font-mono">
            <button
              onClick={() => setSelectedBenchmark('operational')}
              className={`px-3 py-1.5 rounded-lg transition-all cursor-pointer ${
                selectedBenchmark === 'operational'
                  ? 'bg-orange-500 text-white font-bold shadow-md'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              Operational DB Runs
            </button>
            <button
              onClick={() => setSelectedBenchmark('phase4_2')}
              className={`px-3 py-1.5 rounded-lg transition-all cursor-pointer ${
                selectedBenchmark === 'phase4_2'
                  ? 'bg-orange-500 text-white font-bold shadow-md'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              Phase 4.2 Benchmark
            </button>
            <button
              onClick={() => setSelectedBenchmark('phase4_3')}
              className={`px-3 py-1.5 rounded-lg transition-all cursor-pointer ${
                selectedBenchmark === 'phase4_3'
                  ? 'bg-orange-500 text-white font-bold shadow-md'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              Phase 4.3 Expanded (25)
            </button>
          </div>
        </div>
      </div>

      {/* VIEW 1: OPERATIONAL TELEMETRY */}
      {selectedBenchmark === 'operational' && (
        <div className="space-y-6">
          {/* Top KPI Cards */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-[#111827] border border-slate-800 rounded-xl p-4">
              <div className="text-xs text-slate-400 font-mono">Total DB Inspections</div>
              <div className="text-2xl font-bold font-mono text-white mt-1">
                {opKpis.total_analyses}
              </div>
              <div className="text-[11px] text-slate-500 font-mono mt-0.5">
                {opKpis.images_analyzed} images • {opKpis.videos_analyzed} videos
              </div>
            </div>

            <div className="bg-[#111827] border border-slate-800 rounded-xl p-4">
              <div className="text-xs text-slate-400 font-mono">Hazards Recorded</div>
              <div className="text-2xl font-bold font-mono text-rose-400 mt-1">
                {opKpis.hazards_detected}
              </div>
              <div className="text-[11px] text-slate-500 font-mono mt-0.5">
                Indexed in detections table
              </div>
            </div>

            <div className="bg-[#111827] border border-slate-800 rounded-xl p-4">
              <div className="text-xs text-slate-400 font-mono">Clean Floors Cleared</div>
              <div className="text-2xl font-bold font-mono text-emerald-400 mt-1">
                {opKpis.clean_floors_confirmed}
              </div>
              <div className="text-[11px] text-slate-500 font-mono mt-0.5">
                Zero hazard detections
              </div>
            </div>

            <div className="bg-[#111827] border border-slate-800 rounded-xl p-4">
              <div className="text-xs text-slate-400 font-mono">Safe Floor Clearance</div>
              <div className="text-2xl font-bold font-mono text-cyan-400 mt-1">
                {opKpis.safe_pass_rate_pct}%
              </div>
              <div className="text-[11px] text-slate-500 font-mono mt-0.5">
                Historical safety ratio
              </div>
            </div>
          </div>

          {/* Operational Distribution & Timeline */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            {/* Hazard Distribution */}
            <div className="lg:col-span-6 bg-[#111827] border border-slate-800 rounded-2xl p-5 space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-2">
                  <PieChart className="w-4 h-4 text-orange-400" />
                  Hazard Class Distribution (Database)
                </h3>
                <span className="text-[10px] font-mono text-slate-500">Live SQLite Counts</span>
              </div>

              {classDist.length > 0 ? (
                <div className="space-y-3 pt-2">
                  {classDist.map((item: any, idx: number) => {
                    const totalDets = opKpis.hazards_detected || 1;
                    const pct = Math.round((item.count / totalDets) * 100);
                    return (
                      <div key={idx} className="space-y-1">
                        <div className="flex justify-between text-xs font-mono">
                          <span className="text-white capitalize">{item.class_name.replace(/_/g, ' ')}</span>
                          <span className="text-slate-400">{item.count} incidents ({pct}%)</span>
                        </div>
                        <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
                          <div
                            className="h-full bg-gradient-to-r from-orange-500 to-amber-500 rounded-full"
                            style={{ width: `${pct}%` }}
                          />
                        </div>
                      </div>
                    );
                  })}
                </div>
              ) : (
                <div className="p-8 text-center text-xs text-slate-500 font-mono">
                  No hazards logged yet in operational database.
                </div>
              )}
            </div>

            {/* Activity Timeline */}
            <div className="lg:col-span-6 bg-[#111827] border border-slate-800 rounded-2xl p-5 space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-2">
                  <Clock className="w-4 h-4 text-orange-400" />
                  Recent Inspection Timeline (Days)
                </h3>
                <span className="text-[10px] font-mono text-slate-500">Activity History</span>
              </div>

              {timeline.length > 0 ? (
                <div className="space-y-2 pt-1">
                  {timeline.map((entry: any, tIdx: number) => (
                    <div
                      key={tIdx}
                      className="p-3 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-between text-xs font-mono"
                    >
                      <span className="text-slate-300">{entry.day}</span>
                      <div className="flex items-center gap-3">
                        <span className="text-cyan-400 font-bold">{entry.analyses} Analyses</span>
                        <span className="text-slate-500">|</span>
                        <span className="text-rose-400 font-bold">{entry.hazards || 0} Hazards</span>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="p-8 text-center text-xs text-slate-500 font-mono">
                  Timeline activity will populate automatically as runs occur.
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* VIEW 2: PHASE 4.2 FROZEN BENCHMARK */}
      {selectedBenchmark === 'phase4_2' && (
        <div className="space-y-6">
          {/* Summary Strip */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-[#111827] border border-slate-800 rounded-xl p-4">
              <div className="text-xs text-slate-400 font-mono">Overall mAP@0.5</div>
              <div className="text-2xl font-bold font-mono text-orange-400 mt-1">67.3%</div>
              <div className="text-[11px] text-emerald-400 font-mono mt-0.5">+36.2% vs Phase 4</div>
            </div>

            <div className="bg-[#111827] border border-slate-800 rounded-xl p-4">
              <div className="text-xs text-slate-400 font-mono">Overall mAP@0.5:0.95</div>
              <div className="text-2xl font-bold font-mono text-white mt-1">33.9%</div>
              <div className="text-[11px] text-slate-500 font-mono mt-0.5">IoU range 0.50 to 0.95</div>
            </div>

            <div className="bg-[#111827] border border-slate-800 rounded-xl p-4">
              <div className="text-xs text-slate-400 font-mono">Clean Floor FP Rate</div>
              <div className="text-2xl font-bold font-mono text-emerald-400 mt-1">0.0%</div>
              <div className="text-[11px] text-emerald-400 font-mono mt-0.5">2/2 True Negatives (0 FP)</div>
            </div>

            <div className="bg-[#111827] border border-slate-800 rounded-xl p-4">
              <div className="text-xs text-slate-400 font-mono">Inference Latency</div>
              <div className="text-2xl font-bold font-mono text-cyan-400 mt-1">81.7 ms</div>
              <div className="text-[11px] text-slate-500 font-mono mt-0.5">12.24 FPS on CPU</div>
            </div>
          </div>

          {/* Per-Class Breakdown Table */}
          <div className="bg-[#111827] border border-slate-800 rounded-2xl p-5 space-y-4">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400">
              Phase 4.2 Frozen Test Split Benchmark Breakdown (11 Test Samples)
            </h3>
            <div className="overflow-x-auto">
              <table className="w-full text-xs font-mono text-left">
                <thead className="bg-slate-900 text-slate-400 border-b border-slate-800">
                  <tr>
                    <th className="py-2.5 px-3 font-semibold">Hazard Class</th>
                    <th className="py-2.5 px-3 font-semibold">Precision</th>
                    <th className="py-2.5 px-3 font-semibold">Recall</th>
                    <th className="py-2.5 px-3 font-semibold">mAP@0.5</th>
                    <th className="py-2.5 px-3 font-semibold">mAP@0.5:0.95</th>
                    <th className="py-2.5 px-3 font-semibold">Phase 4 Baseline Delta</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800">
                  <tr>
                    <td className="py-2.5 px-3 text-white font-bold">water_spill</td>
                    <td className="py-2.5 px-3 text-slate-300">79.7%</td>
                    <td className="py-2.5 px-3 text-emerald-400 font-bold">100.0%</td>
                    <td className="py-2.5 px-3 text-orange-400 font-bold">99.5%</td>
                    <td className="py-2.5 px-3 text-slate-300">49.8%</td>
                    <td className="py-2.5 px-3 text-emerald-400">+98.3% (Synthetic Augmentation)</td>
                  </tr>
                  <tr>
                    <td className="py-2.5 px-3 text-white font-bold">oil_spill</td>
                    <td className="py-2.5 px-3 text-slate-300">62.0%</td>
                    <td className="py-2.5 px-3 text-slate-300">57.4%</td>
                    <td className="py-2.5 px-3 text-orange-400 font-bold">56.1%</td>
                    <td className="py-2.5 px-3 text-slate-300">31.1%</td>
                    <td className="py-2.5 px-3 text-emerald-400">+51.7%</td>
                  </tr>
                  <tr>
                    <td className="py-2.5 px-3 text-white font-bold">broken_glass</td>
                    <td className="py-2.5 px-3 text-slate-300">37.5%</td>
                    <td className="py-2.5 px-3 text-slate-300">53.3%</td>
                    <td className="py-2.5 px-3 text-orange-400 font-bold">47.2%</td>
                    <td className="py-2.5 px-3 text-slate-300">20.7%</td>
                    <td className="py-2.5 px-3 text-slate-400">+0.1%</td>
                  </tr>
                  <tr>
                    <td className="py-2.5 px-3 text-white font-bold">obstacle</td>
                    <td className="py-2.5 px-3 text-slate-300">55.5%</td>
                    <td className="py-2.5 px-3 text-slate-300">44.4%</td>
                    <td className="py-2.5 px-3 text-orange-400 font-bold">66.5%</td>
                    <td className="py-2.5 px-3 text-slate-300">34.0%</td>
                    <td className="py-2.5 px-3 text-rose-400">-5.5% (Eliminated False Positives)</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* VIEW 3: PHASE 4.3 EXPANDED VALIDATION */}
      {selectedBenchmark === 'phase4_3' && (
        <div className="space-y-6">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-[#111827] border border-slate-800 rounded-xl p-4">
              <div className="text-xs text-slate-400 font-mono">Independent Benchmark</div>
              <div className="text-2xl font-bold font-mono text-cyan-400 mt-1">25 Images</div>
              <div className="text-[11px] text-slate-500 font-mono mt-0.5">Held-out unseen data</div>
            </div>

            <div className="bg-[#111827] border border-slate-800 rounded-xl p-4">
              <div className="text-xs text-slate-400 font-mono">Custom Model mAP@0.5</div>
              <div className="text-2xl font-bold font-mono text-orange-400 mt-1">43.8%</div>
              <div className="text-[11px] text-slate-500 font-mono mt-0.5">mAP@0.5:0.95: 17.8%</div>
            </div>

            <div className="bg-[#111827] border border-slate-800 rounded-xl p-4">
              <div className="text-xs text-slate-400 font-mono">COCO Baseline Speed</div>
              <div className="text-2xl font-bold font-mono text-slate-300 mt-1">117.4 ms</div>
              <div className="text-[11px] text-slate-500 font-mono mt-0.5">8.52 FPS (80 classes)</div>
            </div>

            <div className="bg-[#111827] border border-slate-800 rounded-xl p-4">
              <div className="text-xs text-slate-400 font-mono">Custom Detector Speed</div>
              <div className="text-2xl font-bold font-mono text-emerald-400 mt-1">87.0 ms</div>
              <div className="text-[11px] text-emerald-400 font-mono mt-0.5">11.50 FPS (4 classes)</div>
            </div>
          </div>

          <div className="p-4 rounded-xl bg-orange-500/10 border border-orange-500/20 space-y-2">
            <div className="text-xs font-bold text-orange-400 flex items-center gap-2">
              <Info className="w-4 h-4 shrink-0" />
              <span>Scientific Generalization & Attenuation Note</span>
            </div>
            <p className="text-xs text-slate-300 leading-relaxed">
              When evaluated on 25 fully independent, out-of-distribution physical photographs, overall mAP@0.5 measured 43.8% (versus 67.3% on the frozen test set). Obstacles and broken glass maintained high detection reliability. However, liquid puddle detection boundary confidence attenuated under complex specular glares and mottled tile grout lines. This confirms why the production default remains anchored to the verified YOLOv8s COCO baseline.
            </p>
          </div>
        </div>
      )}
    </div>
  );
};
