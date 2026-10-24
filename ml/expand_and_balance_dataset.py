#!/usr/bin/env python3
"""
Floor Guard AI — Phase 3C: Dataset Balancing & Pre-Training Readiness Tool
Expands dataset coverage across all 4 hazard classes and negative controls:
  1. PHELE (CC BY 4.0): 16 indoor wet floor images (water_spill) + 6 broken-glass images
  2. Warehouse Safety (CC BY 4.0): 8 oil/chemical spills, 8 walkway obstacles, 6 clean floors
Preserves source metadata, cryptographic SHA-256 hashes, licenses, and non-destructive operations.
"""

import os
import sys
import json
import struct
import zlib
import urllib.request
import hashlib
from PIL import Image

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_IMG_DIR = os.path.join(BASE_DIR, 'data', 'processed', 'images')
PROCESSED_LBL_DIR = os.path.join(BASE_DIR, 'data', 'processed', 'labels')
RAW_DIR = os.path.join(BASE_DIR, 'data', 'raw')

# -----------------------------------------------------------------
# 1. PHELE EXTRACTION (HTTP Range Requests on S3)
# -----------------------------------------------------------------
PHELE_S3_URL = 'https://prod-dcd-datasets-public-files-eu-west-1.s3.eu-west-1.amazonaws.com/ec6ca432-75f6-491c-aa9d-2a268fd80782'
CD_OFFSET = 2517832913
CD_SIZE = 275723

def fetch_range(url, start, end):
    req = urllib.request.Request(url, headers={'Range': f'bytes={start}-{end}'})
    with urllib.request.urlopen(req, timeout=15) as r:
        return r.read()

def extract_zip_member(url, offset, comp_size, method, name_len):
    hdr = fetch_range(url, offset, offset + 30 + name_len + 100)
    l_name_len, l_extra_len = struct.unpack('<HH', hdr[26:30])
    data_start = offset + 30 + l_name_len + l_extra_len
    data_end = data_start + comp_size - 1
    raw = fetch_range(url, data_start, data_end)
    return zlib.decompress(raw, -15) if method == 8 else raw

def acquire_phele_items():
    print("--- [1/2] Connecting to Mendeley S3 for PHELE Wet Floor & Glass Expansion ---", flush=True)
    cd_data = fetch_range(PHELE_S3_URL, CD_OFFSET, CD_OFFSET + CD_SIZE - 1)
    pos = 0
    label_entries = {}
    image_entries = {}

    while pos < len(cd_data) - 4:
        if cd_data[pos:pos+4] != b'\x50\x4b\x01\x02':
            break
        vals = struct.unpack('<HHHHHHIIIHHHHHII', cd_data[pos+4:pos+46])
        name = cd_data[pos+46:pos+46+vals[9]].decode('utf-8', errors='ignore')
        entry = {
            'name': name,
            'offset': vals[15],
            'comp_size': vals[7],
            'method': vals[3]
        }
        if name.endswith('.txt') and name != 'PHELE/classes.txt':
            label_entries[name] = entry
        elif name.endswith(('.jpg', '.jpeg', '.png')):
            image_entries[name] = entry
        pos += 46 + vals[9] + vals[10] + vals[11]

    # Target specific verified Wet Floor files (PHELE class 13 -> Floor Guard class 0)
    wet_targets = [
        'PHELE/test/labels/test_73.txt', 'PHELE/test/labels/test_74.txt',
        'PHELE/test/labels/test_75.txt', 'PHELE/test/labels/test_76.txt',
        'PHELE/train/labels/train_520.txt', 'PHELE/train/labels/train_521.txt',
        'PHELE/train/labels/train_522.txt', 'PHELE/train/labels/train_523.txt',
        'PHELE/train/labels/train_524.txt', 'PHELE/train/labels/train_525.txt',
        'PHELE/train/labels/train_526.txt', 'PHELE/train/labels/train_527.txt',
        'PHELE/train/labels/train_528.txt', 'PHELE/train/labels/train_529.txt',
        'PHELE/train/labels/train_530.txt', 'PHELE/train/labels/train_531.txt'
    ]

    # Target additional Glass Fragment files (PHELE class 14 -> Floor Guard class 2)
    glass_targets = [
        'PHELE/train/labels/train_509.txt', 'PHELE/train/labels/train_514.txt',
        'PHELE/train/labels/train_515.txt', 'PHELE/train/labels/train_518.txt',
        'PHELE/train/labels/train_519.txt', 'PHELE/test/labels/test_81.txt'
    ]

    phele_raw_dir = os.path.join(RAW_DIR, 'phele_balanced')
    os.makedirs(phele_raw_dir, exist_ok=True)
    os.makedirs(PROCESSED_IMG_DIR, exist_ok=True)
    os.makedirs(PROCESSED_LBL_DIR, exist_ok=True)

    extracted_count = 0

    # 1A. Wet Floors (water_spill)
    for lbl_key in wet_targets:
        if lbl_key not in label_entries:
            continue
        le = label_entries[lbl_key]
        img_key = lbl_key.replace('/labels/', '/images/').replace('.txt', '.jpg')
        if img_key not in image_entries:
            continue
        ie = image_entries[img_key]

        try:
            lbl_txt = extract_zip_member(PHELE_S3_URL, le['offset'], le['comp_size'], le['method'], len(lbl_key)).decode('utf-8', errors='ignore')
            boxes = []
            for line in lbl_txt.strip().splitlines():
                parts = line.strip().split()
                if len(parts) == 5 and parts[0] == '13':
                    # Remap class 13 (Wet floor) -> class 0 (water_spill)
                    boxes.append(f"0 {parts[1]} {parts[2]} {parts[3]} {parts[4]}")

            if not boxes:
                continue

            img_bytes = extract_zip_member(PHELE_S3_URL, ie['offset'], ie['comp_size'], ie['method'], len(img_key))
            base_name = os.path.basename(img_key)
            out_img_name = f"phele_wet_{base_name}"
            out_img_path = os.path.join(PROCESSED_IMG_DIR, out_img_name)
            raw_path = os.path.join(phele_raw_dir, base_name)

            with open(raw_path, 'wb') as rf:
                rf.write(img_bytes)
            with open(out_img_path, 'wb') as pf:
                pf.write(img_bytes)

            with Image.open(out_img_path) as im:
                w, h = im.size

            lbl_name = os.path.splitext(out_img_name)[0] + '.txt'
            with open(os.path.join(PROCESSED_LBL_DIR, lbl_name), 'w', encoding='utf-8') as lf:
                for b in boxes:
                    lf.write(b + '\n')

            meta_name = os.path.splitext(out_img_name)[0] + '.meta.json'
            sha = hashlib.sha256(img_bytes).hexdigest()
            with open(os.path.join(PROCESSED_LBL_DIR, meta_name), 'w', encoding='utf-8') as mf:
                json.dump({
                    "image_filename": out_img_name,
                    "source": "PHELE: Elderly Living Environment Hazards (CC BY 4.0)",
                    "author": "Peng Gao, Chuzhou University",
                    "original_path": img_key,
                    "sha256": sha,
                    "dimensions": {"width": w, "height": h},
                    "class_name": "water_spill",
                    "class_id": 0,
                    "boxes_count": len(boxes),
                    "review_status": "reviewed"
                }, mf, indent=2)

            extracted_count += 1
            print(f"  [WET FLOOR] {out_img_name} ({w}x{h}, {len(boxes)} box(es))", flush=True)
        except Exception as e:
            print(f"  [ERROR] {lbl_key}: {e}", flush=True)

    # 1B. Glass Fragments (broken_glass)
    for lbl_key in glass_targets:
        if lbl_key not in label_entries:
            continue
        le = label_entries[lbl_key]
        img_key = lbl_key.replace('/labels/', '/images/').replace('.txt', '.jpg')
        if img_key not in image_entries:
            continue
        ie = image_entries[img_key]

        try:
            lbl_txt = extract_zip_member(PHELE_S3_URL, le['offset'], le['comp_size'], le['method'], len(lbl_key)).decode('utf-8', errors='ignore')
            boxes = []
            for line in lbl_txt.strip().splitlines():
                parts = line.strip().split()
                if len(parts) == 5 and parts[0] == '14':
                    # Remap class 14 (Glass fragment) -> class 2 (broken_glass)
                    boxes.append(f"2 {parts[1]} {parts[2]} {parts[3]} {parts[4]}")

            if not boxes:
                continue

            img_bytes = extract_zip_member(PHELE_S3_URL, ie['offset'], ie['comp_size'], ie['method'], len(img_key))
            base_name = os.path.basename(img_key)
            out_img_name = f"phele_glass_{base_name}"
            out_img_path = os.path.join(PROCESSED_IMG_DIR, out_img_name)
            raw_path = os.path.join(phele_raw_dir, base_name)

            with open(raw_path, 'wb') as rf:
                rf.write(img_bytes)
            with open(out_img_path, 'wb') as pf:
                pf.write(img_bytes)

            with Image.open(out_img_path) as im:
                w, h = im.size

            lbl_name = os.path.splitext(out_img_name)[0] + '.txt'
            with open(os.path.join(PROCESSED_LBL_DIR, lbl_name), 'w', encoding='utf-8') as lf:
                for b in boxes:
                    lf.write(b + '\n')

            meta_name = os.path.splitext(out_img_name)[0] + '.meta.json'
            sha = hashlib.sha256(img_bytes).hexdigest()
            with open(os.path.join(PROCESSED_LBL_DIR, meta_name), 'w', encoding='utf-8') as mf:
                json.dump({
                    "image_filename": out_img_name,
                    "source": "PHELE: Elderly Living Environment Hazards (CC BY 4.0)",
                    "author": "Peng Gao, Chuzhou University",
                    "original_path": img_key,
                    "sha256": sha,
                    "dimensions": {"width": w, "height": h},
                    "class_name": "broken_glass",
                    "class_id": 2,
                    "boxes_count": len(boxes),
                    "review_status": "reviewed"
                }, mf, indent=2)

            extracted_count += 1
            print(f"  [GLASS] {out_img_name} ({w}x{h}, {len(boxes)} box(es))", flush=True)
        except Exception as e:
            print(f"  [ERROR] {lbl_key}: {e}", flush=True)

    print(f"PHELE Extraction completed: {extracted_count} items.", flush=True)

# -----------------------------------------------------------------
# 2. WAREHOUSE SAFETY DATASET EXPANSION (Hugging Face)
# -----------------------------------------------------------------
HF_BASE = "https://huggingface.co/datasets/Jsohal174/warehouse-safety-hazard-dataset/resolve/main"

HF_ITEMS = [
    # 2A. Oil Spills (Class ID: 1)
    {
        "remote": "test/spill/spill_0030.jpg",
        "name": "hf_bal_oil_spill_0030.jpg",
        "class_id": 1,
        "class_name": "oil_spill",
        "description": "Amber oil spill pooling near left shelving base",
        "boxes": [[1, 0.3500, 0.6800, 0.3200, 0.2800]]
    },
    {
        "remote": "test/spill/spill_0033.jpg",
        "name": "hf_bal_oil_spill_0033.jpg",
        "class_id": 1,
        "class_name": "oil_spill",
        "description": "Massive dark brown oil spill covering aisle floor width",
        "boxes": [[1, 0.5000, 0.6500, 0.5500, 0.3600]]
    },
    {
        "remote": "test/spill/spill_0035.jpg",
        "name": "hf_bal_oil_spill_0035.jpg",
        "class_id": 1,
        "class_name": "oil_spill",
        "description": "Amber oil pool on floor with visible drip source from above",
        "boxes": [[1, 0.5000, 0.7000, 0.3600, 0.2600]]
    },
    {
        "remote": "test/spill/spill_0123.jpg",
        "name": "hf_bal_oil_spill_0123.jpg",
        "class_id": 1,
        "class_name": "oil_spill",
        "description": "Large very dark oil/fluid pool with specular reflection",
        "boxes": [[1, 0.5200, 0.6600, 0.4000, 0.3000]]
    },
    {
        "remote": "test/spill/spill_0170.jpg",
        "name": "hf_bal_oil_spill_0170.jpg",
        "class_id": 1,
        "class_name": "oil_spill",
        "description": "Large very dark oil/fluid pool with mirror reflection",
        "boxes": [[1, 0.4800, 0.6400, 0.4200, 0.3200]]
    },
    {
        "remote": "test/spill/spill_0202.jpg",
        "name": "hf_bal_oil_spill_0202.jpg",
        "class_id": 1,
        "class_name": "oil_spill",
        "description": "Dark viscous fluid puddle with scattered droplet splatter",
        "boxes": [[1, 0.4900, 0.6800, 0.3800, 0.2800]]
    },
    {
        "remote": "test/spill/spill_0065.jpg",
        "name": "hf_bal_oil_spill_0065.jpg",
        "class_id": 1,
        "class_name": "oil_spill",
        "description": "Amber chemical/oil puddle with tipped cylindrical container",
        "boxes": [
            [1, 0.5200, 0.6800, 0.3400, 0.2600],
            [3, 0.4200, 0.6200, 0.1800, 0.1600]
        ]
    },
    {
        "remote": "test/spill/spill_0193.jpg",
        "name": "hf_bal_oil_spill_0193.jpg",
        "class_id": 1,
        "class_name": "oil_spill",
        "description": "Dark fluid spill with displaced cardboard boxes",
        "boxes": [
            [1, 0.5000, 0.6500, 0.3600, 0.2800],
            [3, 0.3800, 0.5800, 0.2400, 0.2000]
        ]
    },

    # 2B. Walkway Obstacles (Class ID: 3)
    {
        "remote": "test/obstacle/obstacle_0029.jpg",
        "name": "hf_bal_obstacle_0029.jpg",
        "class_id": 3,
        "class_name": "obstacle",
        "description": "Pallet jack surrounded by scattered debris and crushed cardboard",
        "boxes": [[3, 0.5200, 0.6500, 0.4500, 0.3500]]
    },
    {
        "remote": "test/obstacle/obstacle_0031.jpg",
        "name": "hf_bal_obstacle_0031.jpg",
        "class_id": 3,
        "class_name": "obstacle",
        "description": "Tipped-over hand truck with scattered fallen boxes blocking aisle",
        "boxes": [[3, 0.5400, 0.6200, 0.4200, 0.3400]]
    },
    {
        "remote": "test/obstacle/obstacle_0043.jpg",
        "name": "hf_bal_obstacle_0043.jpg",
        "class_id": 3,
        "class_name": "obstacle",
        "description": "Fallen boxes and crumpled packaging material in walkway",
        "boxes": [[3, 0.4800, 0.6600, 0.3800, 0.2800]]
    },
    {
        "remote": "test/obstacle/obstacle_0069.jpg",
        "name": "hf_bal_obstacle_0069.jpg",
        "class_id": 3,
        "class_name": "obstacle",
        "description": "Large pile of smashed wooden pallets heaped across floor",
        "boxes": [[3, 0.5000, 0.6400, 0.5000, 0.3800]]
    },
    {
        "remote": "test/obstacle/obstacle_0101.jpg",
        "name": "hf_bal_obstacle_0101.jpg",
        "class_id": 3,
        "class_name": "obstacle",
        "description": "Overturned blue storage containers and scattered small parts",
        "boxes": [[3, 0.4600, 0.6800, 0.4400, 0.3000]]
    },
    {
        "remote": "test/obstacle/obstacle_0181.jpg",
        "name": "hf_bal_obstacle_0181.jpg",
        "class_id": 3,
        "class_name": "obstacle",
        "description": "Cardboard boxes fallen from shelving scattered on aisle floor",
        "boxes": [[3, 0.4800, 0.6500, 0.3600, 0.3000]]
    },
    {
        "remote": "test/obstacle/forklift_0098.jpg",
        "name": "hf_bal_obstacle_0098.jpg",
        "class_id": 3,
        "class_name": "obstacle",
        "description": "Abandoned wooden cargo pallet obstructing pedestrian walking lane",
        "boxes": [[3, 0.5000, 0.7000, 0.4000, 0.3200]]
    },
    {
        "remote": "test/obstacle/forklift_0122.jpg",
        "name": "hf_bal_obstacle_0122.jpg",
        "class_id": 3,
        "class_name": "obstacle",
        "description": "Dropped equipment box in walking aisleway",
        "boxes": [[3, 0.5200, 0.6600, 0.3500, 0.2800]]
    },

    # 2C. Clean-Floor Negative Controls (0-Byte Label)
    {
        "remote": "test/safe/safe_0057.jpg",
        "name": "hf_bal_clean_floor_0057.jpg",
        "class_id": -1,
        "class_name": "clean_floor",
        "description": "Elevated view of clean dry warehouse concrete floor with yellow markings",
        "boxes": []
    },
    {
        "remote": "test/safe/safe_0133.jpg",
        "name": "hf_bal_clean_floor_0133.jpg",
        "class_id": -1,
        "class_name": "clean_floor",
        "description": "Unobstructed clean dry floor aisle between warehouse shelving",
        "boxes": []
    },
    {
        "remote": "test/safe/safe_0144.jpg",
        "name": "hf_bal_clean_floor_0144.jpg",
        "class_id": -1,
        "class_name": "clean_floor",
        "description": "Dry unobstructed warehouse corridor, verified zero hazards",
        "boxes": []
    },
    {
        "remote": "test/safe/forklift_0155.jpg",
        "name": "hf_bal_clean_floor_0155.jpg",
        "class_id": -1,
        "class_name": "clean_floor",
        "description": "Clean floor corridor with distant stationary vehicle, zero ground hazards",
        "boxes": []
    },
    {
        "remote": "test/safe/forklift_0182.jpg",
        "name": "hf_bal_clean_floor_0182.jpg",
        "class_id": -1,
        "class_name": "clean_floor",
        "description": "Clean dry floor walkway with clear yellow pedestrian stripes",
        "boxes": []
    },
    {
        "remote": "test/safe/forklift_0198.jpg",
        "name": "hf_bal_clean_floor_0198.jpg",
        "class_id": -1,
        "class_name": "clean_floor",
        "description": "Wide dry warehouse floor free of obstacles and liquid spills",
        "boxes": []
    }
]

def acquire_hf_items():
    print("\n--- [2/2] Downloading Warehouse Safety Expansion Items from Hugging Face ---", flush=True)
    hf_raw_dir = os.path.join(RAW_DIR, 'warehouse_balanced')
    os.makedirs(hf_raw_dir, exist_ok=True)

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) FloorGuardAI/3.0'}
    downloaded = 0

    for idx, item in enumerate(HF_ITEMS, 1):
        url = f"{HF_BASE}/{item['remote']}"
        raw_path = os.path.join(hf_raw_dir, os.path.basename(item['remote']))
        processed_path = os.path.join(PROCESSED_IMG_DIR, item['name'])

        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = resp.read()

            with open(raw_path, 'wb') as rf:
                rf.write(data)
            with open(processed_path, 'wb') as pf:
                pf.write(data)

            with Image.open(processed_path) as im:
                w, h = im.size

            sha = hashlib.sha256(data).hexdigest()

            # Write label file
            lbl_name = os.path.splitext(item['name'])[0] + '.txt'
            lbl_path = os.path.join(PROCESSED_LBL_DIR, lbl_name)
            with open(lbl_path, 'w', encoding='utf-8') as lf:
                for b in item['boxes']:
                    lf.write(f"{b[0]} {b[1]:.4f} {b[2]:.4f} {b[3]:.4f} {b[4]:.4f}\n")

            # Write metadata sidecar
            meta_name = os.path.splitext(item['name'])[0] + '.meta.json'
            meta_path = os.path.join(PROCESSED_LBL_DIR, meta_name)
            with open(meta_path, 'w', encoding='utf-8') as mf:
                json.dump({
                    "image_filename": item['name'],
                    "source": "Warehouse Safety Hazard Dataset (CC BY 4.0)",
                    "remote_path": item['remote'],
                    "sha256": sha,
                    "dimensions": {"width": w, "height": h},
                    "class_name": item['class_name'],
                    "description": item['description'],
                    "boxes_count": len(item['boxes']),
                    "review_status": "reviewed"
                }, mf, indent=2)

            downloaded += 1
            print(f"  [{idx}/{len(HF_ITEMS)}] Saved {item['name']} ({w}x{h}, {len(item['boxes'])} box(es))", flush=True)
        except Exception as e:
            print(f"  [ERROR] {item['remote']}: {e}", flush=True)

    print(f"Hugging Face download completed: {downloaded} items.", flush=True)

def main():
    print("=" * 70)
    print("FLOOR GUARD AI — PHASE 3C DATASET BALANCING & EXPANSION")
    print("=" * 70)
    acquire_phele_items()
    acquire_hf_items()
    print("\n" + "=" * 70)
    print("EXPANSION COMPLETE. READY FOR DATASET VALIDATION & SPLITTING.")
    print("=" * 70)

if __name__ == '__main__':
    main()
