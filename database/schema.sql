-- Floor Guard AI Database Schema
-- SQLite3 Compatible

CREATE TABLE IF NOT EXISTS detection_runs (
    id TEXT PRIMARY KEY,
    source_type TEXT NOT NULL CHECK(source_type IN ('image', 'video')),
    original_filename TEXT NOT NULL,
    file_path TEXT NOT NULL,
    created_at TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('completed', 'failed', 'processing')),
    processing_duration_ms INTEGER NOT NULL DEFAULT 0,
    model_version TEXT NOT NULL,
    total_detections INTEGER NOT NULL DEFAULT 0,
    summary TEXT
);

CREATE INDEX IF NOT EXISTS idx_detection_runs_created_at ON detection_runs(created_at);
CREATE INDEX IF NOT EXISTS idx_detection_runs_status ON detection_runs(status);

CREATE TABLE IF NOT EXISTS detections (
    id TEXT PRIMARY KEY,
    detection_run_id TEXT NOT NULL,
    class_name TEXT NOT NULL,
    confidence REAL NOT NULL,
    severity TEXT NOT NULL CHECK(severity IN ('Safe', 'Low', 'Medium', 'High', 'Critical')),
    bounding_box_json TEXT NOT NULL,
    segmentation_mask_reference TEXT,
    estimated_area REAL,
    evidence_path TEXT,
    location TEXT DEFAULT 'Floor Surface',
    FOREIGN KEY(detection_run_id) REFERENCES detection_runs(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_detections_run_id ON detections(detection_run_id);
CREATE INDEX IF NOT EXISTS idx_detections_class ON detections(class_name);
CREATE INDEX IF NOT EXISTS idx_detections_severity ON detections(severity);

CREATE TABLE IF NOT EXISTS dataset_sources (
    id TEXT PRIMARY KEY,
    dataset_name TEXT NOT NULL,
    version TEXT NOT NULL,
    license TEXT NOT NULL,
    source_reference TEXT NOT NULL,
    download_status TEXT NOT NULL CHECK(download_status IN ('verified', 'ready', 'partial', 'external')),
    image_count INTEGER NOT NULL DEFAULT 0,
    annotation_count INTEGER NOT NULL DEFAULT 0,
    last_verified_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS training_runs (
    id TEXT PRIMARY KEY,
    model_name TEXT NOT NULL,
    dataset_version TEXT NOT NULL,
    configuration_json TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('completed', 'running', 'failed', 'queued')),
    started_at TEXT NOT NULL,
    completed_at TEXT,
    checkpoint_path TEXT,
    metrics_json TEXT,
    error_summary TEXT
);

CREATE TABLE IF NOT EXISTS model_registry (
    id TEXT PRIMARY KEY,
    model_version TEXT NOT NULL,
    task_type TEXT NOT NULL CHECK(task_type IN ('detection', 'segmentation')),
    artifact_path TEXT NOT NULL,
    trained_status TEXT NOT NULL CHECK(trained_status IN ('custom-trained and evaluated', 'pretrained but not custom-trained', 'training in progress', 'unavailable')),
    evaluation_metrics_json TEXT NOT NULL,
    created_at TEXT NOT NULL,
    active INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS application_settings (
    key TEXT PRIMARY KEY,
    value_json TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
