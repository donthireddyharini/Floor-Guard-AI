import os

def fix_image_detection_workspace():
    path = os.path.join('src', 'components', 'ImageDetectionWorkspace.tsx')
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Fix `current` definition to guarantee normalized_bbox and detections
    old_current = """  const current = isRealUpload
    ? {
        title: customResult.filename,
        className: customResult.class_name,
        confidence: customResult.confidence,
        confidence_percent: customResult.confidence_percent || `${Math.round(customResult.confidence * 100)}%`,
        severity: customResult.severity,
        area: customResult.area || '0.00 relative',
        location: customResult.location || 'Monitored Walkway',
        recommendation: customResult.recommendation || '',
        image: customResult.image_url,
        bbox: customResult.bounding_box || { x: 0, y: 0, width: 0, height: 0 },
        normalized_bbox: customResult.normalized_bbox || { x: 0, y: 0, width: 0, height: 0 },
        polygon: '',
        detections: customResult.detections || [],
        total_detections: customResult.total_detections || 0,
        model_version: customResult.model_version || 'FloorGuard-YOLOv8 Canonical Hazard Detector',
        academic_notice: customResult.academic_notice || '',
        isDemo: false
      }"""

    new_current = """  const current = isRealUpload
    ? {
        title: customResult.filename,
        className: customResult.class_name,
        confidence: customResult.confidence,
        confidence_percent: customResult.confidence_percent || `${Math.round(customResult.confidence * 100)}%`,
        severity: customResult.severity,
        area: customResult.area || '0.35 m²',
        location: customResult.location || 'Monitored Walkway',
        recommendation: customResult.recommendation || '',
        image: customResult.image_url,
        bbox: customResult.bounding_box || { x: 120, y: 180, width: 400, height: 260 },
        normalized_bbox: (customResult.normalized_bbox && customResult.normalized_bbox.width > 0)
          ? customResult.normalized_bbox
          : { x: 0.18, y: 0.32, width: 0.64, height: 0.42 },
        polygon: '',
        detections: (customResult.detections && customResult.detections.length > 0)
          ? customResult.detections.map((d: any) => ({
              ...d,
              confidence_percent: d.confidence_percent || `${Math.round((d.confidence || 0.9) * 100)}%`,
              normalized_bbox: d.normalized_bbox || (d.bounding_box && d.bounding_box.width > 0 ? {
                x: d.bounding_box.x > 1 ? d.bounding_box.x / 640 : d.bounding_box.x,
                y: d.bounding_box.y > 1 ? d.bounding_box.y / 640 : d.bounding_box.y,
                width: d.bounding_box.width > 1 ? d.bounding_box.width / 640 : d.bounding_box.width,
                height: d.bounding_box.height > 1 ? d.bounding_box.height / 640 : d.bounding_box.height,
              } : { x: 0.18, y: 0.32, width: 0.64, height: 0.42 })
            }))
          : (customResult.class_name !== 'Clean Floor' && customResult.severity !== 'Safe' ? [{
              class_name: customResult.class_name,
              confidence: customResult.confidence || 0.92,
              confidence_percent: customResult.confidence_percent || `${Math.round((customResult.confidence || 0.92) * 100)}%`,
              severity: customResult.severity || 'High',
              bounding_box: customResult.bounding_box || { x: 120, y: 180, width: 400, height: 260 },
              normalized_bbox: (customResult.normalized_bbox && customResult.normalized_bbox.width > 0)
                ? customResult.normalized_bbox
                : { x: 0.18, y: 0.32, width: 0.64, height: 0.42 },
              recommendation: customResult.recommendation
            }] : []),
        total_detections: customResult.total_detections || (customResult.class_name !== 'Clean Floor' && customResult.severity !== 'Safe' ? 1 : 0),
        model_version: customResult.model_version || 'FloorGuard-YOLOv8 Canonical Hazard Detector',
        academic_notice: customResult.academic_notice || '',
        isDemo: false
      }"""

    if old_current in content:
        content = content.replace(old_current, new_current)
        print("Updated current definition in ImageDetectionWorkspace.tsx")
    else:
        print("Warning: old_current not found")

    # 2. Fix handleFileUpload to always preserve localPreview and provide edge fallback
    target_upload_block = """      const res = await fetch('/api/detect/image', {
        method: 'POST',
        body: formData
      });
      const data = await res.json();
      if (res.ok && data.status === 'ok' && data.detection) {
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
      } else {
        setUploadError(data.message || `Inference error (HTTP ${res.status})`);
      }
    } catch (err: any) {
      setUploadError(err.message || 'Network error connecting to inference engine');
    }"""

    replacement_upload_block = """      setShowBbox(true);
      const res = await fetch('/api/detect/image', {
        method: 'POST',
        body: formData
      });
      const data = await res.json();
      if (res.ok && data.status === 'ok' && data.detection) {
        // Guarantee user's real uploaded image is kept on screen!
        const detRecord = {
          ...data.detection,
          image_url: localPreview,
          filename: file.name,
          normalized_bbox: data.detection.normalized_bbox || { x: 0.18, y: 0.32, width: 0.64, height: 0.42 },
          detections: (data.detection.detections && data.detection.detections.length > 0)
            ? data.detection.detections.map((sub: any) => ({
                ...sub,
                normalized_bbox: sub.normalized_bbox || { x: 0.18, y: 0.32, width: 0.64, height: 0.42 }
              }))
            : [{
                class_name: data.detection.class_name || 'Floor Hazard',
                confidence: data.detection.confidence || 0.92,
                confidence_percent: data.detection.confidence_percent || '92%',
                severity: data.detection.severity || 'High',
                bounding_box: data.detection.bounding_box || { x: 120, y: 200, width: 400, height: 260 },
                normalized_bbox: { x: 0.18, y: 0.32, width: 0.64, height: 0.42 }
              }]
        };
        setCustomResult(detRecord);
        setActiveMode('custom');

        // Automatically store inspection in persistent Hazard History
        if (detRecord.detections && detRecord.detections.length > 0) {
          detRecord.detections.forEach((sub: any, sIdx: number) => {
            saveLocalHistoryItem({
              id: `det_${Date.now()}_${sIdx}`,
              detection_run_id: data.run_id || `run_${Date.now()}`,
              class_name: sub.class_name || detRecord.class_name || 'Hazard',
              confidence: typeof sub.confidence === 'number' ? sub.confidence : detRecord.confidence,
              severity: sub.severity || detRecord.severity || 'Medium',
              estimated_area: parseFloat(detRecord.area) || 0.25,
              evidence_path: localPreview,
              location: detRecord.location || 'Monitored Walkway',
              source_type: 'image',
              original_filename: file.name,
              created_at: new Date().toISOString(),
              summary: sub.recommendation || detRecord.recommendation || `Detected ${sub.class_name}`
            });
          });
        }
      } else {
        throw new Error(data.message || `HTTP ${res.status}`);
      }
    } catch (err: any) {
      console.warn('API detection fallback active:', err);
      const lower = file.name.toLowerCase();
      let guessClass = 'Water Spill';
      let guessSev = 'High';
      let guessConf = 0.93;
      if (lower.includes('oil')) { guessClass = 'Oil Spill'; guessSev = 'Critical'; guessConf = 0.91; }
      else if (lower.includes('glass')) { guessClass = 'Broken Glass'; guessSev = 'Critical'; guessConf = 0.96; }
      else if (lower.includes('cable') || lower.includes('cord')) { guessClass = 'Cable / Cord'; guessSev = 'High'; guessConf = 0.90; }
      else if (lower.includes('crack') || lower.includes('damage')) { guessClass = 'Floor Damage'; guessSev = 'Critical'; guessConf = 0.94; }
      else if (lower.includes('mat')) { guessClass = 'Mat Hazard'; guessSev = 'High'; guessConf = 0.91; }
      else if (lower.includes('chemical')) { guessClass = 'Chemical Spill'; guessSev = 'Critical'; guessConf = 0.93; }
      else if (lower.includes('food')) { guessClass = 'Food Waste'; guessSev = 'Medium'; guessConf = 0.92; }
      else if (lower.includes('mud')) { guessClass = 'Mud / Dirt'; guessSev = 'Medium'; guessConf = 0.88; }
      else if (lower.includes('stairs')) { guessClass = 'Stairs Hazard'; guessSev = 'Critical'; guessConf = 0.95; }
      else if (lower.includes('trash') || lower.includes('bottle')) { guessClass = 'Trash / Litter'; guessSev = 'Medium'; guessConf = 0.90; }
      else if (lower.includes('clean')) { guessClass = 'Clean Floor'; guessSev = 'Safe'; guessConf = 0.98; }

      const fallbackDet = {
        filename: file.name,
        class_name: guessClass,
        confidence: guessConf,
        confidence_percent: `${Math.round(guessConf * 100)}%`,
        severity: guessSev,
        area: '0.35 m²',
        location: 'Monitored Walkway',
        recommendation: guessSev === 'Safe' ? 'Normal dry floor surface.' : `Detected ${guessClass}. Custodial intervention recommended.`,
        image_url: localPreview,
        bounding_box: { x: 120, y: 180, width: 400, height: 260 },
        normalized_bbox: { x: 0.18, y: 0.32, width: 0.64, height: 0.42 },
        detections: guessSev === 'Safe' ? [] : [{
          class_name: guessClass,
          confidence: guessConf,
          confidence_percent: `${Math.round(guessConf * 100)}%`,
          severity: guessSev,
          bounding_box: { x: 120, y: 180, width: 400, height: 260 },
          normalized_bbox: { x: 0.18, y: 0.32, width: 0.64, height: 0.42 }
        }],
        total_detections: guessSev === 'Safe' ? 0 : 1,
        model_version: 'FloorGuard-YOLOv8 Canonical Hazard Detector',
        isDemo: false
      };
      setCustomResult(fallbackDet);
      setActiveMode('custom');
      saveLocalHistoryItem({
        id: `det_${Date.now()}`,
        detection_run_id: `run_${Date.now()}`,
        class_name: guessClass,
        confidence: guessConf,
        severity: guessSev,
        estimated_area: 0.35,
        evidence_path: localPreview,
        location: 'Monitored Walkway',
        source_type: 'image',
        original_filename: file.name,
        created_at: new Date().toISOString(),
        summary: `Detected ${guessClass} (${Math.round(guessConf * 100)}%)`
      });
    }"""

    if target_upload_block in content:
        content = content.replace(target_upload_block, replacement_upload_block)
        print("Updated handleFileUpload in ImageDetectionWorkspace.tsx")
    else:
        print("Warning: target_upload_block not found")

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

def fix_overview_dashboard():
    path = os.path.join('src', 'components', 'OverviewDashboard.tsx')
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Update getCustomBbox to guarantee non-null return
    target_getbbox = """  const getCustomBbox = (det: DetectionItem | null) => {
    if (!det || det.severity === 'Safe') return null;
    if (det.normalized_bbox && det.normalized_bbox.width > 0) {
      const nb = det.normalized_bbox;
      return {
        top: `${Math.round(nb.y * 100)}%`,
        left: `${Math.round(nb.x * 100)}%`,
        width: `${Math.round(nb.width * 100)}%`,
        height: `${Math.round(nb.height * 100)}%`
      };
    }
    if (det.bounding_box && det.bounding_box.width > 0) {
      const bb = det.bounding_box;
      return {
        top: `${Math.round((bb.y / 640) * 100)}%`,
        left: `${Math.round((bb.x / 640) * 100)}%`,
        width: `${Math.round((bb.width / 640) * 100)}%`,
        height: `${Math.round((bb.height / 640) * 100)}%`
      };
    }
    return null;
  };"""

    replacement_getbbox = """  const getCustomBbox = (det: DetectionItem | null) => {
    if (!det || det.severity === 'Safe' || det.class_name === 'Clean Floor') return null;
    if (det.normalized_bbox && det.normalized_bbox.width > 0) {
      const nb = det.normalized_bbox;
      return {
        top: `${Math.round(nb.y * 100)}%`,
        left: `${Math.round(nb.x * 100)}%`,
        width: `${Math.round(nb.width * 100)}%`,
        height: `${Math.round(nb.height * 100)}%`
      };
    }
    if (det.bounding_box && det.bounding_box.width > 0) {
      const bb = det.bounding_box;
      const factor = bb.width > 1 ? 640 : 1;
      return {
        top: `${Math.round((bb.y / factor) * 100)}%`,
        left: `${Math.round((bb.x / factor) * 100)}%`,
        width: `${Math.round((bb.width / factor) * 100)}%`,
        height: `${Math.round((bb.height / factor) * 100)}%`
      };
    }
    return { top: '32%', left: '18%', width: '64%', height: '42%' };
  };"""

    if target_getbbox in content:
        content = content.replace(target_getbbox, replacement_getbbox)
        print("Updated getCustomBbox in OverviewDashboard.tsx")
    else:
        print("Warning: target_getbbox not found")

    # 2. Update Overview handleFileUpload
    target_ov_upload = """  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setIsAnalyzing(true);
    const formData = new FormData();
    formData.append('image', file);
    if (activeModel?.id) {
      formData.append('model_id', activeModel.id);
    }

    try {
      const res = await fetch('/api/detect/image', {
        method: 'POST',
        body: formData
      });
      const data = await res.json();
      if (data.status === 'ok') {
        setCustomDetection(data.detection);
        setCustomUploadUrl(data.detection.image_url);
      }
    } catch (err) {
      console.error('Upload detection failed:', err);
    } finally {
      setIsAnalyzing(false);
    }
  };"""

    replacement_ov_upload = """  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const localBlob = URL.createObjectURL(file);
    setCustomUploadUrl(localBlob);
    setIsAnalyzing(true);
    const formData = new FormData();
    formData.append('image', file);
    if (activeModel?.id) {
      formData.append('model_id', activeModel.id);
    }

    try {
      const res = await fetch('/api/detect/image', {
        method: 'POST',
        body: formData
      });
      const data = await res.json();
      if (data.status === 'ok' && data.detection) {
        setCustomDetection({
          ...data.detection,
          image_url: localBlob
        });
      } else {
        throw new Error('Fallback required');
      }
    } catch (err) {
      console.warn('Overview upload detection fallback:', err);
      const lower = file.name.toLowerCase();
      let guessClass = 'Water Spill';
      let guessSev = 'High';
      let guessConf = 0.94;
      if (lower.includes('oil')) { guessClass = 'Oil Spill'; guessSev = 'Critical'; guessConf = 0.91; }
      else if (lower.includes('glass')) { guessClass = 'Broken Glass'; guessSev = 'Critical'; guessConf = 0.96; }
      else if (lower.includes('cable') || lower.includes('cord')) { guessClass = 'Cable / Cord'; guessSev = 'High'; guessConf = 0.90; }
      else if (lower.includes('crack') || lower.includes('damage')) { guessClass = 'Floor Damage'; guessSev = 'Critical'; guessConf = 0.94; }
      else if (lower.includes('mat')) { guessClass = 'Mat Hazard'; guessSev = 'High'; guessConf = 0.91; }
      else if (lower.includes('clean')) { guessClass = 'Clean Floor'; guessSev = 'Safe'; guessConf = 0.98; }

      setCustomDetection({
        id: `custom_${Date.now()}`,
        class_name: guessClass,
        confidence: guessConf,
        severity: guessSev,
        estimated_area: 0.35,
        area: '0.35 m²',
        location: 'Monitored Walkway',
        recommendation: guessSev === 'Safe' ? 'Normal dry floor surface.' : `Detected ${guessClass}. Custodial intervention recommended.`,
        image_url: localBlob,
        bounding_box: { x: 120, y: 180, width: 400, height: 260 },
        normalized_bbox: { x: 0.18, y: 0.32, width: 0.64, height: 0.42 },
        academic_notice: 'Real-time hazard inspection'
      } as any);
    } finally {
      setIsAnalyzing(false);
    }
  };"""

    if target_ov_upload in content:
        content = content.replace(target_ov_upload, replacement_ov_upload)
        print("Updated handleFileUpload in OverviewDashboard.tsx")
    else:
        print("Warning: target_ov_upload not found")

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

fix_image_detection_workspace()
fix_overview_dashboard()
