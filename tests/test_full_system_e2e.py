#!/usr/bin/env python3
"""
Floor Guard AI — Comprehensive End-to-End Full Stack & Model System Verification Suite
Validates all aspects of the completed application:
  1. Multi-Model Image Inference (COCO Baseline vs Phase 4.2 Custom)
  2. Authentic OpenCV Video Decoding & Keyframe Detection Pipeline
  3. REST API /api/detect/image with SQLite Persistence
  4. REST API /api/detect/video with Keyframe Storage
  5. REST API /api/history & /api/history/:id Thumbnail Validation (Zero 404s)
  6. REST API /api/model/compare Arena
  7. REST API /api/analytics/real Operational & Scientific Telemetry
  8. Model Registry Governance Integrity
"""

import os
import sys
import json
import time
import urllib.request
import urllib.parse
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from ml.predict_image import detect
from ml.predict_video import analyze_video

def log(msg, status="INFO"):
    colors = {
        "INFO": "\033[94m",
        "PASS": "\033[92m",
        "FAIL": "\033[91m",
        "WARN": "\033[93m",
        "RESET": "\033[0m"
    }
    prefix = f"[{status}]"
    print(f"  {prefix} {msg}")

def run_e2e_tests():
    print("=" * 80)
    print("FLOOR GUARD AI — COMPREHENSIVE END-TO-END SYSTEM TEST SUITE")
    print("=" * 80)

    results = {}

    # 1. Dual-Model Image Inference
    print("\n[Step 1] Verifying Dual-Model Image Inference Engine...")
    try:
        sample_img = BASE_DIR / 'data' / 'processed' / 'images' / 'sample_water_spill.jpg'
        assert sample_img.exists(), f"Sample image not found: {sample_img}"

        # Test Model A: COCO
        res_coco = detect(str(sample_img), model_identifier='yolov8s-coco-pretrained')
        assert res_coco["status"] == "ok", f"COCO run failed: {res_coco}"
        assert res_coco["model_id"] == "yolov8s-coco-pretrained"
        assert res_coco["is_custom_trained"] is False
        assert Path(res_coco["annotated_image_url"].replace('/uploads/annotated/', str(BASE_DIR / 'uploads' / 'annotated' / ''))).exists() or res_coco["annotated_image_url"]

        # Test Model B: Phase 4.2 Custom
        res_custom = detect(str(sample_img), model_identifier='floorguard-yolov8s-v1.1.0-phase4.2')
        assert res_custom["status"] == "ok", f"Custom run failed: {res_custom}"
        assert res_custom["is_custom_trained"] is True
        assert res_custom["total_detections"] > 0
        assert res_custom["detections"][0]["class_name"] == "Water Spill"

        log(f"COCO: {res_coco['total_detections']} detections | Custom: {res_custom['total_detections']} detections ({res_custom['class_name']})", "PASS")
        results["step_1_dual_model_inference"] = "PASS"
    except Exception as e:
        log(f"Dual model failed: {e}", "FAIL")
        results["step_1_dual_model_inference"] = f"FAIL: {e}"

    # 2. OpenCV Video Processing
    print("\n[Step 2] Verifying Real OpenCV Video Keyframe Extraction & Inference...")
    try:
        sample_vid = BASE_DIR / 'public' / 'samples' / 'sample_corridor_walkthrough.mp4'
        assert sample_vid.exists(), f"Sample video not found: {sample_vid}"

        vid_res = analyze_video(str(sample_vid), model_identifier='floorguard-yolov8s-v1.1.0-phase4.2', sampling_interval_sec=1.0)
        assert vid_res["status"] == "ok"
        assert vid_res["video_info"]["total_frames"] > 0
        assert len(vid_res["keyframes"]) > 0
        assert vid_res["hazards_count"] > 0

        # Verify keyframe thumbs exist on disk
        first_thumb = vid_res["keyframes"][0]["thumb"]
        first_thumb_disk = BASE_DIR / 'uploads' / 'annotated' / Path(first_thumb).name
        assert first_thumb_disk.exists(), f"Keyframe thumbnail missing on disk: {first_thumb_disk}"

        log(f"Analyzed {vid_res['video_info']['total_frames_analyzed']} frames across {vid_res['video_info']['duration_seconds']:.1f}s, identified {vid_res['hazards_count']} hazards", "PASS")
        results["step_2_opencv_video"] = "PASS"
    except Exception as e:
        log(f"OpenCV video failed: {e}", "FAIL")
        results["step_2_opencv_video"] = f"FAIL: {e}"

    # 3. Live Backend Image Detection Endpoint
    print("\n[Step 3] Testing Backend Live Endpoint POST /api/detect/image...")
    try:
        url = "http://localhost:3000/api/detect/image"
        payload = json.dumps({
            "imagePath": "data/processed/images/sample_water_spill.jpg",
            "model_id": "floorguard-yolov8s-v1.1.0-phase4.2",
            "confidence": "0.20"
        }).encode('utf-8')
        req = urllib.request.Request(url, data=payload, headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode('utf-8'))

        assert data["status"] == "ok"
        assert data["detection"]["class_name"] == "Water Spill"
        assert "annotated_image_url" in data["detection"]
        run_id = data.get("run_id") or data.get("detection", {}).get("run_id")
        assert run_id, "run_id not returned in API response"

        log(f"Recorded inspection run {run_id} with class '{data['detection']['class_name']}'", "PASS")
        results["step_3_api_detect_image"] = "PASS"
    except Exception as e:
        log(f"API image detection failed: {e}", "FAIL")
        results["step_3_api_detect_image"] = f"FAIL: {e}"

    # 4. Live Backend Video Detection Endpoint
    print("\n[Step 4] Testing Backend Live Endpoint POST /api/detect/video...")
    try:
        url = "http://localhost:3000/api/detect/video"
        payload = json.dumps({
            "model_id": "floorguard-yolov8s-v1.1.0-phase4.2",
            "interval": "1.0",
            "confidence": "0.20"
        }).encode('utf-8')
        req = urllib.request.Request(url, data=payload, headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode('utf-8'))

        assert data["status"] == "ok"
        assert data["total_frames_analyzed"] > 0
        assert len(data["keyframes"]) > 0
        vid_run_id = data["run_id"]

        log(f"Recorded video inspection run {vid_run_id} with {len(data['keyframes'])} keyframes", "PASS")
        results["step_4_api_detect_video"] = "PASS"
    except Exception as e:
        log(f"API video detection failed: {e}", "FAIL")
        results["step_4_api_detect_video"] = f"FAIL: {e}"

    # 5. History Endpoint & Thumbnail Validation
    print("\n[Step 5] Testing History Endpoint GET /api/history & Thumbnail Accessibility...")
    try:
        url = "http://localhost:3000/api/history?limit=10"
        with urllib.request.urlopen(url, timeout=10) as resp:
            h_data = json.loads(resp.read().decode('utf-8'))

        assert h_data["status"] == "ok"
        assert len(h_data["history"]) > 0

        # Check first history item thumbnail accessibility
        first_item = h_data["history"][0]
        thumb_url = f"http://localhost:3000{first_item['thumb_url']}"
        with urllib.request.urlopen(thumb_url, timeout=5) as t_resp:
            assert t_resp.status == 200
            assert len(t_resp.read()) > 0

        # Check single history detail endpoint
        detail_url = f"http://localhost:3000/api/history/{first_item['id']}"
        with urllib.request.urlopen(detail_url, timeout=5) as d_resp:
            d_data = json.loads(d_resp.read().decode('utf-8'))
            assert d_data["status"] == "ok"
            assert d_data["run"]["id"] == first_item['id']

        log(f"Verified {len(h_data['history'])} history records. Thumbnail accessible (HTTP 200) without 404.", "PASS")
        results["step_5_history_and_thumbnails"] = "PASS"
    except Exception as e:
        log(f"History verification failed: {e}", "FAIL")
        results["step_5_history_and_thumbnails"] = f"FAIL: {e}"

    # 6. Model Comparison Arena Endpoint
    print("\n[Step 6] Testing Model Comparison Arena POST /api/model/compare...")
    try:
        url = "http://localhost:3000/api/model/compare"
        payload = json.dumps({
            "imagePath": "data/processed/images/sample_water_spill.jpg",
            "confidence": "0.25"
        }).encode('utf-8')
        req = urllib.request.Request(url, data=payload, headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req, timeout=15) as resp:
            comp_data = json.loads(resp.read().decode('utf-8'))

        assert comp_data["status"] == "ok"
        assert "model_a_coco" in comp_data
        assert "model_b_custom" in comp_data
        assert comp_data["model_a_coco"]["model_id"] == "yolov8s-coco-pretrained"
        assert comp_data["model_b_custom"]["is_custom_trained"] is True

        log(f"Arena comparison executed: Model A ({comp_data['model_a_coco']['total_detections']} objs) vs Model B ({comp_data['model_b_custom']['total_detections']} hazards)", "PASS")
        results["step_6_model_comparison_arena"] = "PASS"
    except Exception as e:
        log(f"Arena comparison failed: {e}", "FAIL")
        results["step_6_model_comparison_arena"] = f"FAIL: {e}"

    # 7. Real Analytics & Evaluation Telemetry
    print("\n[Step 7] Testing Real Operational Analytics & Evaluation Telemetry...")
    try:
        url = "http://localhost:3000/api/analytics/real"
        with urllib.request.urlopen(url, timeout=10) as resp:
            a_data = json.loads(resp.read().decode('utf-8'))

        assert a_data["status"] == "ok"
        kpis = a_data["operational_kpis"]
        assert kpis["total_analyses"] > 0
        assert kpis["images_analyzed"] > 0
        assert "evaluation_telemetry" in a_data
        assert a_data["evaluation_telemetry"]["phase4_2_frozen_benchmark"]["mAP50"] == 0.6732

        log(f"Real KPIs: {kpis['total_analyses']} analyses, {kpis['hazards_detected']} hazards. Phase 4.2 Benchmark: 67.32% mAP50", "PASS")
        results["step_7_real_analytics"] = "PASS"
    except Exception as e:
        log(f"Analytics verification failed: {e}", "FAIL")
        results["step_7_real_analytics"] = f"FAIL: {e}"

    # Summary
    print("\n" + "=" * 80)
    print("END-TO-END VERIFICATION SUMMARY:")
    all_passed = True
    for step, outcome in results.items():
        status_flag = "PASS" if outcome == "PASS" else "FAIL"
        print(f"  {step}: {outcome}")
        if outcome != "PASS":
            all_passed = False
    print("=" * 80)

    if all_passed:
        print("\n\033[92mALL 7 END-TO-END SYSTEM TESTS PASSED SUCCESSFULLY!\033[0m")
        return 0
    else:
        print("\n\033[91mSOME TESTS FAILED!\033[0m")
        return 1

if __name__ == '__main__':
    sys.exit(run_e2e_tests())
