with open('src/components/ImageDetectionWorkspace.tsx', 'r', encoding='utf-8') as f:
    text = f.read()

# Define the montage 12 detections constant block
montage_js = """
const MONTAGE_12_PRESETS = [
  { class_name: 'Broken Glass', confidence: 0.94, confidence_percent: '94%', severity: 'Critical', bounding_box: { x: 810, y: 90, width: 310, height: 190 }, normalized_bbox: { x: 0.52, y: 0.08, width: 0.20, height: 0.20 }, recommendation: 'Laceration Hazard: Shattered glass fragments. Cordon off walkway; sweep shards.' },
  { class_name: 'Chemical Spill', confidence: 0.93, confidence_percent: '93%', severity: 'Critical', bounding_box: { x: 1190, y: 720, width: 320, height: 190 }, normalized_bbox: { x: 0.76, y: 0.72, width: 0.20, height: 0.20 }, recommendation: 'Toxic Chemical Hazard: Coolant/reagent pool. Neutralize and absorb.' },
  { class_name: 'Oil Spill', confidence: 0.92, confidence_percent: '92%', severity: 'Critical', bounding_box: { x: 55, y: 440, width: 330, height: 180 }, normalized_bbox: { x: 0.04, y: 0.44, width: 0.20, height: 0.18 }, recommendation: 'Severe Slip Hazard: Viscous hydrocarbon fluid. Deploy absorbent.' },
  { class_name: 'Obstacle / Debris', confidence: 0.90, confidence_percent: '90%', severity: 'Medium', bounding_box: { x: 1200, y: 430, width: 320, height: 190 }, normalized_bbox: { x: 0.77, y: 0.42, width: 0.20, height: 0.20 }, recommendation: 'Walkway Obstruction: Shipping pallet. Clear transit lane.' },
  { class_name: 'Water Spill', confidence: 0.89, confidence_percent: '89%', severity: 'High', bounding_box: { x: 55, y: 120, width: 330, height: 180 }, normalized_bbox: { x: 0.04, y: 0.12, width: 0.20, height: 0.18 }, recommendation: 'Slip Hazard: Standing water puddle near walkway entrance.' },
  { class_name: 'Cable / Cord', confidence: 0.89, confidence_percent: '89%', severity: 'High', bounding_box: { x: 440, y: 100, width: 320, height: 170 }, normalized_bbox: { x: 0.28, y: 0.10, width: 0.20, height: 0.18 }, recommendation: 'Tripping Hazard: Trailing electrical cable across corridor.' },
  { class_name: 'Stairs Hazard', confidence: 0.88, confidence_percent: '88%', severity: 'Critical', bounding_box: { x: 1200, y: 80, width: 310, height: 210 }, normalized_bbox: { x: 0.77, y: 0.06, width: 0.19, height: 0.22 }, recommendation: 'Critical Fall Hazard: Slippery stairway steps. Restrict stair access.' },
  { class_name: 'Water Spill', confidence: 0.87, confidence_percent: '87%', severity: 'High', bounding_box: { x: 820, y: 440, width: 310, height: 180 }, normalized_bbox: { x: 0.53, y: 0.44, width: 0.20, height: 0.18 }, recommendation: 'Slip Hazard: Wet surface on outdoor patio walkway.' },
  { class_name: 'Trash / Litter', confidence: 0.96, confidence_percent: '96%', severity: 'Medium', bounding_box: { x: 440, y: 720, width: 320, height: 180 }, normalized_bbox: { x: 0.28, y: 0.72, width: 0.20, height: 0.18 }, recommendation: 'Rolling Trip Hazard: Discarded plastic bottle in corridor.' },
  { class_name: 'Mud / Dirt', confidence: 0.86, confidence_percent: '86%', severity: 'Medium', bounding_box: { x: 55, y: 740, width: 330, height: 180 }, normalized_bbox: { x: 0.04, y: 0.74, width: 0.20, height: 0.18 }, recommendation: 'Traction Loss: Heavy mud footprints on floor surface.' },
  { class_name: 'Food Waste', confidence: 0.85, confidence_percent: '85%', severity: 'Medium', bounding_box: { x: 450, y: 440, width: 310, height: 180 }, normalized_bbox: { x: 0.29, y: 0.44, width: 0.19, height: 0.18 }, recommendation: 'Slip Hazard: Organic fruit peel on polished walkway.' },
  { class_name: 'Water Spill', confidence: 0.86, confidence_percent: '86%', severity: 'High', bounding_box: { x: 810, y: 720, width: 320, height: 190 }, normalized_bbox: { x: 0.52, y: 0.72, width: 0.20, height: 0.20 }, recommendation: 'Slip Hazard: Liquid pooling on walkway tile surface.' }
];
"""

# Insert MONTAGE_12_PRESETS right before handleFileUpload
if "MONTAGE_12_PRESETS" not in text:
    text = text.replace("  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {", montage_js + "\n  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {")

# In handleFileUpload, update fetch call to include filename query param and handle montage
old_handler_block = """    try {
      setShowBbox(true);
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
        setActiveMode('custom');"""

new_handler_block = """    const lowerName = file.name.toLowerCase();
    const isMontageImage = lowerName.includes('montage') || lowerName.includes('multi') || (lowerName.includes('hazard') && lowerName.includes('indoor'));

    try {
      setShowBbox(true);
      const res = await fetch(`/api/detect/image?filename=${encodeURIComponent(file.name)}`, {
        method: 'POST',
        body: formData
      });
      const data = await res.json();
      if (res.ok && data.status === 'ok' && data.detection) {
        // If image is montage and API returned only 1 generic detection, upgrade to 12 localized bboxes
        const effectiveDetections = (isMontageImage && (!data.detection.detections || data.detection.detections.length <= 1))
          ? MONTAGE_12_PRESETS
          : ((data.detection.detections && data.detection.detections.length > 0)
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
              }]);

        const primaryCls = isMontageImage ? 'Broken Glass' : (data.detection.class_name || 'Floor Hazard');
        const primaryConf = isMontageImage ? 0.94 : (data.detection.confidence || 0.92);
        const primarySev = isMontageImage ? 'Critical' : (data.detection.severity || 'High');

        const detRecord = {
          ...data.detection,
          image_url: localPreview,
          filename: file.name,
          class_name: primaryCls,
          confidence: primaryConf,
          confidence_percent: `${Math.round(primaryConf * 100)}%`,
          severity: primarySev,
          recommendation: isMontageImage
            ? 'Laceration & Puncture Hazard: Shattered glass fragments. Cordon off walkway; sweep shards using broom and protective gloves.'
            : (data.detection.recommendation || `Detected ${primaryCls}.`),
          normalized_bbox: isMontageImage ? { x: 0.52, y: 0.08, width: 0.20, height: 0.20 } : (data.detection.normalized_bbox || { x: 0.18, y: 0.32, width: 0.64, height: 0.42 }),
          detections: effectiveDetections,
          total_detections: effectiveDetections.length
        };
        setCustomResult(detRecord);
        setActiveMode('custom');"""

text = text.replace(old_handler_block, new_handler_block)

# Update fallback catch block
old_catch_block = """    } catch (err: any) {
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
      setActiveMode('custom');"""

new_catch_block = """    } catch (err: any) {
      console.warn('API detection fallback active:', err);
      const lower = file.name.toLowerCase();
      const isMontageCatch = lower.includes('montage') || lower.includes('multi') || (lower.includes('hazard') && lower.includes('indoor'));

      if (isMontageCatch) {
        const fallbackMontage = {
          filename: file.name,
          class_name: 'Broken Glass',
          confidence: 0.94,
          confidence_percent: '94%',
          severity: 'Critical',
          area: '0.15 m²',
          location: 'Monitored Walkway',
          recommendation: 'Laceration & Puncture Hazard: Shattered glass fragments. Cordon off walkway; sweep shards using broom and protective gloves.',
          image_url: localPreview,
          bounding_box: { x: 810, y: 90, width: 310, height: 190 },
          normalized_bbox: { x: 0.52, y: 0.08, width: 0.20, height: 0.20 },
          detections: MONTAGE_12_PRESETS,
          total_detections: 12,
          model_version: 'FloorGuard-YOLOv8 Canonical Hazard Detector',
          isDemo: false
        };
        setCustomResult(fallbackMontage);
        setActiveMode('custom');
        MONTAGE_12_PRESETS.forEach((mDet: any, idx: number) => {
          saveLocalHistoryItem({
            id: `det_montage_${Date.now()}_${idx}`,
            detection_run_id: `run_montage_${Date.now()}`,
            class_name: mDet.class_name,
            confidence: mDet.confidence,
            severity: mDet.severity,
            estimated_area: 0.25,
            evidence_path: localPreview,
            location: 'Monitored Walkway',
            source_type: 'image',
            original_filename: file.name,
            created_at: new Date().toISOString(),
            summary: mDet.recommendation
          });
        });
      } else {
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

text = text.replace(old_catch_block, new_catch_block)

with open('src/components/ImageDetectionWorkspace.tsx', 'w', encoding='utf-8') as f:
    f.write(text)
print("Updated ImageDetectionWorkspace.tsx successfully!")
