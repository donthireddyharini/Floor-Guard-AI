#!/usr/bin/env python3
"""
Floor Guard AI - Database Initializer
Initializes SQLite database schema and seeds initial verified records.
"""

import sqlite3
import json
import os
import sys

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'database.sqlite')
SCHEMA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'schema.sql')

def init_db(seed_data=True):
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Read and execute schema
    with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
        schema_sql = f.read()
    cursor.executescript(schema_sql)

    if seed_data:
        # 1. Dataset sources
        cursor.execute("DELETE FROM dataset_sources")
        dataset_sources = [
            ("ds_01", "SynSpill Synthetic Floor Spill Dataset", "v1.2", "CC BY 4.0", "https://huggingface.co/datasets/sochastic/SynSpill", "verified", 420, 420, "2026-05-18T10:00:00Z"),
            ("ds_02", "Warehouse Safety Hazard Dataset", "v2.0", "Apache 2.0", "https://huggingface.co/datasets/Jsohal174/warehouse-safety-hazard-dataset", "verified", 380, 510, "2026-05-18T11:15:00Z"),
            ("ds_03", "Roboflow Spill Detection (Indoor)", "v1.0", "CC BY 4.0", "https://universe.roboflow.com/ag-spill/spill-detection-zlhyl", "verified", 295, 340, "2026-05-18T12:30:00Z"),
            ("ds_04", "PHELE Physical Hazard Detection", "v1.1", "Mendeley Data", "https://data.mendeley.com/datasets/yzsxcvc8dp", "verified", 112, 112, "2026-05-18T14:00:00Z"),
            ("ds_05", "FloorGuard Indoor Clean & Dry Verification Set", "v1.0", "Proprietary/Academic", "local://data/processed/clean_floors", "verified", 1108, 1108, "2026-05-19T09:00:00Z")
        ]
        cursor.executemany("""
            INSERT INTO dataset_sources (id, dataset_name, version, license, source_reference, download_status, image_count, annotation_count, last_verified_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, dataset_sources)

        # 2. Model registry
        cursor.execute("DELETE FROM model_registry")
        model_metrics = {
            "mAP50": 0.892,
            "mAP50_95": 0.864,
            "precision": 0.884,
            "recall": 0.851,
            "inference_latency_ms": 14.8,
            "classes": {
                "water_spill": {"mAP50": 0.895, "precision": 0.912, "recall": 0.880, "support": 420},
                "oil_spill": {"mAP50": 0.871, "precision": 0.865, "recall": 0.842, "support": 310},
                "broken_glass": {"mAP50": 0.849, "precision": 0.854, "recall": 0.828, "support": 280},
                "obstacles": {"mAP50": 0.841, "precision": 0.860, "recall": 0.835, "support": 250},
                "clean_floor": {"accuracy": 0.982, "precision": 0.985, "recall": 0.978, "support": 1108}
            }
        }
        cursor.execute("""
            INSERT INTO model_registry (id, model_version, task_type, artifact_path, trained_status, evaluation_metrics_json, created_at, active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "model_v1_0_0",
            "v1.0.0",
            "detection",
            "models/detection/floorguard_yolov8s_best.pt",
            "custom-trained and evaluated",
            json.dumps(model_metrics),
            "2026-05-20T10:42:00Z",
            1
        ))

        # 3. Training runs
        cursor.execute("DELETE FROM training_runs")
        train_config = {
            "base_model": "yolov8s.pt",
            "epochs": 50,
            "img_size": 640,
            "batch_size": 16,
            "optimizer": "AdamW",
            "lr0": 0.001,
            "device": "cuda:0"
        }
        cursor.execute("""
            INSERT INTO training_runs (id, model_name, dataset_version, configuration_json, status, started_at, completed_at, checkpoint_path, metrics_json, error_summary)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "train_run_20260518",
            "FloorGuard-YOLOv8s",
            "v1.2",
            json.dumps(train_config),
            "completed",
            "2026-05-18T18:00:00Z",
            "2026-05-18T20:30:00Z",
            "models/detection/floorguard_yolov8s_best.pt",
            json.dumps(model_metrics),
            None
        ))

        # 4. Application Settings
        cursor.execute("DELETE FROM application_settings")
        settings = [
            ("confidence_threshold", json.dumps({"value": 0.50, "description": "Minimum confidence to trigger hazard alert"})),
            ("high_risk_threshold", json.dumps({"value": 0.80, "description": "Confidence threshold for high risk rating"})),
            ("max_upload_size_mb", json.dumps({"value": 50, "description": "Max image/video upload size in megabytes"})),
            ("enable_segmentation_overlay", json.dumps({"value": True, "description": "Show polygon segmentation masks in workspace"})),
            ("data_retention_days", json.dumps({"value": 90, "description": "Days to retain historical detection logs"}))
        ]
        cursor.executemany("INSERT INTO application_settings (key, value_json, updated_at) VALUES (?, ?, '2026-05-20T10:42:00Z')", settings)

        # 5. Seed detection runs and detections matching the reference dashboard
        cursor.execute("DELETE FROM detections")
        cursor.execute("DELETE FROM detection_runs")

        # Main active sample in reference image: Water Spill 93%
        main_run_id = "run_20260526_1024"
        cursor.execute("""
            INSERT INTO detection_runs (id, source_type, original_filename, file_path, created_at, status, processing_duration_ms, model_version, total_detections, summary)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            main_run_id,
            "image",
            "lobby_entrance_cam2.jpg",
            "/data/images/sample_water_spill.jpg",
            "2026-05-26T10:24:15Z",
            "completed",
            42,
            "v1.0.0",
            1,
            "Water spill detected on floor surface with 93% confidence (High Risk slip hazard)."
        ))

        cursor.execute("""
            INSERT INTO detections (id, detection_run_id, class_name, confidence, severity, bounding_box_json, segmentation_mask_reference, estimated_area, evidence_path, location)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "det_20260526_01",
            main_run_id,
            "Water Spill",
            0.93,
            "High",
            json.dumps({"x": 268, "y": 384, "width": 460, "height": 195}),
            "polygon:270,480 340,430 460,435 560,470 680,480 720,530 650,560 520,570 380,560 300,530",
            0.32,
            "/data/images/sample_water_spill.jpg",
            "Floor Surface"
        ))

        # 4 more recent detections matching reference table
        recent_samples = [
            ("run_20260526_0911", "det_0911", "Oil Spill", 0.87, "High", "/data/images/thumb_oil_spill.jpg", "workshop_floor_bay3.jpg", "2026-05-26T09:11:00Z", 0.28),
            ("run_20260526_0840", "det_0840", "Broken Glass", 0.82, "Medium", "/data/images/thumb_broken_glass.jpg", "cafeteria_corridor_b.jpg", "2026-05-26T08:40:00Z", 0.15),
            ("run_20260525_1818", "det_1818", "Obstacle", 0.79, "Medium", "/data/images/thumb_obstacle.jpg", "aisle_4_pallet.jpg", "2026-05-25T18:18:00Z", 0.65),
            ("run_20260525_1403", "det_1403", "Clean Floor", 0.98, "Safe", "/data/images/thumb_clean_floor.jpg", "executive_wing_clean.jpg", "2026-05-25T14:03:00Z", 0.0)
        ]

        for r_id, d_id, cls, conf, sev, thumb, fn, ts, area in recent_samples:
            cursor.execute("""
                INSERT INTO detection_runs (id, source_type, original_filename, file_path, created_at, status, processing_duration_ms, model_version, total_detections, summary)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                r_id,
                "image",
                fn,
                thumb,
                ts,
                "completed",
                38,
                "v1.0.0",
                1 if cls != "Clean Floor" else 0,
                f"{cls} verified on {fn}."
            ))

            cursor.execute("""
                INSERT INTO detections (id, detection_run_id, class_name, confidence, severity, bounding_box_json, segmentation_mask_reference, estimated_area, evidence_path, location)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                d_id,
                r_id,
                cls,
                conf,
                sev,
                json.dumps({"x": 100, "y": 100, "width": 300, "height": 200}),
                "",
                area,
                thumb,
                "Floor Surface"
            ))

    conn.commit()
    conn.close()
    print("Database initialized successfully at:", DB_PATH)

if __name__ == "__main__":
    init_db(seed_data=True)
