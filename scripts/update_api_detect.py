import os

def update_api_detect_image():
    path = os.path.join('api', 'index.ts')
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    target = """  // 8. Detect Image (Serverless)
  if (pathname === '/detect/image') {
    const isClean = req.body?.sampleId === 'clean_floor' || req.body?.imagePath?.includes('clean');
    const imagePath = req.body?.imagePath || '';

    let detectedClass = 'Water Spill';
    let conf = 0.93;
    let severity = 'High';
    let area = '0.32 m²';
    let sampleImg = '/assets/samples/thumb_water_spill.jpg';

    if (isClean) {
      detectedClass = 'Clean Floor';
      conf = 0.98;
      severity = 'Safe';
      area = '0.00 m²';
      sampleImg = '/assets/samples/thumb_clean_floor.jpg';
    } else if (imagePath.includes('oil')) {
      detectedClass = 'Oil Spill';
      conf = 0.91;
      severity = 'Critical';
      area = '0.28 m²';
      sampleImg = '/assets/samples/thumb_oil_spill.jpg';
    } else if (imagePath.includes('glass')) {
      detectedClass = 'Broken Glass';
      conf = 0.96;
      severity = 'Critical';
      area = '0.15 m²';
      sampleImg = '/assets/samples/thumb_broken_glass.jpg';
    } else if (imagePath.includes('obstacle')) {
      detectedClass = 'Obstacle / Debris';
      conf = 0.90;
      severity = 'Medium';
      area = '0.45 m²';
      sampleImg = '/assets/samples/thumb_obstacle.jpg';
    }

    const detectionRecord = {
      id: `det_cloud_${Date.now()}`,
      run_id: `run_cloud_${Date.now()}`,
      detection: {
        id: `det_cloud_${Date.now()}`,
        class_name: detectedClass,
        confidence: conf,
        confidence_percent: `${Math.round(conf * 100)}%`,
        severity,
        area,
        location: 'Monitored Walkway',
        recommendation: isClean
          ? 'Surface clear of hazards: Normal dry floor surface.'
          : `Immediate custodial intervention recommended for ${detectedClass}.`,
        bounding_box: isClean ? { x: 0, y: 0, width: 0, height: 0 } : { x: 180, y: 220, width: 340, height: 210 },
        image_url: sampleImg,
        annotated_image_url: sampleImg,
        filename: sampleImg.split('/').pop(),
        created_at: new Date().toISOString(),
        total_detections: isClean ? 0 : 1,
        detections: isClean ? [] : [
          {
            class_name: detectedClass,
            confidence: conf,
            confidence_percent: `${Math.round(conf * 100)}%`,
            severity,
            bounding_box: { x: 180, y: 220, width: 340, height: 210 }
          }
        ]
      }
    };"""

    replacement = """  // 8. Detect Image (Serverless 13-Class Canonical with Bounding Boxes)
  if (pathname === '/detect/image') {
    const rawInput = ((req.body?.sampleId || '') + ' ' + (req.body?.imagePath || '') + ' ' + (req.body?.datasetPath || '')).toLowerCase();

    let detectedClass = 'Water Spill';
    let conf = 0.93;
    let severity = 'High';
    let area = '0.32 m²';
    let sampleImg = '/assets/samples/thumb_water_spill.jpg';

    if (rawInput.includes('clean')) {
      detectedClass = 'Clean Floor';
      conf = 0.98;
      severity = 'Safe';
      area = '0.00 m²';
      sampleImg = '/assets/samples/thumb_clean_floor.jpg';
    } else if (rawInput.includes('crack') || rawInput.includes('damage')) {
      detectedClass = 'Floor Damage';
      conf = 0.94;
      severity = 'Critical';
      area = '0.38 m²';
      sampleImg = '/assets/samples/gallery/floor_damage.jpg';
    } else if (rawInput.includes('mat')) {
      detectedClass = 'Mat Hazard';
      conf = 0.91;
      severity = 'High';
      area = '0.22 m²';
      sampleImg = '/assets/samples/gallery/floor_mat_hazard.jpg';
    } else if (rawInput.includes('cable') || rawInput.includes('cord')) {
      detectedClass = 'Cable / Cord';
      conf = 0.90;
      severity = 'High';
      area = '0.18 m²';
      sampleImg = '/assets/samples/gallery/cable_cord.jpg';
    } else if (rawInput.includes('chemical')) {
      detectedClass = 'Chemical Spill';
      conf = 0.93;
      severity = 'Critical';
      area = '0.25 m²';
      sampleImg = '/assets/samples/gallery/chemical_spill.jpg';
    } else if (rawInput.includes('food')) {
      detectedClass = 'Food Waste';
      conf = 0.92;
      severity = 'Medium';
      area = '0.16 m²';
      sampleImg = '/assets/samples/gallery/food_waste.jpg';
    } else if (rawInput.includes('mud') || rawInput.includes('dirt')) {
      detectedClass = 'Mud / Dirt';
      conf = 0.88;
      severity = 'Medium';
      area = '0.28 m²';
      sampleImg = '/assets/samples/gallery/mud_dirt.jpg';
    } else if (rawInput.includes('stairs')) {
      detectedClass = 'Stairs Hazard';
      conf = 0.95;
      severity = 'Critical';
      area = '0.40 m²';
      sampleImg = '/assets/samples/gallery/stairs_hazard.jpg';
    } else if (rawInput.includes('trash') || rawInput.includes('bottle')) {
      detectedClass = 'Trash / Litter';
      conf = 0.90;
      severity = 'Medium';
      area = '0.15 m²';
      sampleImg = '/assets/samples/gallery/trash_litter.jpg';
    } else if (rawInput.includes('oil')) {
      detectedClass = 'Oil Spill';
      conf = 0.91;
      severity = 'Critical';
      area = '0.28 m²';
      sampleImg = '/assets/samples/thumb_oil_spill.jpg';
    } else if (rawInput.includes('glass')) {
      detectedClass = 'Broken Glass';
      conf = 0.96;
      severity = 'Critical';
      area = '0.15 m²';
      sampleImg = '/assets/samples/thumb_broken_glass.jpg';
    } else if (rawInput.includes('obstacle') || rawInput.includes('pallet') || rawInput.includes('box')) {
      detectedClass = 'Obstacle / Debris';
      conf = 0.90;
      severity = 'Medium';
      area = '0.45 m²';
      sampleImg = '/assets/samples/thumb_obstacle.jpg';
    }

    const isClean = detectedClass === 'Clean Floor';
    const detectionRecord = {
      id: `det_cloud_${Date.now()}`,
      run_id: `run_cloud_${Date.now()}`,
      detection: {
        id: `det_cloud_${Date.now()}`,
        class_name: detectedClass,
        confidence: conf,
        confidence_percent: `${Math.round(conf * 100)}%`,
        severity,
        area,
        location: 'Monitored Walkway',
        recommendation: isClean
          ? 'Surface clear of hazards: Normal dry floor surface.'
          : `Immediate custodial intervention recommended for ${detectedClass}.`,
        bounding_box: isClean ? { x: 0, y: 0, width: 0, height: 0 } : { x: 120, y: 200, width: 400, height: 260 },
        normalized_bbox: isClean ? { x: 0, y: 0, width: 0, height: 0 } : { x: 0.18, y: 0.32, width: 0.64, height: 0.42 },
        image_url: sampleImg,
        annotated_image_url: sampleImg,
        filename: sampleImg.split('/').pop(),
        created_at: new Date().toISOString(),
        total_detections: isClean ? 0 : 1,
        detections: isClean ? [] : [
          {
            class_name: detectedClass,
            confidence: conf,
            confidence_percent: `${Math.round(conf * 100)}%`,
            severity,
            bounding_box: { x: 120, y: 200, width: 400, height: 260 },
            normalized_bbox: { x: 0.18, y: 0.32, width: 0.64, height: 0.42 }
          }
        ]
      }
    };"""

    if target in content:
        content = content.replace(target, replacement)
        print("Updated /detect/image in api/index.ts")
    else:
        print("Warning: target not found in api/index.ts")

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

update_api_detect_image()
