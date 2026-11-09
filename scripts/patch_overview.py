with open('src/components/OverviewDashboard.tsx', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Update Card 1 fallback and subtext
text = text.replace(
    "{analyticsData?.dataset_summary?.total_curated_images || 160}",
    "{analyticsData?.dataset_summary?.total_curated_images || 141}"
)
text = text.replace(
    "<span>82 Train / 18 Val / 16 Test</span>",
    "<span>112 Train / 15 Val / 14 Test</span>"
)

# 2. Update Card 2
text = text.replace(
    "<span>141 Verified Ground Truth Boxes</span>",
    "<span>160 Verified Ground Truth Boxes</span>"
)

# 3. Add onError to main detection image
old_img = """              <img
                src={activeData.image}
                alt={activeData.title}
                className="w-full h-full object-fill transition-transform duration-300"
              />"""

new_img = """              <img
                src={activeData.image}
                alt={activeData.title}
                onError={(e) => {
                  (e.currentTarget as HTMLImageElement).onerror = null;
                  (e.currentTarget as HTMLImageElement).src = '/assets/samples/thumb_water_spill.jpg';
                }}
                className="w-full h-full object-fill transition-transform duration-300"
              />"""
text = text.replace(old_img, new_img)

# 4. Add onError to sample buttons
old_thumb = """                  <div className="relative rounded-md overflow-hidden aspect-21/9 mb-1.5 bg-black">
                    <img src={s.thumb} alt={s.title} className="w-full h-full object-cover" />"""

new_thumb = """                  <div className="relative rounded-md overflow-hidden aspect-21/9 mb-1.5 bg-black">
                    <img
                      src={s.thumb}
                      alt={s.title}
                      onError={(e) => {
                        (e.currentTarget as HTMLImageElement).onerror = null;
                        (e.currentTarget as HTMLImageElement).src = '/assets/samples/thumb_water_spill.jpg';
                      }}
                      className="w-full h-full object-cover"
                    />"""
text = text.replace(old_thumb, new_thumb)

# 5. Fix safe navigation for activeData
old_active = """  const activeData = customDetection
    ? {
        ...customDetection,
        title: customDetection.class_name,
        className: customDetection.class_name.toUpperCase(),
        confidence: Math.round(customDetection.confidence * 100),
        riskLevel: customDetection.severity === 'Safe' ? 'SAFE' : `${customDetection.severity.toUpperCase()} RISK`,
        riskColor: customDetection.severity === 'Critical' ? 'bg-[#ef4444] text-white' : 'bg-[#f59e0b] text-white',
        area: customDetection.area || '0.35 m²',
        targetType: 'Floor Surface',
        alert: customDetection.recommendation || `Detected ${customDetection.class_name}.`,
        image: customDetection.image_url,
        thumb: customDetection.image_url,
        bbox: getCustomBbox(customDetection),
        polygonPath: '',
        subtitle: `Detected at ${new Date().toLocaleTimeString()}`
      }
    : {
        ...samples[selectedSample],
        bbox: samples[selectedSample].bbox,
        polygonPath: samples[selectedSample].polygonPath,
        subtitle: samples[selectedSample].subtitle
      };"""

new_active = """  const activeData = customDetection
    ? {
        ...customDetection,
        title: customDetection.class_name || 'Floor Hazard',
        className: (customDetection.class_name || 'Floor Hazard').toUpperCase(),
        confidence: Math.round((customDetection.confidence || 0.9) * 100),
        riskLevel: (customDetection.severity === 'Safe' || customDetection.class_name === 'Clean Floor')
          ? 'SAFE'
          : `${(customDetection.severity || 'Medium').toUpperCase()} RISK`,
        riskColor: customDetection.severity === 'Critical' ? 'bg-[#ef4444] text-white' : 'bg-[#f59e0b] text-white',
        area: customDetection.area || '0.35 m²',
        targetType: 'Floor Surface',
        alert: customDetection.recommendation || `Detected ${customDetection.class_name || 'Floor Hazard'}.`,
        image: customDetection.image_url || '/assets/samples/thumb_water_spill.jpg',
        thumb: customDetection.image_url || '/assets/samples/thumb_water_spill.jpg',
        bbox: getCustomBbox(customDetection),
        polygonPath: '',
        subtitle: `Detected at ${new Date().toLocaleTimeString()}`
      }
    : {
        ...(samples[selectedSample] || samples.water),
        bbox: (samples[selectedSample] || samples.water).bbox,
        polygonPath: (samples[selectedSample] || samples.water).polygonPath,
        subtitle: (samples[selectedSample] || samples.water).subtitle
      };"""

text = text.replace(old_active, new_active)

# 6. Update Verified Dataset Classes Chips
chips_old = """              <div className="flex flex-wrap gap-1.5">
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
                </span>"""

chips_new = """              <div className="flex flex-wrap gap-1.5">
                <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-[#13281c] text-[#22c55e] border border-[#22c55e]/40">
                  Clean Floor (11 Controls)
                </span>
                <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-[#162734] text-[#06b6d4] border border-[#06b6d4]/40">
                  Water Spill (24 Boxes)
                </span>
                <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-[#23172e] text-[#8b5cf6] border border-[#8b5cf6]/40">
                  Obstacle / Debris (21 Boxes)
                </span>
                <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-[#1e293b] text-[#94a3b8] border border-[#94a3b8]/40">
                  Trash / Litter (18 Boxes)
                </span>
                <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-[#2a2216] text-[#f59e0b] border border-[#f59e0b]/40">
                  Oil Spill (13 Boxes)
                </span>
                <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-[#2a171a] text-[#ef4444] border border-[#ef4444]/40">
                  Broken Glass (10 Boxes)
                </span>
                <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-[#2d1b28] text-[#ec4899] border border-[#ec4899]/40">
                  Cable / Cord (9 Boxes)
                </span>
                <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-[#2b1f13] text-[#eab308] border border-[#eab308]/40">
                  Food Waste (8 Boxes)
                </span>
                <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-[#3b1d16] text-[#f97316] border border-[#f97316]/40">
                  Floor Damage (7 Boxes)
                </span>
                <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-[#1e1e38] text-[#818cf8] border border-[#818cf8]/40">
                  Chemical Spill (6 Boxes)
                </span>
                <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-[#162a22] text-[#34d399] border border-[#34d399]/40">
                  Mat Hazard (6 Boxes)
                </span>
                <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-[#281636] text-[#c084fc] border border-[#c084fc]/40">
                  Mud / Dirt (4 Boxes)
                </span>
                <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-[#142828] text-[#2dd4bf] border border-[#2dd4bf]/40">
                  Stairs Hazard (4 Boxes)
                </span>"""

text = text.replace(chips_old, chips_new)
text = text.replace("12 Hazard Classes + 9 Controls", "12 Hazard Classes + 11 Controls")

with open('src/components/OverviewDashboard.tsx', 'w', encoding='utf-8') as f:
    f.write(text)
print("Updated OverviewDashboard.tsx successfully!")
