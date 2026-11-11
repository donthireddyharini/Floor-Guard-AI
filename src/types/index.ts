export type NavSection =
  | 'home'
  | 'overview'
  | 'image_detection'
  | 'video_analysis'
  | 'dataset_training'
  | 'hazard_history'
  | 'analytics'
  | 'settings';

export type HazardSeverity = 'Safe' | 'Low' | 'Medium' | 'High' | 'Critical';

export interface BoundingBox {
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
  normalized_bbox?: any;
  polygon_contour?: string;
  image_url: string;
  filename: string;
  created_at: string;
  task?: 'detection' | 'classification';
  academic_notice?: string;
  model_version?: string;
  architecture?: string;
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
  location?: string;
}

export interface DatasetSplitData {
  train: number;
  val: number;
  test: number;
  train_pct: string;
  val_pct: string;
  test_pct: string;
}

export interface DatasetSummary {
  total_curated_images: number;
  total_annotations: number;
  roboflow_reported_images: number;
  splits: DatasetSplitData;
  class_distribution: Record<string, number>;
  roboflow_class_distribution: {
    spill: number;
    normal_floor: number;
  };
  sources: any[];
  huggingface_downloaded: number;
  huggingface_samples: any[];
}

export interface TrainingTelemetry {
  active_model_id: string;
  yolo_detection: {
    model_name: string;
    architecture: string;
    epochs: number;
    batch_size: number;
    initial_lr: number;
    hardware: string;
    duration_minutes: number;
    final_train_loss: number;
    final_val_loss: number;
    loss_history: { epoch: number; train_loss: number; val_loss: number; mAP50: number }[];
    mAP50: number;
    mAP50_95: number;
    precision: number;
    recall: number;
    latency_ms: number;
    fps: number;
    per_class: Record<string, any>;
  };
  roboflow_classification: {
    model_name: string;
    architecture: string;
    dataset_source: string;
    reported_images: number;
    epochs: number;
    batch_size: number;
    optimizer: string;
    classes: string[];
    convergence: { epoch: number; train_loss: number; val_loss: number; val_acc: number }[];
    accuracy: number;
    precision: number;
    recall: number;
    f1_score: number;
    latency_ms: number;
    fps: number;
    per_class: Record<string, any>;
    academic_disclosure: string;
  };
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
  dataset_summary?: DatasetSummary;
  training_telemetry?: TrainingTelemetry;
}
