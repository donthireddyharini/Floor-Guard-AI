import os

def update_image_detection_workspace():
    path = os.path.join('src', 'components', 'ImageDetectionWorkspace.tsx')
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Import
    if 'saveLocalHistoryItem' not in content:
        content = content.replace(
            "import { DetectionItem } from '../types';",
            "import { DetectionItem } from '../types';\nimport { saveLocalHistoryItem } from '../utils/historyStore';"
        )

    # 2. Add history in handleFileUpload
    target_upload = """      if (res.ok && data.status === 'ok' && data.detection) {
        setCustomResult(data.detection);
        setActiveMode('custom');"""

    replacement_upload = """      if (res.ok && data.status === 'ok' && data.detection) {
        setCustomResult(data.detection);
        setActiveMode('custom');

        // Automatically store inspection in persistent Hazard History
        const det = data.detection;
        if (det.detections && det.detections.length > 0) {
          det.detections.forEach((sub: any, sIdx: number) => {
            saveLocalHistoryItem({
              id: `det_${Date.now()}_${sIdx}`,
              detection_run_id: data.run_id || `run_${Date.now()}`,
              class_name: sub.class_name || det.class_name || 'Hazard',
              confidence: typeof sub.confidence === 'number' ? sub.confidence : det.confidence,
              severity: sub.severity || det.severity || 'Medium',
              estimated_area: parseFloat(det.area) || 0.25,
              evidence_path: det.annotated_image_url || det.image_url || localPreview,
              location: det.location || 'Monitored Walkway',
              source_type: 'image',
              original_filename: file.name,
              created_at: new Date().toISOString(),
              summary: sub.recommendation || det.recommendation || `Detected ${sub.class_name}`
            });
          });
        } else {
          saveLocalHistoryItem({
            id: det.id || `det_${Date.now()}`,
            detection_run_id: data.run_id || `run_${Date.now()}`,
            class_name: det.class_name,
            confidence: det.confidence,
            severity: det.severity,
            estimated_area: parseFloat(det.area) || 0.32,
            evidence_path: det.annotated_image_url || det.image_url || localPreview,
            location: det.location || 'Monitored Walkway',
            source_type: 'image',
            original_filename: file.name,
            created_at: new Date().toISOString(),
            summary: det.recommendation || `Detected ${det.class_name}`
          });
        }"""

    if target_upload in content:
        content = content.replace(target_upload, replacement_upload)
        print('Updated handleFileUpload in ImageDetectionWorkspace.tsx')
    else:
        print('Warning: target_upload not found')

    # 3. Add history in handleSelectPreset
    target_preset = """        if (res.ok && data.status === 'ok' && data.detection) {
          setCustomResult(data.detection);
        } else {"""

    replacement_preset = """        if (res.ok && data.status === 'ok' && data.detection) {
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

    if target_preset in content:
        content = content.replace(target_preset, replacement_preset)
        print('Updated handleSelectPreset in ImageDetectionWorkspace.tsx')
    else:
        print('Warning: target_preset not found')

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

update_image_detection_workspace()

def update_video_analysis_view():
    path = os.path.join('src', 'components', 'VideoAnalysisView.tsx')
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Import
    if 'saveLocalHistoryItem' not in content:
        content = content.replace(
            "import { VideoAnalysisRecord, KeyframeItem } from '../types';",
            "import { VideoAnalysisRecord, KeyframeItem } from '../types';\nimport { saveLocalHistoryItem } from '../utils/historyStore';"
        )

    # 2. Add history in file upload analysis
    target_upload = """        if (va.keyframes && va.keyframes.length > 0) {
          setKeyframes(va.keyframes);
          setSelectedKeyframe(0);
          setHasAnalyzed(true);
          setShowOverlay(true);
        }"""

    replacement_upload = """        if (va.keyframes && va.keyframes.length > 0) {
          setKeyframes(va.keyframes);
          setSelectedKeyframe(0);
          setHasAnalyzed(true);
          setShowOverlay(true);

          // Save detected hazard keyframes to persistent Hazard History
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

    if target_upload in content:
        content = content.replace(target_upload, replacement_upload)
        print('Updated file upload in VideoAnalysisView.tsx')
    else:
        print('Warning: target_upload in VideoAnalysisView not found')

    # 3. Add history in default sample video analysis
    target_default = """        if (va.keyframes && va.keyframes.length > 0) {
          setKeyframes(va.keyframes);
          setSelectedKeyframe(0);
        }
        setHasAnalyzed(true);
        setShowOverlay(true);
        loadVideoHistory();"""

    replacement_default = """        if (va.keyframes && va.keyframes.length > 0) {
          setKeyframes(va.keyframes);
          setSelectedKeyframe(0);

          // Save default tour keyframes to persistent Hazard History
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

    if target_default in content:
        content = content.replace(target_default, replacement_default)
        print('Updated default video analysis in VideoAnalysisView.tsx')
    else:
        print('Warning: target_default in VideoAnalysisView not found')

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

update_video_analysis_view()

def update_hazard_history_view():
    path = os.path.join('src', 'components', 'HazardHistoryView.tsx')
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Add import
    if 'getLocalHistory' not in content:
        content = content.replace(
            "import { RecentDetectionRow } from '../types';",
            "import { RecentDetectionRow } from '../types';\nimport { getLocalHistory, removeLocalHistoryItem } from '../utils/historyStore';"
        )

    # 2. Replace loadDetections
    target_load = """  // Load records from backend API
  const loadDetections = async () => {
    setLoading(true);
    try {
      const url = new URL('/api/detections', window.location.origin);
      if (activeSourceTab !== 'all') url.searchParams.set('source_type', activeSourceTab);
      if (selectedClass !== 'all') url.searchParams.set('className', selectedClass);
      if (selectedSeverity !== 'all') url.searchParams.set('severity', selectedSeverity);
      if (searchTerm) url.searchParams.set('search', searchTerm);

      const res = await fetch(url.toString());
      const data = await res.json();
      if (data.status === 'ok') {
        setDetections(data.detections);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDetections();
  }, [activeSourceTab, selectedClass, selectedSeverity, searchTerm]);"""

    replacement_load = """  // Load records from backend API + persistent localStorage
  const loadDetections = async () => {
    setLoading(true);
    try {
      const localItems = getLocalHistory();
      let apiItems: any[] = [];
      try {
        const url = new URL('/api/detections', window.location.origin);
        if (activeSourceTab !== 'all') url.searchParams.set('source_type', activeSourceTab);
        if (selectedClass !== 'all') url.searchParams.set('className', selectedClass);
        if (selectedSeverity !== 'all') url.searchParams.set('severity', selectedSeverity);
        if (searchTerm) url.searchParams.set('search', searchTerm);

        const res = await fetch(url.toString());
        if (res.ok) {
          const data = await res.json();
          if (data.status === 'ok' && Array.isArray(data.detections)) {
            apiItems = data.detections;
          }
        }
      } catch (e) {
        console.warn('Backend detections endpoint unavailable, loading local history store');
      }

      // Merge local items and API items, deduplicating by ID
      const seenIds = new Set<string>();
      const combined: any[] = [];
      for (const item of [...localItems, ...apiItems]) {
        if (!seenIds.has(item.id)) {
          seenIds.add(item.id);
          combined.push(item);
        }
      }

      // Apply client-side filters
      const filtered = combined.filter((row: any) => {
        if (activeSourceTab !== 'all' && (row.source_type || 'image') !== activeSourceTab) return false;
        if (selectedClass !== 'all' && !(row.class_name || '').toLowerCase().includes(selectedClass.toLowerCase())) return false;
        if (selectedSeverity !== 'all' && row.severity !== selectedSeverity) return false;
        if (searchTerm) {
          const q = searchTerm.toLowerCase();
          const matchFilename = (row.original_filename || '').toLowerCase().includes(q);
          const matchClass = (row.class_name || '').toLowerCase().includes(q);
          const matchLoc = (row.location || '').toLowerCase().includes(q);
          if (!matchFilename && !matchClass && !matchLoc) return false;
        }
        return true;
      });

      filtered.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());
      setDetections(filtered);
    } catch (err) {
      console.error('Error loading hazard detections history:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDetections();
    const handleUpdate = () => loadDetections();
    window.addEventListener('floorguard:history_updated', handleUpdate);
    return () => window.removeEventListener('floorguard:history_updated', handleUpdate);
  }, [activeSourceTab, selectedClass, selectedSeverity, searchTerm]);"""

    if target_load in content:
        content = content.replace(target_load, replacement_load)
        print('Updated loadDetections in HazardHistoryView.tsx')
    else:
        print('Warning: target_load in HazardHistoryView not found')

    # 3. Replace handleDelete to remove from local store too
    target_del = """  const handleDelete = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!confirm('Are you sure you want to remove this detection log?')) return;
    try {
      await fetch(`/api/detections/${id}`, { method: 'DELETE' });
      setDetections((prev) => prev.filter((d) => d.id !== id));
    } catch (err) {
      console.error(err);
    }
  };"""

    replacement_del = """  const handleDelete = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!confirm('Are you sure you want to remove this detection log?')) return;
    removeLocalHistoryItem(id);
    try {
      await fetch(`/api/detections/${id}`, { method: 'DELETE' });
    } catch (err) {
      // ignore
    }
    setDetections((prev) => prev.filter((d) => d.id !== id));
  };"""

    if target_del in content:
        content = content.replace(target_del, replacement_del)
        print('Updated handleDelete in HazardHistoryView.tsx')
    else:
        print('Warning: target_del in HazardHistoryView not found')

    # 4. Add onError image fallback
    target_img = """                      <img
                        src={row.evidence_path || '/assets/samples/thumb_water_spill.jpg'}
                        alt={row.class_name}
                        className="w-full h-full object-cover"
                      />"""

    replacement_img = """                      <img
                        src={row.evidence_path || '/assets/samples/thumb_water_spill.jpg'}
                        alt={row.class_name}
                        className="w-full h-full object-cover"
                        onError={(e) => {
                          (e.target as HTMLImageElement).src = '/assets/samples/thumb_water_spill.jpg';
                        }}
                      />"""

    if target_img in content:
        content = content.replace(target_img, replacement_img)
        print('Updated image onError fallback in HazardHistoryView.tsx')
    else:
        print('Warning: target_img in HazardHistoryView not found')

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

update_hazard_history_view()
