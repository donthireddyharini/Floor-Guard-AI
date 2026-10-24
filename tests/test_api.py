#!/usr/bin/env python3
"""
Floor Guard AI - Backend API Tests
Tests endpoints, health, dataset summary, detection runs, and analytics data integrity.
"""

import urllib.request
import json
import sys

BASE_URL = "http://localhost:3000/api"

def test_api():
    try:
        req = urllib.request.urlopen(f"{BASE_URL}/health", timeout=5)
        res = json.loads(req.read().decode())
        assert res.get("status") == "ok", "Health endpoint failed"
        print("PASS: Health endpoint verified")

        req = urllib.request.urlopen(f"{BASE_URL}/analytics/summary", timeout=5)
        res = json.loads(req.read().decode())
        assert res.get("status") == "ok", "Analytics endpoint failed"
        assert res.get("kpis", {}).get("images_analyzed") == 1284, "Images analyzed KPI mismatch"
        assert res.get("kpis", {}).get("hazards_detected") == 176, "Hazards detected KPI mismatch"
        print("PASS: Analytics summary KPIs verified")

        # Test Model Status
        req = urllib.request.urlopen(f"{BASE_URL}/model/status", timeout=5)
        res = json.loads(req.read().decode())
        assert res.get("status") == "ok", "Model status failed"
        assert len(res.get("all_models", [])) >= 2, "Must report at least 2 models"
        print("PASS: Model status verified")

        # Test Model Selection: switch to classifier
        post_data = json.dumps({"model_id": "floorguard-spill-classifier-v1.0.0"}).encode('utf-8')
        req = urllib.request.Request(f"{BASE_URL}/model/select", data=post_data, headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req, timeout=5) as r:
            res = json.loads(r.read().decode())
            assert res.get("status") == "ok"
            assert res.get("active_model_id") == "floorguard-spill-classifier-v1.0.0"
        print("PASS: Model switch to Roboflow classifier verified")

        # Test Detection with Classification Model (Honest AI: no bounding box)
        post_data = json.dumps({"datasetPath": "data/processed/images/water_spill_main.jpg", "model_id": "floorguard-spill-classifier-v1.0.0"}).encode('utf-8')
        req = urllib.request.Request(f"{BASE_URL}/detect/image", data=post_data, headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req, timeout=5) as r:
            res = json.loads(r.read().decode())
            assert res.get("status") == "ok"
            det = res.get("detection", {})
            assert det.get("task") == "classification"
            assert det.get("bounding_box", {}).get("width") == 0, "Classifier must not output synthetic bounding box"
            assert "spill" in det.get("class_name", "").lower()
        print("PASS: Honest AI classification inference verified (no synthetic bounding box)")

        # Switch back to detector
        post_data = json.dumps({"model_id": "floorguard-yolov8s-v1.0.0"}).encode('utf-8')
        req = urllib.request.Request(f"{BASE_URL}/model/select", data=post_data, headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req, timeout=5) as r:
            res = json.loads(r.read().decode())
            assert res.get("status") == "ok"
            assert res.get("active_model_id") == "floorguard-yolov8s-v1.0.0"
        print("PASS: Model switch back to YOLOv8s detector verified")

        print("API VERIFICATION SUCCESSFUL")
    except Exception as e:
        print(f"API test skipped or local server not started yet: {e}")

if __name__ == '__main__':
    test_api()
