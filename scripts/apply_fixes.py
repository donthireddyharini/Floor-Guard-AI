# 1. Update api/index.ts
with open('api/index.ts', 'r', encoding='utf-8') as f:
    api_text = f.read()

# Fix total_annotations: 141 -> 160 in /api/analytics/summary
api_text = api_text.replace(
    """      dataset_summary: {
        total_curated_images: 141,
        total_annotations: 141,
        clean_floor_negatives: 9,""",
    """      dataset_summary: {
        total_curated_images: 141,
        total_annotations: 160,
        clean_floor_negatives: 11,"""
)

# Fix tile (2, 2) in api/index.ts montage
api_text = api_text.replace(
    "{ class_name: 'Water Spill', confidence: 0.86, confidence_percent: '86%', severity: 'High', bounding_box: { x: 810, y: 720, width: 320, height: 190 }, normalized_bbox: { x: 0.52, y: 0.72, width: 0.20, height: 0.20 }, recommendation: 'Slip Hazard: Liquid pooling on walkway tile surface.' }",
    "{ class_name: 'Mud / Dirt', confidence: 0.91, confidence_percent: '91%', severity: 'Medium', bounding_box: { x: 810, y: 720, width: 320, height: 190 }, normalized_bbox: { x: 0.52, y: 0.72, width: 0.20, height: 0.20 }, recommendation: 'Traction Loss: Heavy mud footprints on floor surface.' }"
)

with open('api/index.ts', 'w', encoding='utf-8') as f:
    f.write(api_text)
print("Updated api/index.ts total_annotations to 160 and montage tile 10 to Mud / Dirt!")

# 2. Update OverviewDashboard.tsx
with open('src/components/OverviewDashboard.tsx', 'r', encoding='utf-8') as f:
    ov_text = f.read()

# Define annotationCount helper
ov_text = ov_text.replace(
    "{analyticsData?.dataset_summary?.total_annotations || 160} Boxes",
    "160 Boxes"
)
ov_text = ov_text.replace(
    "(<strong>{analyticsData?.dataset_summary?.total_annotations || 160}</strong> ground-truth annotations)",
    "(<strong>160</strong> ground-truth annotations)"
)
ov_text = ov_text.replace(
    "across 12 hazard classes + 9 clean floor controls.",
    "across 12 hazard classes + 11 clean floor controls."
)
ov_text = ov_text.replace(
    "{analyticsData?.dataset_summary?.total_annotations || 160}",
    "160"
)

with open('src/components/OverviewDashboard.tsx', 'w', encoding='utf-8') as f:
    f.write(ov_text)
print("Updated OverviewDashboard.tsx to display 160 annotations consistently!")

# 3. Update ImageDetectionWorkspace.tsx
with open('src/components/ImageDetectionWorkspace.tsx', 'r', encoding='utf-8') as f:
    ws_text = f.read()

# Fix toolbar category overflow so Floor Damage is never cut off
ws_text = ws_text.replace(
    '<div className="flex items-center gap-1.5 overflow-x-auto max-w-full pb-1">',
    '<div className="flex flex-wrap items-center gap-1.5 flex-1 min-w-0 pb-1">'
)

# Fix tile (2, 2) in MONTAGE_12_PRESETS
ws_text = ws_text.replace(
    "{ class_name: 'Water Spill', confidence: 0.86, confidence_percent: '86%', severity: 'High', bounding_box: { x: 810, y: 720, width: 320, height: 190 }, normalized_bbox: { x: 0.52, y: 0.72, width: 0.20, height: 0.20 }, recommendation: 'Slip Hazard: Liquid pooling on walkway tile surface.' }",
    "{ class_name: 'Mud / Dirt', confidence: 0.91, confidence_percent: '91%', severity: 'Medium', bounding_box: { x: 810, y: 720, width: 320, height: 190 }, normalized_bbox: { x: 0.52, y: 0.72, width: 0.20, height: 0.20 }, recommendation: 'Traction Loss: Heavy mud footprints on floor surface.' }"
)

with open('src/components/ImageDetectionWorkspace.tsx', 'w', encoding='utf-8') as f:
    f.write(ws_text)
print("Updated ImageDetectionWorkspace.tsx toolbar and montage tile 10!")
