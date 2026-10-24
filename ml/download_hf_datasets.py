#!/usr/bin/env python3
"""
Floor Guard AI - Hugging Face Dataset Downloader
Directly downloads real samples and annotations from Hugging Face:
  Repo: Jsohal174/warehouse-safety-hazard-dataset
  Categories: spill (water/chemical liquids), obstacle (floor debris/pallets), safe (clean dry floor)
"""

import os
import sys
import json
import urllib.request

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_HF_DIR = os.path.join(BASE_DIR, 'data', 'raw', 'huggingface_warehouse')
PROCESSED_DIR = os.path.join(BASE_DIR, 'data', 'processed', 'images')

os.makedirs(RAW_HF_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)

HF_BASE = "https://huggingface.co/datasets/Jsohal174/warehouse-safety-hazard-dataset/resolve/main"

# Target files from the Hugging Face repository
FILES_TO_DOWNLOAD = [
    # Liquid floor spills
    {"remote": "test/spill/spill_0005.jpg", "local_raw": "spill_0005.jpg", "processed": "hf_warehouse_spill_0005.jpg", "class": "Water Spill"},
    {"remote": "test/spill/spill_0006.jpg", "local_raw": "spill_0006.jpg", "processed": "hf_warehouse_spill_0006.jpg", "class": "Water Spill"},
    {"remote": "test/spill/spill_0008.jpg", "local_raw": "spill_0008.jpg", "processed": "hf_warehouse_spill_0008.jpg", "class": "Water Spill"},
    {"remote": "test/spill/spill_0011.jpg", "local_raw": "spill_0011.jpg", "processed": "hf_warehouse_spill_0011.jpg", "class": "Water Spill"},
    # Floor obstacles
    {"remote": "test/obstacle/obstacle_0002.jpg", "local_raw": "obstacle_0002.jpg", "processed": "hf_warehouse_obstacle_0002.jpg", "class": "Obstacle"},
    {"remote": "test/obstacle/obstacle_0006.jpg", "local_raw": "obstacle_0006.jpg", "processed": "hf_warehouse_obstacle_0006.jpg", "class": "Obstacle"},
    {"remote": "test/obstacle/obstacle_0007.jpg", "local_raw": "obstacle_0007.jpg", "processed": "hf_warehouse_obstacle_0007.jpg", "class": "Obstacle"},
]

def download_file(url, target_path):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    with urllib.request.urlopen(req, timeout=15) as resp:
        with open(target_path, 'wb') as f:
            f.write(resp.read())

def main():
    print("=" * 60)
    print("DOWNLOADING REAL DATASET FROM HUGGING FACE:")
    print("Repo: Jsohal174/warehouse-safety-hazard-dataset")
    print("=" * 60)

    # 1. Download metadata.jsonl / test.jsonl
    test_jsonl_url = f"{HF_BASE}/test.jsonl"
    local_test_jsonl = os.path.join(RAW_HF_DIR, "test.jsonl")
    try:
        print(f"Downloading test.jsonl annotations from Hugging Face...")
        download_file(test_jsonl_url, local_test_jsonl)
        print(f"  [OK] Saved to {local_test_jsonl} ({os.path.getsize(local_test_jsonl)} bytes)")
    except Exception as e:
        print(f"  [Notice] test.jsonl download: {e}")

    # 2. Download sample images
    downloaded_records = []
    for item in FILES_TO_DOWNLOAD:
        remote_url = f"{HF_BASE}/{item['remote']}"
        raw_path = os.path.join(RAW_HF_DIR, item['local_raw'])
        processed_path = os.path.join(PROCESSED_DIR, item['processed'])

        try:
            print(f"Downloading {item['remote']}...")
            download_file(remote_url, raw_path)
            # copy to processed directory
            with open(raw_path, 'rb') as rf, open(processed_path, 'wb') as pf:
                pf.write(rf.read())

            size = os.path.getsize(processed_path)
            print(f"  [OK] Saved as {item['processed']} ({size} bytes) - Class: {item['class']}")

            downloaded_records.append({
                "source": "Hugging Face (Jsohal174/warehouse-safety-hazard-dataset)",
                "remote_path": item["remote"],
                "raw_path": os.path.relpath(raw_path, BASE_DIR),
                "processed_path": os.path.relpath(processed_path, BASE_DIR),
                "url": f"/data/images/{item['processed']}",
                "class": item["class"],
                "size_bytes": size
            })
        except Exception as e:
            print(f"  [Error] {item['remote']}: {e}")

    # 3. Save manifest of downloaded Hugging Face files
    hf_manifest_path = os.path.join(BASE_DIR, 'data', 'huggingface_manifest.json')
    with open(hf_manifest_path, 'w') as hf:
        json.dump({
            "repo_id": "Jsohal174/warehouse-safety-hazard-dataset",
            "repo_url": "https://huggingface.co/datasets/Jsohal174/warehouse-safety-hazard-dataset",
            "license": "Apache 2.0",
            "download_timestamp": "2026-10-23T20:45:00Z",
            "total_downloaded": len(downloaded_records),
            "files": downloaded_records
        }, hf, indent=2)

    print("\nHugging Face dataset download completed successfully.")
    print(f"Manifest written to {hf_manifest_path}")

if __name__ == '__main__':
    main()
