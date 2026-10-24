#!/usr/bin/env python3
"""
Floor Guard AI — Phase 3A: Pilot Dataset Acquisition & Provenance Tool
Acquires a documented, safe, legally usable pilot batch of floor hazard images.
Target Sources:
  - Hugging Face: Jsohal174/warehouse-safety-hazard-dataset (CC BY 4.0)
Preserves:
  - Source URLs, licenses, SHA-256 hashes, original filenames, dimensions.
  - Never overwrites existing images.
"""

import os
import sys
import json
import hashlib
import argparse
import urllib.request
from PIL import Image

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
RAW_DIR = os.path.join(DATA_DIR, 'raw', 'huggingface_warehouse')
PROCESSED_DIR = os.path.join(DATA_DIR, 'processed', 'images')
PILOT_MANIFEST_PATH = os.path.join(DATA_DIR, 'pilot_manifest.json')

HF_BASE_URL = "https://huggingface.co/datasets/Jsohal174/warehouse-safety-hazard-dataset/resolve/main"

PILOT_ITEMS = [
    # Liquid floor spills (water / oil / chemicals)
    {
        "remote": "test/spill/spill_0013.jpg",
        "raw_name": "spill_0013.jpg",
        "processed_name": "hf_pilot_water_spill_0013.jpg",
        "class": "water_spill",
        "description": "Small clear water puddle with surface reflections on concrete floor",
        "license": "CC BY 4.0",
        "source": "Hugging Face (Jsohal174/warehouse-safety-hazard-dataset)"
    },
    {
        "remote": "test/spill/spill_0014.jpg",
        "raw_name": "spill_0014.jpg",
        "processed_name": "hf_pilot_oil_spill_0014.jpg",
        "class": "oil_spill",
        "description": "Large amber/viscous fluid spill with high contrast on warehouse floor",
        "license": "CC BY 4.0",
        "source": "Hugging Face (Jsohal174/warehouse-safety-hazard-dataset)"
    },
    {
        "remote": "test/spill/spill_0018.jpg",
        "raw_name": "spill_0018.jpg",
        "processed_name": "hf_pilot_water_spill_0018.jpg",
        "class": "water_spill",
        "description": "Clear liquid puddle in walkway with distorted pattern reflection",
        "license": "CC BY 4.0",
        "source": "Hugging Face (Jsohal174/warehouse-safety-hazard-dataset)"
    },
    {
        "remote": "test/spill/spill_0021.jpg",
        "raw_name": "spill_0021.jpg",
        "processed_name": "hf_pilot_water_spill_0021.jpg",
        "class": "water_spill",
        "description": "Liquid spill pool near storage racking corner",
        "license": "CC BY 4.0",
        "source": "Hugging Face (Jsohal174/warehouse-safety-hazard-dataset)"
    },
    {
        "remote": "test/spill/spill_0022.jpg",
        "raw_name": "spill_0022.jpg",
        "processed_name": "hf_pilot_water_spill_0022.jpg",
        "class": "water_spill",
        "description": "Irregular fluid spill with wet periphery on industrial concrete",
        "license": "CC BY 4.0",
        "source": "Hugging Face (Jsohal174/warehouse-safety-hazard-dataset)"
    },
    # Walkway obstacles (pallets, boxes, debris)
    {
        "remote": "test/obstacle/obstacle_0008.jpg",
        "raw_name": "obstacle_0008.jpg",
        "processed_name": "hf_pilot_obstacle_0008.jpg",
        "class": "obstacle",
        "description": "Broken wooden pallet smashed and scattered in walking lane",
        "license": "CC BY 4.0",
        "source": "Hugging Face (Jsohal174/warehouse-safety-hazard-dataset)"
    },
    {
        "remote": "test/obstacle/obstacle_0010.jpg",
        "raw_name": "obstacle_0010.jpg",
        "processed_name": "hf_pilot_obstacle_0010.jpg",
        "class": "obstacle",
        "description": "Broken pallet fragments and wood debris obstructing floor corridor",
        "license": "CC BY 4.0",
        "source": "Hugging Face (Jsohal174/warehouse-safety-hazard-dataset)"
    },
    {
        "remote": "test/obstacle/obstacle_0018.jpg",
        "raw_name": "obstacle_0018.jpg",
        "processed_name": "hf_pilot_obstacle_0018.jpg",
        "class": "obstacle",
        "description": "Loose cardboard boxes and packaging debris on warehouse floor",
        "license": "CC BY 4.0",
        "source": "Hugging Face (Jsohal174/warehouse-safety-hazard-dataset)"
    },
    {
        "remote": "test/obstacle/obstacle_0025.jpg",
        "raw_name": "obstacle_0025.jpg",
        "processed_name": "hf_pilot_obstacle_0025.jpg",
        "class": "obstacle",
        "description": "Dropped equipment container obstructing pedestrian walkway",
        "license": "CC BY 4.0",
        "source": "Hugging Face (Jsohal174/warehouse-safety-hazard-dataset)"
    },
    # Clean dry floors (Negative background samples)
    {
        "remote": "test/safe/forklift_0017.jpg",
        "raw_name": "forklift_0017.jpg",
        "processed_name": "hf_pilot_clean_floor_0017.jpg",
        "class": "clean_floor",
        "description": "Clean dry warehouse floor with unobstructed center aisle",
        "license": "CC BY 4.0",
        "source": "Hugging Face (Jsohal174/warehouse-safety-hazard-dataset)"
    },
    {
        "remote": "test/safe/forklift_0024.jpg",
        "raw_name": "forklift_0024.jpg",
        "processed_name": "hf_pilot_clean_floor_0024.jpg",
        "class": "clean_floor",
        "description": "Clean concrete floor aisle between tall racking, free of spills",
        "license": "CC BY 4.0",
        "source": "Hugging Face (Jsohal174/warehouse-safety-hazard-dataset)"
    },
    {
        "remote": "test/safe/forklift_0026.jpg",
        "raw_name": "forklift_0026.jpg",
        "processed_name": "hf_pilot_clean_floor_0026.jpg",
        "class": "clean_floor",
        "description": "Dry industrial walkway with clear floor markings",
        "license": "CC BY 4.0",
        "source": "Hugging Face (Jsohal174/warehouse-safety-hazard-dataset)"
    },
    {
        "remote": "test/safe/forklift_0072.jpg",
        "raw_name": "forklift_0072.jpg",
        "processed_name": "hf_pilot_clean_floor_0072.jpg",
        "class": "clean_floor",
        "description": "Unobstructed dry concrete floor corridor",
        "license": "CC BY 4.0",
        "source": "Hugging Face (Jsohal174/warehouse-safety-hazard-dataset)"
    }
]

def sha256_file(filepath):
    h = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def acquire_pilot(dry_run=False):
    print("=" * 70)
    print("FLOOR GUARD AI — PHASE 3A PILOT DATASET ACQUISITION")
    print("=" * 70)
    print(f"Mode: {'DRY RUN (Plan Inspection Only)' if dry_run else 'ACTIVE PILOT ACQUISITION'}")
    print(f"Target count: {len(PILOT_ITEMS)} pilot images across classes")
    print(f"Destination: {PROCESSED_DIR}")
    print("-" * 70)

    os.makedirs(RAW_DIR, exist_ok=True)
    os.makedirs(PROCESSED_DIR, exist_ok=True)

    records = []
    skipped = 0
    acquired = 0

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) FloorGuardAI/3.0'}

    for idx, item in enumerate(PILOT_ITEMS, 1):
        url = f"{HF_BASE_URL}/{item['remote']}"
        raw_path = os.path.join(RAW_DIR, item['raw_name'])
        processed_path = os.path.join(PROCESSED_DIR, item['processed_name'])

        print(f"\n[{idx}/{len(PILOT_ITEMS)}] {item['processed_name']}")
        print(f"  Class: {item['class']} | Source: {item['remote']}")
        print(f"  Description: {item['description']}")

        if os.path.exists(processed_path):
            print(f"  [EXISTS] File already present at {processed_path}. Skipping download to prevent overwrite.")
            skipped += 1
            digest = sha256_file(processed_path)
            with Image.open(processed_path) as im:
                width, height = im.size
                fmt = im.format
            size_b = os.path.getsize(processed_path)
        elif dry_run:
            print(f"  [DRY RUN] Would fetch: {url}")
            digest = "DRY_RUN_PENDING"
            width, height = 1024, 768
            fmt = "JPEG"
            size_b = 0
        else:
            print(f"  [DOWNLOADING] Connecting to Hugging Face...")
            req = urllib.request.Request(url, headers=headers)
            try:
                with urllib.request.urlopen(req, timeout=15) as resp:
                    data = resp.read()
                # Save raw
                with open(raw_path, 'wb') as rf:
                    rf.write(data)
                # Save processed
                with open(processed_path, 'wb') as pf:
                    pf.write(data)

                # Verify image integrity
                with Image.open(processed_path) as im:
                    im.verify()
                with Image.open(processed_path) as im:
                    width, height = im.size
                    fmt = im.format

                digest = sha256_file(processed_path)
                size_b = os.path.getsize(processed_path)
                acquired += 1
                print(f"  [OK] Successfully saved ({size_b} bytes, {width}x{height} {fmt}, SHA: {digest[:12]}...)")
            except Exception as e:
                print(f"  [ERROR] Download failed: {e}")
                continue

        records.append({
            "filename": item['processed_name'],
            "raw_filename": item['raw_name'],
            "remote_path": item['remote'],
            "url": url,
            "target_class": item['class'],
            "description": item['description'],
            "license": item['license'],
            "source": item['source'],
            "sha256": digest,
            "size_bytes": size_b,
            "dimensions": {"width": width, "height": height},
            "format": fmt
        })

    # Save pilot manifest
    if not dry_run:
        manifest = {
            "version": "1.0-pilot",
            "timestamp": "2026-10-24T15:00:00Z",
            "source_repo": "Jsohal174/warehouse-safety-hazard-dataset",
            "license": "CC BY 4.0",
            "total_items": len(records),
            "acquired_new": acquired,
            "already_present": skipped,
            "class_distribution": {},
            "items": records
        }
        for r in records:
            cls = r['target_class']
            manifest['class_distribution'][cls] = manifest['class_distribution'].get(cls, 0) + 1

        with open(PILOT_MANIFEST_PATH, 'w') as mf:
            json.dump(manifest, mf, indent=2)
        print("\n" + "=" * 70)
        print(f"PILOT ACQUISITION COMPLETE: {acquired} new, {skipped} existing.")
        print(f"Manifest written to: {PILOT_MANIFEST_PATH}")
        print("Class breakdown in pilot:")
        for cls, count in manifest['class_distribution'].items():
            print(f"  - {cls}: {count} images")
        print("=" * 70)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Floor Guard AI Pilot Dataset Acquisition")
    parser.add_argument('--dry-run', action='store_true', help="Preview acquisition without downloading")
    args = parser.parse_args()
    acquire_pilot(dry_run=args.dry_run)
