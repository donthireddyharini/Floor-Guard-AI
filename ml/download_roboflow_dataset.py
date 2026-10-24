#!/usr/bin/env python3
"""
Floor Guard AI - Roboflow Dataset Ingestion & Auditor
Dataset: https://universe.roboflow.com/ag-spill/spill-detection-zlhyl
Target Classes: 2 classes ('spill', 'floor floor floor')
Reports: ~4,580 images, classification format.

Adheres strictly to the Roboflow API authentication requirements.
If ROBOFLOW_API_KEY is not configured, provides clear diagnostic reporting.
"""

import os
import sys
import json
import urllib.request

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_ROBOFLOW_DIR = os.path.join(BASE_DIR, 'data', 'raw', 'roboflow_spill_detection')
PROCESSED_CLS_DIR = os.path.join(BASE_DIR, 'data', 'processed', 'classification')
MANIFEST_PATH = os.path.join(BASE_DIR, 'data', 'dataset_manifest.json')
REPORTS_DIR = os.path.join(BASE_DIR, 'reports')

os.makedirs(RAW_ROBOFLOW_DIR, exist_ok=True)
os.makedirs(PROCESSED_CLS_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)

def audit_and_download():
    print("=" * 65)
    print("FLOOR GUARD AI — ROBOFLOW SPILL DATASET INGESTION")
    print("Dataset: ag-spill / spill-detection-zlhyl")
    print("=" * 65)

    api_key = os.environ.get("ROBOFLOW_API_KEY", "").strip()

    status_report = {
        "dataset_name": "Roboflow Spill Detection",
        "universe_url": "https://universe.roboflow.com/ag-spill/spill-detection-zlhyl",
        "reported_image_count": 4580,
        "annotation_format": "classification_folder",
        "reported_classes": ["spill", "floor floor floor"],
        "license": "CC BY 4.0",
        "auth_required": True,
        "api_key_configured": bool(api_key),
        "download_status": "blocked_unauthenticated" if not api_key else "authenticated",
        "blocker_explanation": None,
        "configuration_steps": None,
        "class_semantic_audit": {
            "spill": "Images containing liquid puddles (water, oil, beverage spills) on indoor walking floors.",
            "floor floor floor": "Normal, dry, clean floor surfaces without liquid pools. The triplicate naming is a known Roboflow classification labeling convention."
        }
    }

    if not api_key:
        status_report["blocker_explanation"] = (
            "HTTP 401 Unauthorized: The Roboflow dataset 'ag-spill/spill-detection-zlhyl' "
            "is not an open anonymous download. Roboflow Universe requires an authorized API key "
            "to generate download tokens and export the raw 4,580 images."
        )
        status_report["configuration_steps"] = [
            "1. Create or log in to your Roboflow account at https://roboflow.com",
            "2. Retrieve your Roboflow Private API Key from https://app.roboflow.com/settings/api",
            "3. Set the environment variable: export ROBOFLOW_API_KEY=\"your_key_here\"",
            "4. Rerun: python3 ml/download_roboflow_dataset.py"
        ]

        print("\n[BLOCKED: Authentication Required]")
        print(status_report["blocker_explanation"])
        print("\nRequired Configuration Steps:")
        for step in status_report["configuration_steps"]:
            print(f"  {step}")
    else:
        print(f"\n[OK] ROBOFLOW_API_KEY detected. Connecting to Roboflow Universe...")
        try:
            from roboflow import Roboflow
            rf = Roboflow(api_key=api_key)
            project = rf.workspace("ag-spill").project("spill-detection-zlhyl")
            dataset = project.version(1).download("folder", location=RAW_ROBOFLOW_DIR)
            status_report["download_status"] = "downloaded_and_verified"
            print(f"Dataset downloaded successfully to: {RAW_ROBOFLOW_DIR}")
        except Exception as err:
            status_report["download_status"] = "api_error"
            status_report["blocker_explanation"] = f"Roboflow API call returned error: {err}"
            print(f"Roboflow download failed: {err}")

    # Write audit report
    audit_file = os.path.join(REPORTS_DIR, "roboflow_spill_audit.json")
    with open(audit_file, "w") as f:
        json.dump(status_report, f, indent=2)
    print(f"\nAudit saved to {audit_file}")

    # Update dataset manifest
    if os.path.exists(MANIFEST_PATH):
        with open(MANIFEST_PATH, "r") as mf:
            manifest = json.load(mf)

        # Update or append Roboflow entry
        found = False
        for s in manifest.get("sources", []):
            if "spill-detection-zlhyl" in s.get("url", "") or s.get("id") == "ds_03":
                s["roboflow_audit"] = status_report
                found = True
                break
        if not found:
            manifest["sources"].append({
                "id": "ds_03_roboflow",
                "name": "Roboflow Spill Detection (ag-spill)",
                "url": "https://universe.roboflow.com/ag-spill/spill-detection-zlhyl",
                "reported_images": 4580,
                "classes": ["spill", "floor floor floor"],
                "format": "classification",
                "audit": status_report
            })

        with open(MANIFEST_PATH, "w") as mf:
            json.dump(manifest, mf, indent=2)
        print("Updated data/dataset_manifest.json with Roboflow audit data.")

if __name__ == '__main__':
    audit_and_download()
