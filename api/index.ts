// Floor Guard AI - Vercel Serverless API Handler

// Fallback & Mock Data for Serverless Cloud Runtime
const MODEL_REGISTRY = {
  active_model_id: "yolov8s-coco-pretrained",
  registry: [
    {
      id: "yolov8s-coco-pretrained",
      name: "Ultralytics YOLOv8s Pretrained (COCO-80)",
      version: "8.0.0",
      architecture: "YOLOv8s",
      task: "detection",
      trained_status: "official_ultralytics_pretrained",
      weights_path: "models/pretrained/yolov8s.pt",
      parameters_count: "11.2M",
      input_resolution: [640, 640],
      active: true,
      description: "Official pretrained weights from Ultralytics on MS COCO 80 classes.",
      classes: ["person", "bicycle", "car", "motorcycle", "bottle", "chair", "potted plant", "laptop", "box"]
    },
    {
      id: "floorguard-yolov8s-v1.1.0-phase4.2",
      name: "FloorGuard-YOLOv8s Custom Hazard Detector (Phase 4.2)",
      version: "1.1.0-phase4.2",
      architecture: "YOLOv8s",
      task: "detection",
      trained_status: "custom_trained_phase4_2",
      weights_path: "models/detection/floorguard_yolov8s_phase4_2_best.pt",
      parameters_count: "11.13M",
      input_resolution: [640, 640],
      active: false,
      description: "Custom YOLOv8s detector trained for 100 epochs on floor hazards with synthetic liquid augmentation.",
      classes: ["water_spill", "oil_spill", "broken_glass", "obstacle"]
    }
  ]
};

const OPERATIONAL_KPIS = {
  total_analyses: 48,
  images_analyzed: 40,
  videos_analyzed: 8,
  hazards_detected: 185,
  clean_floors_confirmed: 12,
  safe_pass_rate_pct: 25
};

const EVALUATION_TELEMETRY = {
  phase4_2_frozen_benchmark: {
    mAP50: 0.6732,
    mAP50_95: 0.3389,
    precision: 0.5867,
    recall: 0.6377,
    clean_floor_tn: 2,
    clean_floor_fp: 0,
    per_class: {
      water_spill: { precision: 0.7966, recall: 1.0, mAP50: 0.995 },
      oil_spill: { precision: 0.6203, recall: 0.574, mAP50: 0.5607 },
      broken_glass: { precision: 0.3746, recall: 0.5333, mAP50: 0.4722 },
      obstacle: { precision: 0.5552, recall: 0.4436, mAP50: 0.665 }
    }
  },
  phase4_3_expanded_benchmark: {
    total_images: 25,
    mAP50: 0.4375,
    mAP50_95: 0.1777,
    clean_floor_tn: 5,
    clean_floor_fp: 0
  }
};

const SAMPLE_RUNS = [
  {
    id: "run_cloud_01",
    source_type: "image",
    original_filename: "sample_water_spill.jpg",
    file_path: "/data/images/sample_water_spill.jpg",
    annotated_path: "/data/images/sample_water_spill.jpg",
    thumb_url: "/data/images/sample_water_spill.jpg",
    created_at: new Date().toISOString(),
    status: "completed",
    model_version: "FloorGuard-YOLOv8s-Phase4.2",
    total_detections: 2,
    summary: "Detected 2 hazard(s): Water Spill (94%), Water Spill (88%)"
  },
  {
    id: "run_cloud_02",
    source_type: "image",
    original_filename: "thumb_oil_spill.jpg",
    file_path: "/data/images/thumb_oil_spill.jpg",
    annotated_path: "/data/images/thumb_oil_spill.jpg",
    thumb_url: "/data/images/thumb_oil_spill.jpg",
    created_at: new Date(Date.now() - 3600000).toISOString(),
    status: "completed",
    model_version: "FloorGuard-YOLOv8s-Phase4.2",
    total_detections: 1,
    summary: "Detected 1 hazard(s): Oil Spill (87%)"
  },
  {
    id: "run_cloud_03",
    source_type: "image",
    original_filename: "thumb_broken_glass.jpg",
    file_path: "/data/images/thumb_broken_glass.jpg",
    annotated_path: "/data/images/thumb_broken_glass.jpg",
    thumb_url: "/data/images/thumb_broken_glass.jpg",
    created_at: new Date(Date.now() - 7200000).toISOString(),
    status: "completed",
    model_version: "FloorGuard-YOLOv8s-Phase4.2",
    total_detections: 3,
    summary: "Detected 3 hazard(s): Broken Glass (91%)"
  },
  {
    id: "run_cloud_04",
    source_type: "video",
    original_filename: "sample_corridor_walkthrough.mp4",
    file_path: "/samples/sample_corridor_walkthrough.mp4",
    annotated_path: "/data/images/sample_water_spill.jpg",
    thumb_url: "/data/images/sample_water_spill.jpg",
    created_at: new Date(Date.now() - 10800000).toISOString(),
    status: "completed",
    model_version: "FloorGuard-YOLOv8s-Phase4.2",
    total_detections: 2,
    summary: "Analyzed 6 sampled frames. Identified 2 hazard instances."
  }
];

export default function handler(req: any, res: any) {
  // CORS Headers
  res.setHeader('Access-Control-Allow-Credentials', 'true');
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET,OPTIONS,PATCH,DELETE,POST,PUT');
  res.setHeader(
    'Access-Control-Allow-Headers',
    'X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version'
  );

  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }

  const url = req.url || '';
  const pathname = url.split('?')[0].replace(/^\/api/, '');

  // 1. Health
  if (pathname === '/health' || pathname === '') {
    return res.status(200).json({
      status: 'ok',
      system: 'Floor Guard AI (Vercel Serverless)',
      version: '1.0.0',
      active_model: 'Ultralytics YOLOv8s Pretrained (COCO-80)',
      active_model_id: 'yolov8s-coco-pretrained',
      runtime: 'Vercel Serverless Node',
      timestamp: new Date().toISOString()
    });
  }

  // 2. Model Status
  if (pathname === '/model/status') {
    return res.status(200).json({
      status: 'ok',
      active_model_id: 'yolov8s-coco-pretrained',
      model: MODEL_REGISTRY.registry[0],
      all_models: MODEL_REGISTRY.registry
    });
  }

  // 3. Model Select
  if (pathname === '/model/select') {
    const { model_id } = req.body || {};
    const selected = MODEL_REGISTRY.registry.find(m => m.id === model_id) || MODEL_REGISTRY.registry[0];
    return res.status(200).json({
      status: 'ok',
      message: `Active model switched to ${selected.name}`,
      active_model_id: selected.id,
      active_model: selected,
      all_models: MODEL_REGISTRY.registry.map(m => ({ ...m, active: m.id === selected.id }))
    });
  }

  // 4. Analytics Real
  if (pathname === '/analytics/real') {
    return res.status(200).json({
      status: 'ok',
      operational_kpis: OPERATIONAL_KPIS,
      hazard_class_distribution: [
        { class_name: 'Water Spill', count: 72 },
        { class_name: 'Broken Glass', count: 64 },
        { class_name: 'Obstacle', count: 31 },
        { class_name: 'Oil Spill', count: 18 }
      ],
      activity_timeline: [
        { day: '2026-10-20', analyses: 5, hazards: 12 },
        { day: '2026-10-21', analyses: 8, hazards: 19 },
        { day: '2026-10-22', analyses: 11, hazards: 34 },
        { day: '2026-10-23', analyses: 14, hazards: 52 },
        { day: '2026-10-24', analyses: 10, hazards: 38 }
      ],
      recent_analyses: SAMPLE_RUNS,
      evaluation_telemetry: EVALUATION_TELEMETRY
    });
  }

  // 5. Analytics Summary
  if (pathname === '/analytics/summary') {
    return res.status(200).json({
      status: 'ok',
      kpis: {
        images_analyzed: 48,
        images_analyzed_delta: 'Verified inspections',
        hazards_detected: 185,
        hazards_detected_delta: 'Indexed in database',
        safe_floors: 12,
        safe_floors_delta: 'Dry clearance passes',
        model_map: '67.3%',
        model_map_delta: 'Phase 4.2 Benchmark'
      },
      hazard_distribution: {
        total: 185,
        items: [
          { name: 'Water Spill', count: 72, percentage: 39, color: '#06b6d4' },
          { name: 'Broken Glass', count: 64, percentage: 35, color: '#a855f7' },
          { name: 'Obstacle', count: 31, percentage: 17, color: '#ef4444' },
          { name: 'Oil Spill', count: 18, percentage: 9, color: '#f59e0b' }
        ]
      },
      recent_detections: SAMPLE_RUNS
    });
  }

  // 6. History
  if (pathname === '/history') {
    return res.status(200).json({
      status: 'ok',
      total_count: SAMPLE_RUNS.length,
      history: SAMPLE_RUNS
    });
  }

  // 7. Single History Detail
  if (pathname.startsWith('/history/')) {
    const id = pathname.replace('/history/', '');
    const found = SAMPLE_RUNS.find(r => r.id === id) || SAMPLE_RUNS[0];
    return res.status(200).json({
      status: 'ok',
      run: {
        ...found,
        detections: [
          {
            id: `det_${found.id}_1`,
            class_name: 'Water Spill',
            confidence: 0.94,
            severity: 'High',
            bounding_box: { x: 180, y: 220, width: 340, height: 210 },
            location: 'Walkway Center',
            estimated_area: 0.32
          }
        ]
      }
    });
  }

  // 8. Model Compare Arena
  if (pathname === '/model/compare') {
    return res.status(200).json({
      status: 'ok',
      model_a_coco: {
        model_id: 'yolov8s-coco-pretrained',
        model_name: 'Ultralytics YOLOv8s Pretrained (COCO-80)',
        inference_duration_ms: 84,
        total_detections: 0,
        detections: [],
        annotated_image_url: '/data/images/sample_water_spill.jpg'
      },
      model_b_custom: {
        model_id: 'floorguard-yolov8s-v1.1.0-phase4.2',
        model_name: 'FloorGuard-YOLOv8s Custom Hazard Detector (Phase 4.2)',
        inference_duration_ms: 91,
        total_detections: 2,
        detections: [
          {
            class_name: 'water_spill',
            confidence: 0.94,
            confidence_percent: '94%',
            severity: 'High',
            bounding_box: { x: 180, y: 220, width: 340, height: 210 }
          },
          {
            class_name: 'water_spill',
            confidence: 0.88,
            confidence_percent: '88%',
            severity: 'High',
            bounding_box: { x: 520, y: 310, width: 220, height: 160 }
          }
        ],
        annotated_image_url: '/data/images/sample_water_spill.jpg'
      }
    });
  }

  // 9. Detect Image
  if (pathname === '/detect/image') {
    const isClean = req.body?.sampleId === 'clean_floor' || req.body?.imagePath?.includes('clean');
    return res.status(200).json({
      status: 'ok',
      run_id: `run_cloud_${Date.now()}`,
      detection: {
        id: `det_cloud_${Date.now()}`,
        class_name: isClean ? 'Clean Floor' : 'Water Spill',
        confidence: isClean ? 0.98 : 0.93,
        confidence_percent: isClean ? '98%' : '93%',
        severity: isClean ? 'Safe' : 'High',
        area: isClean ? '0.00 m²' : '0.35 m²',
        location: 'Pedestrian Walkway',
        recommendation: isClean ? 'Surface clear of hazards.' : 'Immediate custodial intervention recommended.',
        bounding_box: isClean ? { x: 0, y: 0, width: 0, height: 0 } : { x: 180, y: 220, width: 340, height: 210 },
        image_url: isClean ? '/data/images/thumb_clean_floor.jpg' : '/data/images/sample_water_spill.jpg',
        annotated_image_url: isClean ? '/data/images/thumb_clean_floor.jpg' : '/data/images/sample_water_spill.jpg',
        filename: isClean ? 'thumb_clean_floor.jpg' : 'sample_water_spill.jpg',
        created_at: new Date().toISOString(),
        total_detections: isClean ? 0 : 1,
        detections: isClean ? [] : [
          {
            class_name: 'Water Spill',
            confidence: 0.93,
            confidence_percent: '93%',
            severity: 'High',
            bounding_box: { x: 180, y: 220, width: 340, height: 210 }
          }
        ]
      }
    });
  }

  // 10. Detect Video
  if (pathname === '/detect/video') {
    return res.status(200).json({
      status: 'ok',
      run_id: `run_vid_cloud_${Date.now()}`,
      duration: '00:06',
      total_frames: 180,
      total_frames_analyzed: 6,
      hazards_count: 2,
      safe_frames_count: 4,
      processing_duration_seconds: 0.54,
      keyframes: [
        {
          id: 0,
          frame: 0,
          timestamp: '00:00',
          detected_class: 'Clean Floor',
          confidence: 0.98,
          severity: 'Safe',
          detections_count: 0,
          thumb: '/data/images/thumb_clean_floor.jpg'
        },
        {
          id: 1,
          frame: 30,
          timestamp: '00:01',
          detected_class: 'Water Spill',
          confidence: 0.94,
          severity: 'High',
          detections_count: 1,
          thumb: '/data/images/sample_water_spill.jpg',
          detections: [
            {
              class_name: 'Water Spill',
              confidence: 0.94,
              confidence_percent: '94%',
              severity: 'High',
              bounding_box: { x: 180, y: 220, width: 340, height: 210 }
            }
          ]
        },
        {
          id: 2,
          frame: 60,
          timestamp: '00:02',
          detected_class: 'Oil Spill',
          confidence: 0.87,
          severity: 'High',
          detections_count: 1,
          thumb: '/data/images/thumb_oil_spill.jpg',
          detections: [
            {
              class_name: 'Oil Spill',
              confidence: 0.87,
              confidence_percent: '87%',
              severity: 'High',
              bounding_box: { x: 210, y: 240, width: 300, height: 180 }
            }
          ]
        }
      ]
    });
  }

  // 11. Settings
  if (pathname === '/settings') {
    return res.status(200).json({
      status: 'ok',
      settings: {
        confidence_threshold: 0.25,
        video_interval: 1.0
      }
    });
  }

  return res.status(404).json({
    status: 'error',
    message: `API Route not found: ${pathname}`
  });
}
