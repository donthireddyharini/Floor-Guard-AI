export type NavSection =
  | 'overview'
  | 'image_detection'
  | 'video_analysis'
  | 'hazard_history'
  | 'analytics'
  | 'ai_model_lab'
  | 'settings';

export type HazardSeverity = 'Safe' | 'Low' | 'Medium' | 'High' | 'Critical';

export interface BoundingBox {
  x: number;
  y: number;
  width: number;
  height: number;
}

export interface NormalizedBoundingBox {
  x: number;
  y: number;
  width: number;
  height: number;
}

export interface ModelMetrics {
  mAP50?: number;
  mAP50_95?: number;
  precision?: number;
  recall?: number;
  accuracy?: number;
  f1_score?: number;
  latency_batch1_ms?: number;
  fps?: number;
}

export interface ModelItem {
  id: string;
  name: string;
  version: string;
  architecture: string;
  task: 'detection' | 'classification';
  trained_status: string;
  weights_path: string;
  parameters_count?: string;
  input_resolution?: [number, number];
  metrics: ModelMetrics;
  classes: string[];
  description: string;
  active?: boolean;
  unsupported_classes?: string[];
}

export interface DetectionSubItem {
  class_id: number;
  class_name: string;
  raw_class_name?: string;
  confidence: number;
  confidence_percent: string;
  severity: HazardSeverity;
  is_tripping_hazard_candidate?: boolean;
  estimated_area_m2?: number;
  bounding_box: BoundingBox;
  normalized_bbox: NormalizedBoundingBox;
}

export interface DetectionItem {
  id: string;
  run_id?: string;
  class_name: string;
  confidence: number;
  confidence_percent?: string;
  severity: HazardSeverity;
  area: string;
  location: string;
  recommendation?: string;
  bounding_box: BoundingBox;
  normalized_bbox?: NormalizedBoundingBox;
  polygon_contour?: string;
  image_url: string;
  annotated_image_url?: string;
  filename: string;
  created_at: string;
  task?: 'detection' | 'classification';
  academic_notice?: string;
  model_version?: string;
  architecture?: string;
  inference_duration_ms?: number;
  detections?: DetectionSubItem[];
  total_detections?: number;
  supported_classes?: string[];
  unsupported_classes?: string[];
}

export interface VideoKeyframe {
  id: number;
  frame: number;
  timestamp: string;
  timestamp_seconds: number;
  detected_class: string;
  confidence: number;
  severity: HazardSeverity;
  detections_count: number;
  detections: DetectionSubItem[];
  thumb: string;
  note?: string;
}

export interface VideoAnalysisResult {
  run_id: string;
  filename: string;
  video_url: string;
  is_demo_simulation: boolean;
  model_id: string;
  model_name: string;
  is_custom_trained: boolean;
  duration: string;
  duration_seconds: number;
  fps: number;
  total_frames: number;
  total_frames_analyzed: number;
  sampling_interval_seconds: number;
  hazards_count: number;
  clean_frames_count: number;
  processing_duration_seconds: number;
  average_frame_latency_ms: number;
  throughput_fps: number;
  keyframes: VideoKeyframe[];
  summary: string;
  academic_notice: string;
}

export interface HistoryRunRow {
  id: string;
  source_type: 'image' | 'video';
  original_filename: string;
  original_image_url: string;
  annotated_image_url: string;
  thumb_url: string;
  created_at: string;
  status: string;
  processing_duration_ms: number;
  model_version: string;
  total_detections: number;
  summary: string;
  detections?: any[];
}

export interface KpiData {
  images_analyzed: number;
  images_analyzed_delta: string;
  hazards_detected: number;
  hazards_detected_delta: string;
  safe_floors: number;
  safe_floors_delta: string;
  model_map: string;
  model_map_delta: string;
}

export interface HazardDistributionItem {
  name: string;
  percentage: number;
  count: number;
  color: string;
}

export interface DetectionTrendPoint {
  date: string;
  total_images: number;
  hazards_detected: number;
}

export interface HeatmapData {
  hours: string[];
  days: string[];
  grid: {
    hour: string;
    values: string[];
  }[];
}

export interface RecentDetectionRow {
  id: string;
  detection_run_id: string;
  class_name: string;
  confidence: number;
  severity: HazardSeverity;
  evidence_path: string;
  created_at: string;
  original_filename: string;
  estimated_area?: number;
}

export interface AnalyticsSummary {
  kpis: KpiData;
  hazard_distribution: {
    total: number;
    items: HazardDistributionItem[];
  };
  detection_trend: DetectionTrendPoint[];
  heatmap: HeatmapData;
  recent_detections: RecentDetectionRow[];
  dataset_summary?: any;
  training_telemetry?: any;
}
