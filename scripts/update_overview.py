import os
import re

def update_overview_dashboard():
    path = os.path.join('src', 'components', 'OverviewDashboard.tsx')
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Update text header description
    old_desc = """            Unified detector trained on <strong>{analyticsData?.dataset_summary?.total_curated_images || 116}</strong> multi-hazard indoor images (<strong>{analyticsData?.dataset_summary?.total_annotations || 204}</strong> ground-truth annotations) across 4 hazard classes + 22 clean floor controls."""
    new_desc = """            Unified detector trained on <strong>{analyticsData?.dataset_summary?.total_curated_images || 121}</strong> multi-hazard indoor images (<strong>{analyticsData?.dataset_summary?.total_annotations || 141}</strong> ground-truth annotations) across 12 hazard classes + 9 clean floor controls."""
    content = content.replace(old_desc, new_desc)

    # 2. Update quick chips
    old_chips = """            <span className="font-bold text-white">{analyticsData?.dataset_summary?.total_curated_images || 116} Imgs</span>"""
    new_chips = """            <span className="font-bold text-white">{analyticsData?.dataset_summary?.total_curated_images || 121} Imgs</span>"""
    content = content.replace(old_chips, new_chips)

    old_ann = """            <span className="font-bold text-[#38bdf8]">{analyticsData?.dataset_summary?.total_annotations || 204} Boxes</span>"""
    new_ann = """            <span className="font-bold text-[#38bdf8]">{analyticsData?.dataset_summary?.total_annotations || 141} Boxes</span>"""
    content = content.replace(old_ann, new_ann)

    old_splits = """              {analyticsData?.dataset_summary?.splits?.train || 82} / {analyticsData?.dataset_summary?.splits?.val || 18} / {analyticsData?.dataset_summary?.splits?.test || 16}"""
    new_splits = """              {analyticsData?.dataset_summary?.splits?.train || 96} / {analyticsData?.dataset_summary?.splits?.val || 12} / {analyticsData?.dataset_summary?.splits?.test || 13}"""
    content = content.replace(old_splits, new_splits)

    # 3. Update KPI Card 1 & 2
    content = content.replace(
        "{analyticsData?.dataset_summary?.total_curated_images || 116}",
        "{analyticsData?.dataset_summary?.total_curated_images || 121}"
    )
    content = content.replace(
        "116 Verified Inspection Images",
        "121 Curated Dataset Images (Zero Leakage)"
    )
    content = content.replace(
        "{analyticsData?.dataset_summary?.total_annotations || 204}",
        "{analyticsData?.dataset_summary?.total_annotations || 141}"
    )
    content = content.replace(
        "204 Verified Ground Truth Boxes",
        "141 Verified Ground Truth Boxes"
    )

    # 4. Donut Chart replacement
    target_donut = """            {/* Donut Chart with Center Total */}
            <div className="flex items-center justify-center py-2">
              <div className="relative w-44 h-44 flex items-center justify-center">
                <svg className="w-full h-full -rotate-90" viewBox="0 0 100 100">
                  {/* Broken Glass (60.8% = 145.2 / 238.8) */}
                  <circle
                    cx="50"
                    cy="50"
                    r="38"
                    fill="transparent"
                    stroke="#ef4444"
                    strokeWidth="14"
                    strokeDasharray="145.2 238.8"
                    strokeDashoffset="0"
                  />
                  {/* Water Spill (15.7% = 37.5 / 238.8) */}
                  <circle
                    cx="50"
                    cy="50"
                    r="38"
                    fill="transparent"
                    stroke="#06b6d4"
                    strokeWidth="14"
                    strokeDasharray="37.5 238.8"
                    strokeDashoffset="-145.2"
                  />
                  {/* Oil Spill (11.8% = 28.2 / 238.8) */}
                  <circle
                    cx="50"
                    cy="50"
                    r="38"
                    fill="transparent"
                    stroke="#f59e0b"
                    strokeWidth="14"
                    strokeDasharray="28.2 238.8"
                    strokeDashoffset="-182.7"
                  />
                  {/* Obstacles (11.8% = 28.2 / 238.8) */}
                  <circle
                    cx="50"
                    cy="50"
                    r="38"
                    fill="transparent"
                    stroke="#8b5cf6"
                    strokeWidth="14"
                    strokeDasharray="28.2 238.8"
                    strokeDashoffset="-210.9"
                  />
                </svg>

                {/* Donut Center */}
                <div className="absolute text-center">
                  <div className="text-2xl font-black text-white font-mono tracking-tight">{analyticsData?.hazard_distribution?.total || 204}</div>
                  <div className="text-[10px] text-slate-400 font-medium">Annotations</div>
                </div>
              </div>
            </div>

            {/* Donut Legend */}
            <div className="space-y-2 text-xs font-mono pt-1">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full bg-[#ef4444]" />
                  <span className="text-slate-300 font-sans">Broken Glass</span>
                </div>
                <div className="flex items-center gap-4">
                  <span className="font-bold text-white">61%</span>
                  <span className="text-slate-400 w-8 text-right">124</span>
                </div>
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full bg-[#06b6d4]" />
                  <span className="text-slate-300 font-sans">Water Spill</span>
                </div>
                <div className="flex items-center gap-4">
                  <span className="font-bold text-white">16%</span>
                  <span className="text-slate-400 w-8 text-right">32</span>
                </div>
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full bg-[#f59e0b]" />
                  <span className="text-slate-300 font-sans">Oil Spill</span>
                </div>
                <div className="flex items-center gap-4">
                  <span className="font-bold text-white">12%</span>
                  <span className="text-slate-400 w-8 text-right">24</span>
                </div>
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full bg-[#8b5cf6]" />
                  <span className="text-slate-300 font-sans">Obstacles</span>
                </div>
                <div className="flex items-center gap-4">
                  <span className="font-bold text-white">12%</span>
                  <span className="text-slate-400 w-8 text-right">24</span>
                </div>
              </div>
            </div>"""

    replacement_donut = """            {/* Donut Chart with Center Total */}
            {(() => {
              const defaultDistribution = [
                { name: 'Broken Glass', count: 32, percentage: 23, color: '#ef4444' },
                { name: 'Water Spill', count: 23, percentage: 16, color: '#06b6d4' },
                { name: 'Obstacle / Debris', count: 17, percentage: 12, color: '#8b5cf6' },
                { name: 'Oil Spill', count: 14, percentage: 10, color: '#f59e0b' },
                { name: 'Trash / Litter', count: 13, percentage: 9, color: '#64748b' },
                { name: 'Food Waste', count: 9, percentage: 6, color: '#eab308' },
                { name: 'Cable / Cord', count: 8, percentage: 6, color: '#ec4899' },
                { name: 'Floor Damage', count: 7, percentage: 5, color: '#f97316' },
                { name: 'Mat Hazard', count: 5, percentage: 4, color: '#10b981' },
                { name: 'Chemical Spill', count: 4, percentage: 3, color: '#6366f1' },
                { name: 'Stairs Hazard', count: 4, percentage: 3, color: '#14b8a6' },
                { name: 'Mud / Dirt', count: 3, percentage: 2, color: '#a855f7' },
                { name: 'Clean Floor (Control)', count: 9, percentage: 6, color: '#22c55e' }
              ];
              const distItems = (analyticsData?.hazard_distribution?.items && analyticsData.hazard_distribution.items.length > 0)
                ? analyticsData.hazard_distribution.items
                : defaultDistribution;
              const totalAnn = analyticsData?.hazard_distribution?.total || 141;

              // Circumference of r=38
              const C = 238.76;
              let accumulated = 0;

              return (
                <div>
                  <div className="flex items-center justify-center py-2">
                    <div className="relative w-44 h-44 flex items-center justify-center">
                      <svg className="w-full h-full -rotate-90" viewBox="0 0 100 100">
                        {distItems.slice(0, 8).map((item: any, idx: number) => {
                          const sliceLen = (Math.max(1, item.percentage || 4) / 100) * C;
                          const offset = -accumulated;
                          accumulated += sliceLen;
                          return (
                            <circle
                              key={`slice-${idx}`}
                              cx="50"
                              cy="50"
                              r="38"
                              fill="transparent"
                              stroke={item.color || '#22c55e'}
                              strokeWidth="14"
                              strokeDasharray={`${sliceLen.toFixed(1)} ${(C - sliceLen).toFixed(1)}`}
                              strokeDashoffset={offset.toFixed(1)}
                            />
                          );
                        })}
                      </svg>

                      {/* Donut Center */}
                      <div className="absolute text-center">
                        <div className="text-2xl font-black text-white font-mono tracking-tight">{totalAnn}</div>
                        <div className="text-[10px] text-slate-400 font-medium">Annotations</div>
                      </div>
                    </div>
                  </div>

                  {/* Donut Legend */}
                  <div className="space-y-1.5 text-xs font-mono pt-1 max-h-48 overflow-y-auto pr-1">
                    {distItems.slice(0, 7).map((item: any, idx: number) => (
                      <div key={`legend-${idx}`} className="flex items-center justify-between py-0.5">
                        <div className="flex items-center gap-2">
                          <span className="w-2.5 h-2.5 rounded-full shrink-0" style={{ backgroundColor: item.color }} />
                          <span className="text-slate-300 font-sans truncate max-w-[130px]">{item.name}</span>
                        </div>
                        <div className="flex items-center gap-3">
                          <span className="font-bold text-white">{item.percentage}%</span>
                          <span className="text-slate-400 w-8 text-right font-mono">{item.count}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              );
            })()}"""

    if target_donut in content:
        content = content.replace(target_donut, replacement_donut)
        print('Updated Donut Chart in OverviewDashboard.tsx')
    else:
        print('Warning: target_donut not found in OverviewDashboard.tsx')

    # 5. Verified Dataset Classes Chips
    target_chips = """              <div className="text-[11px] text-slate-400 mb-1.5 font-medium flex items-center justify-between">
                <span>Verified Dataset Classes</span>
                <span className="font-mono text-[10px] text-slate-500">
                  12 Hazard Classes + 22 Controls
                </span>
              </div>
              <div className="flex flex-wrap gap-1.5">
                <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-[#13281c] text-[#22c55e] border border-[#22c55e]/40">
                  Clean Floor (22 Controls)
                </span>
                <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-[#2a171a] text-[#ef4444] border border-[#ef4444]/40">
                  Floor Crack (16 Boxes)
                </span>
                <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-[#162734] text-[#06b6d4] border border-[#06b6d4]/40">
                  Improper Mat (15 Boxes)
                </span>
                <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-[#23172e] text-[#8b5cf6] border border-[#8b5cf6]/40">
                  Cable / Wire (20 Boxes)
                </span>
                <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-[#2a2216] text-[#f59e0b] border border-[#f59e0b]/40">
                  Water Spill (44 Boxes)
                </span>
                <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-[#2a171a] text-[#ef4444] border border-[#ef4444]/40">
                  Oil Spill (30 Boxes)
                </span>
                <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-[#1a2333] text-[#38bdf8] border border-[#38bdf8]/40">
                  Broken Glass (130 Boxes)
                </span>
                <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-[#2b1f13] text-[#f97316] border border-[#f97316]/40">
                  Food Waste (14 Boxes)
                </span>
                <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-[#1c261e] text-[#10b981] border border-[#10b981]/40">
                  Chemical Spill (12 Boxes)
                </span>
              </div>"""

    replacement_chips = """              <div className="text-[11px] text-slate-400 mb-1.5 font-medium flex items-center justify-between">
                <span>Verified Dataset Classes</span>
                <span className="font-mono text-[10px] text-slate-500">
                  12 Hazard Classes + 9 Controls
                </span>
              </div>
              <div className="flex flex-wrap gap-1.5">
                <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-[#13281c] text-[#22c55e] border border-[#22c55e]/40">
                  Clean Floor (9 Controls)
                </span>
                <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-[#2a171a] text-[#ef4444] border border-[#ef4444]/40">
                  Broken Glass (32 Boxes)
                </span>
                <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-[#162734] text-[#06b6d4] border border-[#06b6d4]/40">
                  Water Spill (23 Boxes)
                </span>
                <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-[#23172e] text-[#8b5cf6] border border-[#8b5cf6]/40">
                  Obstacle / Debris (17 Boxes)
                </span>
                <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-[#2a2216] text-[#f59e0b] border border-[#f59e0b]/40">
                  Oil Spill (14 Boxes)
                </span>
                <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-[#1e293b] text-[#94a3b8] border border-[#94a3b8]/40">
                  Trash / Litter (13 Boxes)
                </span>
                <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-[#2b1f13] text-[#eab308] border border-[#eab308]/40">
                  Food Waste (9 Boxes)
                </span>
                <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-[#2d1b28] text-[#ec4899] border border-[#ec4899]/40">
                  Cable / Cord (8 Boxes)
                </span>
                <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-[#2c1c14] text-[#f97316] border border-[#f97316]/40">
                  Floor Damage (7 Boxes)
                </span>
                <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-[#162920] text-[#10b981] border border-[#10b981]/40">
                  Mat Hazard (5 Boxes)
                </span>
                <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-[#1c261e] text-[#6366f1] border border-[#6366f1]/40">
                  Chemical Spill (4 Boxes)
                </span>
                <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-[#13282c] text-[#14b8a6] border border-[#14b8a6]/40">
                  Stairs Hazard (4 Boxes)
                </span>
                <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-[#24172f] text-[#a855f7] border border-[#a855f7]/40">
                  Mud / Dirt (3 Boxes)
                </span>
              </div>"""

    if target_chips in content:
        content = content.replace(target_chips, replacement_chips)
        print('Updated Dataset Classes Chips in OverviewDashboard.tsx')
    else:
        print('Warning: target_chips not found in OverviewDashboard.tsx')

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

update_overview_dashboard()

def update_server_summary():
    path = 'server.ts'
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    target = """    const totalImages = cleanSummary?.total?.images || 268;
    const totalBoxes = cleanSummary?.total?.bounding_boxes || 374;
    const cleanNegatives = cleanSummary?.total?.clean_floor_negatives || 22;
    const hazardImages = cleanSummary?.total?.hazard_images || 246;

    // Hazard distribution dynamically calculated from verified 12-class dataset
    const classCounts = cleanSummary?.total?.boxes_per_class || {};
    const distributionColors: Record<string, string> = {
      'broken_glass': '#ef4444',
      'obstacle_debris': '#8b5cf6',
      'water_spill': '#06b6d4',
      'oil_spill': '#f59e0b',
      'cable_cord': '#ec4899',
      'food_waste': '#eab308',
      'floor_crack': '#f97316',
      'improper_mat': '#10b981',
      'mud_dirt': '#a855f7',
      'chemical_spill': '#6366f1',
      'trash_litter': '#64748b',
      'stairs_hazard': '#14b8a6'
    };

    const classPrettyNames: Record<string, string> = {
      'broken_glass': 'Broken Glass',
      'obstacle_debris': 'Obstacle / Debris',
      'water_spill': 'Water Spill',
      'oil_spill': 'Oil Spill',
      'cable_cord': 'Cable / Cord',
      'food_waste': 'Food Waste',
      'floor_crack': 'Floor Crack',
      'improper_mat': 'Improper Floor Mat',
      'mud_dirt': 'Mud / Dirt',
      'chemical_spill': 'Chemical Spill',
      'trash_litter': 'Trash / Litter',
      'stairs_hazard': 'Stairs Hazard'
    };"""

    replacement = """    const totalImages = cleanSummary?.total?.images || 121;
    const totalBoxes = cleanSummary?.total?.bounding_boxes || 141;
    const cleanNegatives = cleanSummary?.total?.clean_floor_negatives || 9;
    const hazardImages = cleanSummary?.total?.hazard_images || 112;

    // Hazard distribution dynamically calculated from verified 12-class dataset
    const classCounts = cleanSummary?.total?.boxes_per_class || {};
    const distributionColors: Record<string, string> = {
      'broken_glass': '#ef4444',
      'obstacle_debris': '#8b5cf6',
      'water_spill': '#06b6d4',
      'oil_spill': '#f59e0b',
      'cable_cord': '#ec4899',
      'food_waste': '#eab308',
      'floor_crack': '#f97316',
      'floor_damage': '#f97316',
      'improper_mat': '#10b981',
      'mat_hazard': '#10b981',
      'mud_dirt': '#a855f7',
      'chemical_spill': '#6366f1',
      'trash_litter': '#64748b',
      'stairs_hazard': '#14b8a6',
      'stair_hazard': '#14b8a6',
      'clean_floor': '#22c55e'
    };

    const classPrettyNames: Record<string, string> = {
      'broken_glass': 'Broken Glass',
      'obstacle_debris': 'Obstacle / Debris',
      'water_spill': 'Water Spill',
      'oil_spill': 'Oil Spill',
      'cable_cord': 'Cable / Cord',
      'food_waste': 'Food Waste',
      'floor_crack': 'Floor Damage',
      'floor_damage': 'Floor Damage',
      'improper_mat': 'Mat Hazard',
      'mat_hazard': 'Mat Hazard',
      'mud_dirt': 'Mud / Dirt',
      'chemical_spill': 'Chemical Spill',
      'trash_litter': 'Trash / Litter',
      'stairs_hazard': 'Stairs Hazard',
      'stair_hazard': 'Stairs Hazard',
      'clean_floor': 'Clean Floor (Control)'
    };"""

    if target in content:
        content = content.replace(target, replacement)
        print('Updated server.ts summary numbers & class mapping')
    else:
        print('Warning: target in server.ts not found')

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

update_server_summary()
