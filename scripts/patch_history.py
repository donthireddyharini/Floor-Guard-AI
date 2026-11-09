import os

def patch_image_detection():
    path = os.path.join('src', 'components', 'ImageDetectionWorkspace.tsx')
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    if 'saveLocalHistoryItem' in content:
        print('ImageDetectionWorkspace already patched')
        return

    # Add import
    content = content.replace(
        "import { DetectionItem } from '../types';",
        "import { DetectionItem } from '../types';\nimport { saveLocalHistoryItem } from '../utils/historyStore';"
    )

    # In handleFileUpload:
    old_upload = """      if (res.ok && data.status === 'ok' && data.detection) {
        setCustomResult(data.detection);
        setActiveMode('custom');
      } else {"""

    new_upload = """      if (res.ok && data.status === 'ok' && data.detection) {
        setCustomResult(data.detection);
        setActiveMode('custom');

        // Automatically store inspection in persistent Hazard History
        const detRecord = data.detection;
        if (detRecord.detections && detRecord.detections.length > 0) {
          detRecord.detections.forEach((sub: any, sIdx: number) => {
            saveLocalHistoryItem({
              id: `det_${Date.now()}_${sIdx}`,
              detection_run_id: data.run_id || `run_${Date.now()}`,
              class_name: sub.class_name || detRecord.class_name || 'Hazard',
              confidence: typeof sub.confidence === 'number' ? sub.confidence : detRecord.confidence,
              severity: sub.severity || detRecord.severity || 'Medium',
              estimated_area: parseFloat(detRecord.area) || 0.25,
              evidence_path: detRecord.annotated_image_url || detRecord.image_url || localPreview,
              location: detRecord.location || 'Monitored Walkway',
              source_type: 'image',
              original_filename: file.name,
              created_at: new Date().toISOString(),
              summary: sub.recommendation || detRecord.recommendation || `Detected ${sub.class_name}`
            });
          });
        } else {
          saveLocalHistoryItem({
            id: detRecord.id || `det_${Date.now()}`,
            detection_run_id: data.run_id || `run_${Date.now()}`,
            class_name: detRecord.class_name,
            confidence: detRecord.confidence,
            severity: detRecord.severity,
            estimated_area: parseFloat(detRecord.area) || 0.32,
            evidence_path: detRecord.annotated_image_url || detRecord.image_url || localPreview,
            location: detRecord.location || 'Monitored Walkway',
            source_type: 'image',
            original_filename: file.name,
            created_at: new Date().toISOString(),
            summary: detRecord.recommendation || `Detected ${detRecord.class_name}`
          });
        }
      } else {"""

    content = content.replace(old_upload, new_upload)

    # In handleSelectPreset:
    old_preset = """        if (res.ok && data.status === 'ok' && data.detection) {
          setCustomResult(data.detection);
        } else {"""

    new_preset = """        if (res.ok && data.status === 'ok' && data.detection) {
          setCustomResult(data.detection);

          // Store preset hazard in history
          const pDet = data.detection;
          saveLocalHistoryItem({
            id: `det_preset_${Date.now()}`,
            detection_run_id: `run_preset_${Date.now()}`,
            class_name: pDet.class_name,
            confidence: pDet.confidence,
            severity: pDet.severity,
            estimated_area: parseFloat(pDet.area) || 0.28,
            evidence_path: samplePath,
            location: presets[key]?.location || 'Monitored Walkway',
            source_type: 'image',
            original_filename: `${key}_sample.jpg`,
            created_at: new Date().toISOString(),
            summary: pDet.recommendation || `Detected ${pDet.class_name}`
          });
        } else {"""

    content = content.replace(old_preset, new_preset)

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print('ImageDetectionWorkspace patched cleanly')

def patch_video_analysis():
    path = os.path.join('src', 'components', 'VideoAnalysisView.tsx')
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    if 'saveLocalHistoryItem' in content:
        print('VideoAnalysisView already patched')
        return

    content = content.replace(
        "import { VideoAnalysisRecord, KeyframeItem } from '../types';",
        "import { VideoAnalysisRecord, KeyframeItem } from '../types';\nimport { saveLocalHistoryItem } from '../utils/historyStore';"
    )

    old_va = """        if (va.keyframes && va.keyframes.length > 0) {
          setKeyframes(va.keyframes);
          setSelectedKeyframe(0);
          setHasAnalyzed(true);
          setShowOverlay(true);
        }"""

    new_va = """        if (va.keyframes && va.keyframes.length > 0) {
          setKeyframes(va.keyframes);
          setSelectedKeyframe(0);
          setHasAnalyzed(true);
          setShowOverlay(true);

          // Record each detected hazard keyframe to persistent Hazard History
          va.keyframes.forEach((kf: any, kIdx: number) => {
            if (kf.severity && kf.severity !== 'Safe') {
              saveLocalHistoryItem({
                id: `det_vid_${Date.now()}_${kIdx}`,
                detection_run_id: data.run_id || `run_vid_${Date.now()}`,
                class_name: kf.detected_class || kf.class_name || 'Hazard',
                confidence: kf.confidence || 0.9,
                severity: kf.severity || 'Medium',
                estimated_area: 0.25,
                evidence_path: kf.annotated_image_url || kf.thumb || '/assets/samples/thumb_water_spill.jpg',
                location: `Video @ ${kf.timestamp || '00:00'} (${file.name})`,
                source_type: 'video',
                original_filename: file.name,
                created_at: new Date().toISOString(),
                summary: `Video hazard: ${kf.detected_class || kf.class_name} detected at frame ${kf.frame || kIdx}`
              });
            }
          });
        }"""

    content = content.replace(old_va, new_va)

    old_tour = """        if (va.keyframes && va.keyframes.length > 0) {
          setKeyframes(va.keyframes);
          setSelectedKeyframe(0);
        }
        setHasAnalyzed(true);
        setShowOverlay(true);
        loadVideoHistory();"""

    new_tour = """        if (va.keyframes && va.keyframes.length > 0) {
          setKeyframes(va.keyframes);
          setSelectedKeyframe(0);

          // Record tour keyframes to persistent Hazard History
          va.keyframes.forEach((kf: any, kIdx: number) => {
            if (kf.severity && kf.severity !== 'Safe') {
              saveLocalHistoryItem({
                id: `det_tour_${Date.now()}_${kIdx}`,
                detection_run_id: `run_tour_${Date.now()}`,
                class_name: kf.detected_class || kf.class_name || 'Hazard',
                confidence: kf.confidence || 0.95,
                severity: kf.severity || 'High',
                estimated_area: 0.35,
                evidence_path: kf.annotated_image_url || kf.thumb || '/assets/samples/thumb_water_spill.jpg',
                location: `Patrol Tour @ ${kf.timestamp || '00:00'}`,
                source_type: 'video',
                original_filename: 'corridor_hazard_tour_30s.mp4',
                created_at: new Date().toISOString(),
                summary: `Sample Tour hazard: ${kf.detected_class || kf.class_name} at ${kf.timestamp}`
              });
            }
          });
        }
        setHasAnalyzed(true);
        setShowOverlay(true);
        loadVideoHistory();"""

    content = content.replace(old_tour, new_tour)

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print('VideoAnalysisView patched cleanly')

patch_image_detection()
patch_video_analysis()
