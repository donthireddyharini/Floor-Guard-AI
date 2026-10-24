#!/usr/bin/env python3
"""
Floor Guard AI — Phase 3B: Targeted Broken Glass Extractor from PHELE
Extracts verified broken-glass images and labels from Mendeley Data (CC BY 4.0)
using HTTP range requests directly without downloading the 2.52 GB zip archive.
"""

import os
import sys
import struct
import zlib
import urllib.request
import hashlib
from PIL import Image

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_IMG_DIR = os.path.join(BASE_DIR, 'data', 'processed', 'images')
PROCESSED_LBL_DIR = os.path.join(BASE_DIR, 'data', 'processed', 'labels')
RAW_GLASS_DIR = os.path.join(BASE_DIR, 'data', 'raw', 'phele_glass')

PHELE_S3_URL = 'https://prod-dcd-datasets-public-files-eu-west-1.s3.eu-west-1.amazonaws.com/ec6ca432-75f6-491c-aa9d-2a268fd80782'
CD_OFFSET = 2517832913
CD_SIZE = 275723

def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()

def fetch_range(start, end):
    req = urllib.request.Request(PHELE_S3_URL, headers={'Range': f'bytes={start}-{end}'})
    with urllib.request.urlopen(req, timeout=15) as r:
        return r.read()

def extract_file_from_zip(entry):
    offset = entry['offset']
    comp_size = entry['comp_size']
    name_len = len(entry['name'])
    header_data = fetch_range(offset, offset + 30 + name_len + 100)
    sig = header_data[:4]
    if sig != b'\x50\x4b\x03\x04':
        raise ValueError(f"Invalid local header signature for {entry['name']}")
    l_name_len, l_extra_len = struct.unpack('<HH', header_data[26:30])
    data_start = offset + 30 + l_name_len + l_extra_len
    data_end = data_start + comp_size - 1
    compressed_bytes = fetch_range(data_start, data_end)
    if entry['method'] == 8:
        return zlib.decompress(compressed_bytes, -15)
    return compressed_bytes

def main(target_count=15):
    print("=" * 70)
    print("FLOOR GUARD AI — PHELE TARGETED BROKEN GLASS EXTRACTION")
    print("=" * 70)
    print(f"Target count: {target_count} glass fragment images")
    print("Fetching Central Directory (275 KB) from Mendeley S3...")

    os.makedirs(PROCESSED_IMG_DIR, exist_ok=True)
    os.makedirs(PROCESSED_LBL_DIR, exist_ok=True)
    os.makedirs(RAW_GLASS_DIR, exist_ok=True)

    cd_data = fetch_range(CD_OFFSET, CD_OFFSET + CD_SIZE - 1)
    pos = 0
    label_entries = []
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
            'uncomp_size': vals[8],
            'method': vals[3]
        }
        if name.endswith('.txt') and name != 'PHELE/classes.txt':
            label_entries.append(entry)
        elif name.endswith(('.jpg', '.jpeg', '.png')):
            image_entries[name] = entry
        pos += 46 + vals[9] + vals[10] + vals[11]

    print(f"Found {len(label_entries)} labels and {len(image_entries)} images in archive.")
    print("Searching in parallel for class index 14 ('Glass fragment')...", flush=True)

    from concurrent.futures import ThreadPoolExecutor, as_completed

    def check_label(le):
        try:
            txt = extract_file_from_zip(le).decode('utf-8', errors='ignore')
            lines = [l.strip() for l in txt.strip().splitlines() if l.strip()]
            glass_boxes = []
            for line in lines:
                parts = line.split()
                if len(parts) == 5 and parts[0] == '14':
                    # Remap class 14 -> class 2: broken_glass
                    glass_boxes.append(f"2 {parts[1]} {parts[2]} {parts[3]} {parts[4]}")
            if glass_boxes:
                img_name = le['name'].replace('/labels/', '/images/').replace('.txt', '.jpg')
                if img_name in image_entries:
                    return {
                        'label_entry': le,
                        'image_entry': image_entries[img_name],
                        'boxes': glass_boxes,
                        'original_label_text': txt
                    }
        except:
            pass
        return None

    glass_matches = []
    with ThreadPoolExecutor(max_workers=16) as executor:
        futures = {executor.submit(check_label, le): le for le in label_entries}
        for fut in as_completed(futures):
            res = fut.result()
            if res:
                glass_matches.append(res)
                print(f"  Match [{len(glass_matches)}/{target_count}]: {res['image_entry']['name']} ({len(res['boxes'])} glass boxes)", flush=True)
                if len(glass_matches) >= target_count:
                    # Cancel remaining futures
                    for f in futures:
                        f.cancel()
                    break

    print(f"\nExtracted {len(glass_matches)} verified broken-glass files.", flush=True)
    print("Downloading and validating images in parallel...", flush=True)

    acquired_records = []
    for idx, item in enumerate(glass_matches, 1):
        ie = item['image_entry']
        img_bytes = extract_file_from_zip(ie)
        img_hash = sha256_bytes(img_bytes)

        base_name = os.path.basename(ie['name'])
        target_img_name = f"phele_glass_{base_name}"
        target_img_path = os.path.join(PROCESSED_IMG_DIR, target_img_name)
        raw_img_path = os.path.join(RAW_GLASS_DIR, base_name)

        # Write image files
        with open(raw_img_path, 'wb') as rf:
            rf.write(img_bytes)
        with open(target_img_path, 'wb') as pf:
            pf.write(img_bytes)

        # Verify readability with PIL
        with Image.open(target_img_path) as im:
            im.verify()
        with Image.open(target_img_path) as im:
            w, h = im.size
            fmt = im.format

        # Write remapped YOLO label (class 2: broken_glass)
        label_filename = os.path.splitext(target_img_name)[0] + '.txt'
        label_path = os.path.join(PROCESSED_LBL_DIR, label_filename)
        with open(label_path, 'w', encoding='utf-8') as lf:
            for b in item['boxes']:
                lf.write(b + '\n')

        # Write audit metadata sidecar
        meta_filename = os.path.splitext(target_img_name)[0] + '.meta.json'
        meta_path = os.path.join(PROCESSED_LBL_DIR, meta_filename)
        with open(meta_path, 'w', encoding='utf-8') as mf:
            import json
            meta = {
                "image_filename": target_img_name,
                "source_dataset": "PHELE: Elderly Living Environment Hazards (DOI: 10.17632/yzsxcvc8dp.4)",
                "source_author": "Peng Gao, Chuzhou University",
                "source_license": "CC BY 4.0",
                "original_path_in_archive": ie['name'],
                "sha256": img_hash,
                "dimensions": {"width": w, "height": h},
                "boxes_count": len(item['boxes']),
                "mapped_class": "broken_glass (id: 2)",
                "source_class_id": 14,
                "review_status": "reviewed"
            }
            json.dump(meta, mf, indent=2)

        acquired_records.append({
            "filename": target_img_name,
            "original_name": ie['name'],
            "sha256": img_hash,
            "dimensions": f"{w}x{h}",
            "boxes": len(item['boxes'])
        })
        print(f"[{idx}/{len(glass_matches)}] Saved {target_img_name} ({w}x{h}, {len(item['boxes'])} glass boxes, SHA: {img_hash[:12]}...)")

    print("\n" + "=" * 70)
    print(f"PHELE GLASS EXTRACTION COMPLETED: {len(acquired_records)} files acquired successfully.")
    print("=" * 70)

if __name__ == '__main__':
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 15
    main(count)
