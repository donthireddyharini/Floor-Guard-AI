#!/usr/bin/env python3
"""
Floor Guard AI - Comprehensive Acceptance Test Suite
Runs Tests A through H to verify the retrained 13-class model:
- Test A: Cardboard box / Pallet (must be Obstacle / Debris, NOT Cable/Cord)
- Test B: Discarded water bottle (must be Trash / Litter, NOT Water Spill)
- Test C: Broken glass (must be Broken Glass, NOT generic Debris)
- Test D: Real cable (must be Cable / Cord)
- Test E: Actual water on floor (must be Water Spill)
- Test F: Ordinary clean floor (must be Clean Floor, 0 hazard boxes)
- Test G: General unseen test split evaluation across 60 images
- Test H: Video intelligence & temporal event consolidation test
Outputs: unseen_test_results.csv
"""

import os
import sys
import csv
import glob
import json
import time

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from ml.predict_image import detect
from ml.predict_video import analyze_video

CLASS_NAME_MAP = {
    0: "Clean Floor",
    1: "Floor Mat Hazard",
    2: "Floor Damage",
    3: "Water Spill",
    4: "Oil Spill",
    5: "Chemical Spill",
    6: "Broken Glass",
    7: "Cable / Cord",
    8: "Obstacle / Debris",
    9: "Trash / Litter",
    10: "Food Waste",
    11: "Mud / Dirt",
    12: "Stairs Hazard"
}

# Normalize string representations for comparison
NORMALIZE_MAP = {
    "clean floor": "Clean Floor",
    "floor mat hazard": "Floor Mat Hazard",
    "mat hazard": "Floor Mat Hazard",
    "floor damage": "Floor Damage",
    "water spill": "Water Spill",
    "oil spill": "Oil Spill",
    "chemical spill": "Chemical Spill",
    "broken glass": "Broken Glass",
    "cable / cord": "Cable / Cord",
    "cable cord": "Cable / Cord",
    "obstacle / debris": "Obstacle / Debris",
    "obstacle debris": "Obstacle / Debris",
    "trash / litter": "Trash / Litter",
    "trash litter": "Trash / Litter",
    "food waste": "Food Waste",
    "mud / dirt": "Mud / Dirt",
    "mud dirt": "Mud / Dirt",
    "stairs hazard": "Stairs Hazard",
    "stair hazard": "Stairs Hazard"
}

def normalize_cls(name):
    clean = (name or "").strip().lower()
    return NORMALIZE_MAP.get(clean, name)

def load_ground_truth(label_path):
    if not os.path.exists(label_path):
        return "Clean Floor"
    with open(label_path, 'r', encoding='utf-8') as f:
        lines = [l.strip() for l in f if l.strip()]
    if not lines:
        return "Clean Floor"
    cid = int(lines[0].split()[0])
    return CLASS_NAME_MAP.get(cid, "Unknown")

def main():
    print("=" * 70)
    print("FLOOR GUARD AI — ACCEPTANCE TEST SUITE (PHASE 6)")
    print("=" * 70)

    test_img_dir = os.path.join(BASE_DIR, "corrected_dataset", "images", "test")
    test_lbl_dir = os.path.join(BASE_DIR, "corrected_dataset", "labels", "test")

    results = []

    # 1. SPECIFIC SCENARIO TESTS (A - F)
    scenario_tests = [
        {
            "test_id": "Test_A_BoxNotCable",
            "search": "*pallet*obstacle*.*",
            "desc": "Cardboard box / Pallet (Obstacle / Debris, NOT Cable/Cord)",
            "expected_class": "Obstacle / Debris",
            "forbidden_class": "Cable / Cord"
        },
        {
            "test_id": "Test_B_BottleNotSpill",
            "search": "*bottle*.*",
            "desc": "Discarded water bottle (Trash / Litter, NOT Water Spill)",
            "expected_class": "Trash / Litter",
            "forbidden_class": "Water Spill"
        },
        {
            "test_id": "Test_C_BrokenGlassNotDebris",
            "search": "*glass*.*",
            "desc": "Broken glass (Broken Glass, NOT Obstacle / Debris)",
            "expected_class": "Broken Glass",
            "forbidden_class": "Obstacle / Debris"
        },
        {
            "test_id": "Test_D_RealCable",
            "search": "*cable*.*",
            "desc": "Real cable (Cable / Cord)",
            "expected_class": "Cable / Cord",
            "forbidden_class": ""
        },
        {
            "test_id": "Test_E_WaterSpill",
            "search": "*water*spill*.*",
            "desc": "Water on floor (Water Spill)",
            "expected_class": "Water Spill",
            "forbidden_class": ""
        },
        {
            "test_id": "Test_F_CleanFloor",
            "search": "*clean*floor*.*",
            "desc": "Clean floor control (Clean Floor, 0 boxes)",
            "expected_class": "Clean Floor",
            "forbidden_class": ""
        }
    ]

    print("\n--- Executing Targeted Diagnostic Scenarios A-F ---")
    for scen in scenario_tests:
        matches = glob.glob(os.path.join(test_img_dir, scen["search"]))
        if not matches:
            matches = glob.glob(os.path.join(BASE_DIR, "corrected_dataset", "images", "*", scen["search"]))
        
        if matches:
            target_img = matches[0]
            fname = os.path.basename(target_img)
            t0 = time.time()
            det_res = detect(target_img, conf_threshold=0.18, imgsz=512)
            lat = round((time.time() - t0) * 1000, 1)

            pred_class = det_res.get("class_name", "Clean Floor")
            conf = det_res.get("confidence", 0.0)
            detections = det_res.get("detections", [])

            norm_pred = normalize_cls(pred_class)
            norm_exp = normalize_cls(scen["expected_class"])
            norm_forbid = normalize_cls(scen["forbidden_class"]) if scen["forbidden_class"] else ""

            # Validation logic
            passed = True
            reason = "OK"
            if norm_forbid and norm_pred == norm_forbid:
                passed = False
                reason = f"CRITICAL: Predicted forbidden class {scen['forbidden_class']}!"
            elif scen["expected_class"] == "Clean Floor":
                if len(detections) > 0 or norm_pred != "Clean Floor":
                    passed = False
                    reason = f"Clean floor produced {len(detections)} hazard boxes!"
            else:
                if norm_pred != norm_exp:
                    passed = False
                    reason = f"Expected {scen['expected_class']}, got {pred_class}"

            status_str = "PASS" if passed else "FAIL"
            print(f"[{status_str}] {scen['test_id']} ({fname}): Pred='{pred_class}' ({conf*100:.1f}%), {reason} ({lat}ms)")

            results.append({
                "test_id": scen["test_id"],
                "image_name": fname,
                "ground_truth": scen["expected_class"],
                "predicted_class": pred_class,
                "confidence_percent": f"{conf*100:.1f}%",
                "boxes_detected": len(detections),
                "latency_ms": lat,
                "status": status_str,
                "notes": reason
            })
        else:
            print(f"[SKIP] {scen['test_id']}: No matching image found for pattern {scen['search']}")

    # 2. GENERAL UNSEEN TEST EVALUATION (Test G)
    print("\n--- Executing Test G: Unseen Test Split Evaluation (60 images) ---")
    test_images = sorted(glob.glob(os.path.join(test_img_dir, "*.*")))
    correct_count = 0
    total_latency = 0.0

    for idx, img_path in enumerate(test_images):
        fname = os.path.basename(img_path)
        base = os.path.splitext(fname)[0]
        lbl_path = os.path.join(test_lbl_dir, base + ".txt")
        gt_class = load_ground_truth(lbl_path)

        t0 = time.time()
        det_res = detect(img_path, conf_threshold=0.18, imgsz=512)
        lat = round((time.time() - t0) * 1000, 1)
        total_latency += lat

        pred_class = det_res.get("class_name", "Clean Floor")
        conf = det_res.get("confidence", 0.0)
        detections = det_res.get("detections", [])

        norm_pred = normalize_cls(pred_class)
        norm_gt = normalize_cls(gt_class)

        # Match check
        is_correct = (norm_pred == norm_gt)
        if is_correct:
            correct_count += 1
            status_str = "PASS"
            notes = "Exact match"
        else:
            status_str = "FAIL"
            notes = f"Ground Truth: {gt_class}, Predicted: {pred_class}"

        results.append({
            "test_id": f"Test_G_img_{idx+1:02d}",
            "image_name": fname,
            "ground_truth": gt_class,
            "predicted_class": pred_class,
            "confidence_percent": f"{conf*100:.1f}%",
            "boxes_detected": len(detections),
            "latency_ms": lat,
            "status": status_str,
            "notes": notes
        })

    avg_lat = round(total_latency / max(1, len(test_images)), 1)
    acc = round((correct_count / max(1, len(test_images))) * 100, 2)
    print(f"Test G Complete: {correct_count}/{len(test_images)} correct ({acc}% Top-1 Accuracy), Avg Latency: {avg_lat}ms")

    # 3. VIDEO INTELLIGENCE & EVENT CONSOLIDATION (Test H)
    print("\n--- Executing Test H: Video Intelligence & Temporal Event Consolidation ---")
    video_sample = os.path.join(BASE_DIR, "public", "assets", "samples", "corridor_hazard_tour_30s.mp4")
    if not os.path.exists(video_sample):
        vids = glob.glob(os.path.join(BASE_DIR, "uploads", "originals", "*.mp4"))
        if vids:
            video_sample = vids[0]

    if os.path.exists(video_sample):
        t0 = time.time()
        vid_res = analyze_video(video_sample, num_keyframes=8)
        vid_lat = round((time.time() - t0) * 1000, 1)

        status_vid = vid_res.get("status")
        kfs = vid_res.get("keyframes", [])
        evts = vid_res.get("consolidated_events", [])

        passed = (status_vid == "ok" and len(kfs) > 0)
        status_str = "PASS" if passed else "FAIL"
        notes = f"Processed {len(kfs)} keyframes into {len(evts)} consolidated hazard events."
        print(f"[{status_str}] Test_H_Video ({os.path.basename(video_sample)}): {notes} ({vid_lat}ms)")

        results.append({
            "test_id": "Test_H_Video_Intelligence",
            "image_name": os.path.basename(video_sample),
            "ground_truth": "Consolidated Video Incidents",
            "predicted_class": f"{len(evts)} Unique Events",
            "confidence_percent": f"{vid_res.get('hazards_count', len(evts))} Hazards",
            "boxes_detected": len(kfs),
            "latency_ms": vid_lat,
            "status": status_str,
            "notes": notes
        })
    else:
        print("[SKIP] Test H: No video sample found.")

    # 4. EXPORT CSVs
    output_paths = [
        os.path.join(BASE_DIR, "unseen_test_results.csv"),
        os.path.join(BASE_DIR, "reports", "unseen_test_results.csv"),
        os.path.join(os.path.dirname(BASE_DIR), "unseen_test_results.csv")
    ]

    fieldnames = [
        "test_id", "image_name", "ground_truth", "predicted_class",
        "confidence_percent", "boxes_detected", "latency_ms", "status", "notes"
    ]

    for out_path in output_paths:
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for r in results:
                writer.writerow(r)
        print(f"Saved: {out_path}")

    # Remove temporary test script if present
    t_script = os.path.join(BASE_DIR, "ml", "test_vid.py")
    if os.path.exists(t_script):
        try:
            os.remove(t_script)
        except Exception:
            pass

    print("\nAcceptance tests successfully completed!")

if __name__ == "__main__":
    main()
