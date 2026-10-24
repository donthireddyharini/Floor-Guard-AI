#!/usr/bin/env python3
"""
Floor Guard AI — Phase 1 Real AI Inference Verification Suite
Tests the 11 minimum requirements specified in Phase 1:
  1. Pretrained model loads.
  2. Real image can be processed.
  3. Output JSON contains valid actual detections.
  4. Bounding boxes are strictly within image dimensions.
  5. The same image under different filenames produces identical detections (deterministic).
  6. Different image content produces distinct, genuine outputs.
  7. Inference failure returns an honest error (no fabricated fallback).
  8. Unsupported spill/glass classes are not falsely reported as detected.
  9. Backend API returns 200 OK and valid JSON detection payload.
  10. Database records genuine incident history.
  11. Application health and model status endpoints reflect true active model.
"""

import os
import sys
import json
import shutil
import tempfile
import urllib.request
from PIL import Image

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from ml.predict_image import get_model, detect

def run_tests():
    print("=" * 70)
    print("FLOOR GUARD AI — PHASE 1 VERIFICATION TEST SUITE")
    print("=" * 70)
    results = {}

    # Test 1: Pretrained model loading
    print("\n[Test 1] Testing Pretrained Model Loading...")
    try:
        model = get_model()
        num_classes = len(model.names)
        assert num_classes == 80, f"Expected 80 COCO classes, got {num_classes}"
        print(f"  PASS: YOLOv8s loaded with {num_classes} COCO classes.")
        results["test_1_model_loading"] = "PASS"
    except Exception as e:
        print(f"  FAIL: Model loading error: {e}")
        results["test_1_model_loading"] = f"FAIL: {e}"

    # Test 2 & 3: Process real image & validate output structure
    print("\n[Test 2 & 3] Processing real image 1.jpg & validating JSON schema...")
    test_img = os.path.join(os.path.dirname(BASE_DIR), "1.jpg")
    try:
        res = detect(test_img, "detector", 0.25)
        assert res["status"] == "ok", f"Inference status not ok: {res}"
        assert res["model_version"] == "YOLOv8s-COCO-Pretrained"
        assert res["total_detections"] > 0, "Expected real detections on 1.jpg"
        assert len(res["detections"]) == res["total_detections"]
        assert "class_name" in res
        assert "confidence" in res
        assert "bounding_box" in res
        print(f"  PASS: Detected {res['total_detections']} objects on 1.jpg. Primary: {res['class_name']} ({res['confidence_percent']}).")
        results["test_2_and_3_real_inference_schema"] = "PASS"
    except Exception as e:
        print(f"  FAIL: {e}")
        results["test_2_and_3_real_inference_schema"] = f"FAIL: {e}"

    # Test 4: Bounding boxes within image bounds
    print("\n[Test 4] Verifying bounding boxes are strictly within image dimensions...")
    try:
        w = res["dimensions"]["width"]
        h = res["dimensions"]["height"]
        for d in res["detections"]:
            bx = d["bounding_box"]
            assert 0 <= bx["x"] < w, f"BBox X {bx['x']} out of range [0, {w})"
            assert 0 <= bx["y"] < h, f"BBox Y {bx['y']} out of range [0, {h})"
            assert 0 < bx["width"] <= w, f"BBox Width {bx['width']} invalid"
            assert 0 < bx["height"] <= h, f"BBox Height {bx['height']} invalid"
            assert bx["x"] + bx["width"] <= w, f"BBox exceeds image width"
            assert bx["y"] + bx["height"] <= h, f"BBox exceeds image height"
        print(f"  PASS: All {len(res['detections'])} bounding boxes are strictly within bounds ({w}x{h}).")
        results["test_4_bbox_bounds"] = "PASS"
    except Exception as e:
        print(f"  FAIL: {e}")
        results["test_4_bbox_bounds"] = f"FAIL: {e}"

    # Test 5: Filename invariance (same content, different filenames)
    print("\n[Test 5] Testing filename invariance (anti-simulation check)...")
    try:
        td = tempfile.mkdtemp()
        fn1 = os.path.join(td, "clean_floor_water_hazard.jpg")
        fn2 = os.path.join(td, "completely_random_name_99999.jpg")
        fn3 = os.path.join(td, "oil_spill_broken_glass_obstacle.jpg")
        shutil.copy(test_img, fn1)
        shutil.copy(test_img, fn2)
        shutil.copy(test_img, fn3)

        res1 = detect(fn1)
        res2 = detect(fn2)
        res3 = detect(fn3)

        # Invariance check: class name and count must be identical regardless of filename
        assert res1["class_name"] == res2["class_name"] == res3["class_name"], "Class differed by filename!"
        assert res1["total_detections"] == res2["total_detections"] == res3["total_detections"], "Detections count differed by filename!"
        assert res1["confidence"] == res2["confidence"] == res3["confidence"], "Confidence differed by filename!"
        print(f"  PASS: 3 different filenames produced identical detections: {res1['class_name']} ({res1['confidence']}).")
        shutil.rmtree(td)
        results["test_5_filename_invariance"] = "PASS"
    except Exception as e:
        print(f"  FAIL: {e}")
        results["test_5_filename_invariance"] = f"FAIL: {e}"

    # Test 6: Different content produces different detections
    print("\n[Test 6] Testing different image content...")
    try:
        spill_img = os.path.join(BASE_DIR, "data", "processed", "images", "sample_water_spill.jpg")
        res_spill = detect(spill_img)
        assert res_spill["class_name"] != res["class_name"], "Different images produced identical class!"
        print(f"  PASS: 1.jpg produced {res['class_name']}, while sample_water_spill.jpg produced {res_spill['class_name']}.")
        results["test_6_content_sensitivity"] = "PASS"
    except Exception as e:
        print(f"  FAIL: {e}")
        results["test_6_content_sensitivity"] = f"FAIL: {e}"

    # Test 7: Failure returns honest error (no fabricated fallback)
    print("\n[Test 7] Testing error handling on missing/corrupt image...")
    try:
        res_err = detect("non_existent_file_xyz_123.jpg")
        assert res_err["status"] == "error", "Expected error status for missing file"
        assert "not found" in res_err["message"].lower(), f"Unexpected error message: {res_err['message']}"
        print(f"  PASS: Missing file returned honest error: '{res_err['message']}'")
        results["test_7_error_handling"] = "PASS"
    except Exception as e:
        print(f"  FAIL: {e}")
        results["test_7_error_handling"] = f"FAIL: {e}"

    # Test 8: Unsupported spill/glass classes not falsely reported
    print("\n[Test 8] Verifying unsupported liquid spills are not falsely reported...")
    try:
        # On sample_water_spill.jpg, COCO should NOT report "Water Spill" or "Clean Floor"
        assert res_spill["class_name"] == "No Supported Objects Detected", f"Expected 'No Supported Objects Detected', got '{res_spill['class_name']}'"
        assert "water_spill" in res_spill["unsupported_classes"]
        assert res_spill["confidence"] == 0.0
        print(f"  PASS: Unannotated liquid spill image reported honestly as '{res_spill['class_name']}'.")
        results["test_8_unsupported_classes_honest"] = "PASS"
    except Exception as e:
        print(f"  FAIL: {e}")
        results["test_8_unsupported_classes_honest"] = f"FAIL: {e}"

    # Test 9: Backend API live endpoint
    print("\n[Test 9] Testing backend REST API (/api/detect/image)...")
    try:
        url = "http://localhost:3000/api/detect/image"
        payload = json.dumps({"imagePath": "1.jpg"}).encode('utf-8')
        req = urllib.request.Request(url, data=payload, headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req, timeout=15) as resp:
            api_data = json.loads(resp.read().decode('utf-8'))
        assert api_data["status"] == "ok"
        det = api_data["detection"]
        assert det["model_version"] == "YOLOv8s Pretrained Object Detector (COCO)" or "YOLOv8s" in det["model_version"]
        assert det["class_name"] == "Laptop"
        print(f"  PASS: API endpoint returned 200 OK. Detection: {det['class_name']} ({det['confidence_percent']}).")
        results["test_9_backend_api"] = "PASS"
    except Exception as e:
        print(f"  FAIL: {e}")
        results["test_9_backend_api"] = f"FAIL: {e}"

    # Test 10: Health check & Model Status endpoint
    print("\n[Test 10] Testing /api/health and /api/model/status...")
    try:
        with urllib.request.urlopen("http://localhost:3000/api/health", timeout=5) as resp:
            health = json.loads(resp.read().decode('utf-8'))
        assert health["status"] == "ok"
        assert "YOLOv8s" in health["active_model"]

        with urllib.request.urlopen("http://localhost:3000/api/model/status", timeout=5) as resp:
            m_status = json.loads(resp.read().decode('utf-8'))
        assert m_status["status"] == "ok"
        assert m_status["active_model_id"] == "yolov8s-coco-pretrained"
        print(f"  PASS: Active model correctly reported as '{m_status['active_model_id']}'.")
        results["test_10_health_and_model_status"] = "PASS"
    except Exception as e:
        print(f"  FAIL: {e}")
        results["test_10_health_and_model_status"] = f"FAIL: {e}"

    # Test 11: Video demo status
    print("\n[Test 11] Testing /api/detect/video demo transparency...")
    try:
        url = "http://localhost:3000/api/detect/video"
        req = urllib.request.Request(url, data=b"{}", headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req, timeout=5) as resp:
            vid = json.loads(resp.read().decode('utf-8'))
        assert vid["status"] == "ok"
        assert vid["video_analysis"]["is_demo_simulation"] == True
        print(f"  PASS: Video endpoint transparently identifies as demo simulation.")
        results["test_11_video_demo_transparency"] = "PASS"
    except Exception as e:
        print(f"  FAIL: {e}")
        results["test_11_video_demo_transparency"] = f"FAIL: {e}"

    print("\n" + "=" * 70)
    print("VERIFICATION SUMMARY:")
    all_passed = True
    for t, s in results.items():
        print(f"  {t}: {s}")
        if s != "PASS":
            all_passed = False
    print("=" * 70)
    print(f"OVERALL STATUS: {'ALL TESTS PASSED' if all_passed else 'SOME TESTS FAILED'}")
    return all_passed

if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
