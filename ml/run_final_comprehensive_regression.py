import os
import sys
import json
import time

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from ml.predict_image import detect, get_model
from ml.predict_video import analyze_video

def run_evaluation():
    print("======================================================================")
    print("FLOOR GUARD AI — FINAL DETECTION REGRESSION & BENCHMARK SUITE")
    print("======================================================================")

    model, model_path, is_custom = get_model()
    print(f"Loaded Active Model: {model_path} (is_custom={is_custom})")

    tests = [
        {
            "id": "TC-01",
            "name": "Water Spill with Specular Glints",
            "category": "water_spill",
            "image_path": "public/assets/samples/gallery/water_spill.jpg",
            "expected_classes": ["Water Spill"],
            "allow_clean": False
        },
        {
            "id": "TC-02",
            "name": "Chemical Coolant Liquid Spill",
            "category": "chemical_spill",
            "image_path": "dataset/images/test/floor_hazard_chemical_coolant_spill_aug4_contrast.jpg",
            "expected_classes": ["Chemical Spill", "Water Spill"],
            "allow_clean": False
        },
        {
            "id": "TC-03",
            "name": "Broken Glass Fragments on Ceramic Walkway",
            "category": "broken_glass",
            "image_path": "dataset/images/test/floor_hazard_broken_glass_store_aug3_dim.jpg",
            "expected_classes": ["Broken Glass"],
            "allow_clean": False
        },
        {
            "id": "TC-04",
            "name": "Trailing Power Cable & Wire Obstruction",
            "category": "cable_wire",
            "image_path": "dataset/images/test/floor_hazard_cable_cord_hallway_aug0_orig.jpg",
            "expected_classes": ["Cable Wire", "Cable & Wire Hazard", "Cable & Wire Tripping Hazard"],
            "allow_clean": False
        },
        {
            "id": "TC-05",
            "name": "Dropped Plastic Water Bottle Obstacle (WhatsApp 11.45 AM)",
            "category": "obstacle_debris",
            "image_path": "uploads/originals/1793945880487_p77ihr.jpeg",
            "expected_classes": ["Obstacle Debris", "Obstacle & Debris", "Trash Litter"],
            "allow_clean": False
        },
        {
            "id": "TC-06",
            "name": "Overturned Soda Bottle with Red Label (WhatsApp 10.21 AM)",
            "category": "obstacle_debris",
            "image_path": "uploads/originals/1793940735673_hbhctx.jpeg",
            "expected_classes": ["Obstacle Debris", "Obstacle & Debris", "Trash Litter"],
            "allow_clean": False
        },
        {
            "id": "TC-07",
            "name": "Clear Beverage Container Bottle on Floor",
            "category": "obstacle_debris",
            "image_path": "dataset/images/test/coca_bottle_full_warm.jpg",
            "expected_classes": ["Obstacle Debris", "Obstacle & Debris", "Trash Litter"],
            "allow_clean": False
        },
        {
            "id": "TC-08",
            "name": "Clean Polished Ceramic Floor Tile (Negative Control)",
            "category": "clean_floor",
            "image_path": "public/assets/samples/gallery/clean_floor.jpg",
            "expected_classes": ["Clean Floor"],
            "allow_clean": True
        }
    ]

    results = []
    passed_count = 0
    t0 = time.time()

    for tc in tests:
        p = os.path.join(BASE_DIR, tc["image_path"])
        if not os.path.exists(p):
            print(f"[{tc['id']}] SKIPPED: Missing file {p}")
            continue

        res = detect(p)
        pred_cls = res.get("class_name", "Unknown")
        pred_conf = res.get("confidence", 0.0)
        pred_pct = res.get("confidence_percent", "0%")
        pred_sev = res.get("severity", "Unknown")
        bbox = res.get("bounding_box", {})
        total_dets = res.get("total_detections", 0)

        # Check match against expected classes
        is_pass = any(exp.lower() in pred_cls.lower() or pred_cls.lower() in exp.lower() for exp in tc["expected_classes"])
        if tc["category"] == "clean_floor":
            is_pass = (total_dets == 0 or pred_cls == "Clean Floor")

        if is_pass:
            passed_count += 1

        print(f"[{tc['id']}] {tc['name']}")
        print(f"  Expected: {tc['expected_classes']} | Predicted: {pred_cls} ({pred_pct}) | Severity: {pred_sev} | Pass: {is_pass}")
        if total_dets > 0 and pred_cls != "Clean Floor":
            print(f"  Box: {bbox}")

        results.append({
            "test_id": tc["id"],
            "name": tc["name"],
            "category": tc["category"],
            "file": tc["image_path"],
            "expected_classes": tc["expected_classes"],
            "predicted_class": pred_cls,
            "confidence": pred_conf,
            "confidence_percent": pred_pct,
            "severity": pred_sev,
            "bounding_box": bbox,
            "passed": is_pass
        })

    # Video Pipeline Evaluation
    print("\n--- Running Video Pipeline Benchmark ---")
    vid_file = os.path.join(BASE_DIR, "uploads", "originals", "1793954764960_gayjkr.mp4")
    vid_res = {}
    if os.path.exists(vid_file):
        vid_res = analyze_video(vid_file)
        unique_events = vid_res.get("consolidated_events", [])
        keyframes = vid_res.get("keyframes", [])
        print(f"  Sampled Keyframes: {len(keyframes)}")
        print(f"  Consolidated Hazard Incidents: {len(unique_events)}")
        for evt in unique_events:
            print(f"   -> Incident: {evt['hazard_class']} | Time: {evt['time_range']} | Conf: {evt['confidence_percent']} | Severity: {evt['severity']}")
        vid_pass = len(unique_events) >= 4 and len(keyframes) >= 6
    else:
        vid_pass = False

    elapsed = round(time.time() - t0, 2)
    overall_pass_rate = round((passed_count / max(1, len(results))) * 100, 1)

    report = {
        "report_title": "Floor Guard AI - Final Detection Regression & Accuracy Report",
        "timestamp": "2026-11-06T22:23:00Z",
        "model_checkpoint": model_path,
        "is_custom_trained": is_custom,
        "total_test_cases": len(results),
        "passed_test_cases": passed_count,
        "pass_rate_percent": f"{overall_pass_rate}%",
        "elapsed_seconds": elapsed,
        "test_results": results,
        "video_pipeline": {
            "tested_video": "1793954764960_gayjkr.mp4",
            "passed": vid_pass,
            "keyframes_analyzed": len(vid_res.get("keyframes", [])),
            "consolidated_hazard_events": len(vid_res.get("consolidated_events", [])),
            "temporal_events": vid_res.get("consolidated_events", [])
        },
        "quality_acceptance_verdict": "PASSED" if overall_pass_rate >= 85.0 and vid_pass else "NEEDS_ATTENTION"
    }

    out_p = os.path.join(BASE_DIR, "reports", "final_detection_regression_report.json")
    with open(out_p, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(f"\nFinal regression report saved to: {out_p}")
    print(f"Overall Image Pass Rate: {overall_pass_rate}% | Video Pipeline: {'PASS' if vid_pass else 'FAIL'}")

if __name__ == "__main__":
    run_evaluation()
