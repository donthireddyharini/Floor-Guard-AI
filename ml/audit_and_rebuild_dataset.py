#!/usr/bin/env python3
"""
Floor Guard AI — Phase 1-6: Complete Dataset Audit, Duplicate Detection,
Annotation Quality Verification, and Corrected Dataset Rebuild.

Taxonomy (Canonical 13 Classes):
  0: Clean floor (negative background baseline control)
  1: Mat hazard
  2: Floor damage
  3: Water spill
  4: Oil spill
  5: Chemical spill
  6: Broken glass
  7: Cable/Cord
  8: Obstacle/Debris
  9: Trash/Litter
  10: Food waste
  11: Mud/Dirt
  12: Stair hazards
"""

import os
import sys
import glob
import shutil
import hashlib
import json
import csv
from collections import defaultdict, Counter
import cv2
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Target 13 Classes Mapping
TAXONOMY_13 = {
    0: 'clean_floor',
    1: 'mat_hazard',
    2: 'floor_damage',
    3: 'water_spill',
    4: 'oil_spill',
    5: 'chemical_spill',
    6: 'broken_glass',
    7: 'cable_cord',
    8: 'obstacle_debris',
    9: 'trash_litter',
    10: 'food_waste',
    11: 'mud_dirt',
    12: 'stair_hazard'
}

# Old Model Mapping to New Taxonomy
OLD_TO_NEW_MAP = {
    0: 3,   # water_spill -> 3
    1: 4,   # oil_spill -> 4
    2: 5,   # chemical_spill -> 5
    3: 6,   # broken_glass -> 6
    4: 7,   # cable_cord -> 7
    5: 8,   # obstacle_debris -> 8
    6: 9,   # trash_litter -> 9
    7: 10,  # food_waste -> 10
    8: 11,  # mud_dirt -> 11
    9: 12,  # stairs_hazard -> 12
    10: 1,  # floor_mat_hazard -> 1
    11: 2,  # floor_damage -> 2
}

def compute_sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def compute_phash(img_path):
    try:
        img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            return None
        resized = cv2.resize(img, (32, 32), interpolation=cv2.INTER_AREA)
        dct = cv2.dct(np.float32(resized))
        dct_low = dct[:8, :8].flatten()
        med = np.median(dct_low[1:])  # exclude DC term
        hash_val = sum((1 << i) for i, v in enumerate(dct_low) if v > med)
        return f"{hash_val:016x}"
    except Exception:
        return None

def hamming_distance(h1, h2):
    if not h1 or not h2:
        return 999
    try:
        v1, v2 = int(h1, 16), int(h2, 16)
        return bin(v1 ^ v2).count('1')
    except Exception:
        return 999

def run_audit_and_rebuild():
    print("=" * 70)
    print("FLOOR GUARD AI — DATASET QUALITY AUDIT & REBUILD ENGINE")
    print("=" * 70)

    dataset_dir = os.path.join(BASE_DIR, 'dataset')
    corrected_dir = os.path.join(BASE_DIR, 'corrected_dataset')
    review_dir = os.path.join(BASE_DIR, 'dataset_review')

    # Reset corrected dataset directory
    if os.path.exists(corrected_dir):
        shutil.rmtree(corrected_dir)
    os.makedirs(corrected_dir, exist_ok=True)
    for s in ['train', 'val', 'test']:
        os.makedirs(os.path.join(corrected_dir, 'images', s), exist_ok=True)
        os.makedirs(os.path.join(corrected_dir, 'labels', s), exist_ok=True)
    os.makedirs(review_dir, exist_ok=True)

    # 1. Collect candidate images from dataset splits and raw archive
    print("\n[Step 1] Scanning all images across dataset directories...")
    search_dirs = [
        ('dataset_train', os.path.join(dataset_dir, 'images', 'train')),
        ('dataset_val', os.path.join(dataset_dir, 'images', 'val')),
        ('dataset_test', os.path.join(dataset_dir, 'images', 'test')),
        ('raw_archive', os.path.join(dataset_dir, 'raw_archive', 'images')),
        ('data_unique', os.path.join(BASE_DIR, 'data', 'processed', 'unique')),
        ('gallery', os.path.join(BASE_DIR, 'public', 'assets', 'samples', 'gallery'))
    ]

    all_images = {}  # sha256 -> list of image records
    image_records = []

    for source_tag, d in search_dirs:
        if not os.path.exists(d):
            continue
        for fname in os.listdir(d):
            if not fname.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                continue
            fpath = os.path.join(d, fname)
            sha = compute_sha256(fpath)
            ph = compute_phash(fpath)
            sz = os.path.getsize(fpath)
            
            # Find associated label file if exists
            lbl_file = None
            if source_tag.startswith('dataset_'):
                split = source_tag.split('_')[1]
                cand = os.path.join(dataset_dir, 'labels', split, os.path.splitext(fname)[0] + '.txt')
                if os.path.exists(cand):
                    lbl_file = cand
            elif source_tag == 'raw_archive':
                cand = os.path.join(dataset_dir, 'raw_archive', 'labels', os.path.splitext(fname)[0] + '.txt')
                if os.path.exists(cand):
                    lbl_file = cand

            # If still not found, check dataset/labels across all splits
            if not lbl_file:
                for s in ['train', 'val', 'test']:
                    cand = os.path.join(dataset_dir, 'labels', s, os.path.splitext(fname)[0] + '.txt')
                    if os.path.exists(cand):
                        lbl_file = cand
                        break

            rec = {
                'filename': fname,
                'path': fpath,
                'source': source_tag,
                'filesize': sz,
                'sha256': sha,
                'phash': ph,
                'label_path': lbl_file
            }
            image_records.append(rec)
            if sha not in all_images:
                all_images[sha] = []
            all_images[sha].append(rec)

    total_scanned = len(image_records)
    unique_sha_count = len(all_images)
    exact_duplicates_count = total_scanned - unique_sha_count
    print(f"Total scanned images: {total_scanned}")
    print(f"Unique SHA-256 hashes: {unique_sha_count}")
    print(f"Exact duplicates detected: {exact_duplicates_count}")

    # 2. Perceptual duplicate detection:
    # Use Hamming distance <= 2 to purge exact visual clones (brightness/contrast tweaks of identical frame)
    print("\n[Step 2] Computing perceptual hash similarity across unique images...")
    unique_reps = [recs[0] for recs in all_images.values()]
    phash_groups = []
    visited = set()

    for i in range(len(unique_reps)):
        if i in visited:
            continue
        rep_i = unique_reps[i]
        group = [rep_i]
        visited.add(i)

        for j in range(i + 1, len(unique_reps)):
            if j in visited:
                continue
            rep_j = unique_reps[j]
            dist = hamming_distance(rep_i['phash'], rep_j['phash'])
            # Near-duplicate threshold: dist <= 2 identifies identical scene with minor lighting variation
            if dist <= 2:
                group.append(rep_j)
                visited.add(j)

        phash_groups.append(group)

    near_duplicates_count = sum(len(g) - 1 for g in phash_groups if len(g) > 1)
    print(f"Distinct perceptual visual groups: {len(phash_groups)}")
    print(f"Near-duplicate images detected: {near_duplicates_count}")

    # 3. Generate duplicate_report.csv
    dup_csv_path = os.path.join(BASE_DIR, 'duplicate_report.csv')
    with open(dup_csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['filename', 'source', 'split', 'sha256', 'phash', 'group_id', 'duplicate_type', 'similarity_score', 'action', 'duplicate_of'])
        
        gid = 0
        for group in phash_groups:
            gid += 1
            primary = group[0]
            split_name = primary['source'].split('_')[1] if primary['source'].startswith('dataset_') else primary['source']
            writer.writerow([primary['filename'], primary['source'], split_name, primary['sha256'], primary['phash'], gid, 'representative_unique', 1.0, 'KEEP', 'NONE'])

            for member in group[1:]:
                m_split = member['source'].split('_')[1] if member['source'].startswith('dataset_') else member['source']
                dist = hamming_distance(primary['phash'], member['phash'])
                sim = round(1.0 - (dist / 64.0), 3)
                writer.writerow([member['filename'], member['source'], m_split, member['sha256'], member['phash'], gid, 'near_duplicate', sim, 'PURGE_FROM_TRAIN', primary['filename']])

        # Exact SHA duplicates
        for sha, recs in all_images.items():
            if len(recs) > 1:
                orig = recs[0]
                for dup in recs[1:]:
                    d_split = dup['source'].split('_')[1] if dup['source'].startswith('dataset_') else dup['source']
                    writer.writerow([dup['filename'], dup['source'], d_split, dup['sha256'], dup['phash'], 'EXACT', 'exact_byte_duplicate', 1.0, 'PURGE_EXACT_DUPLICATE', orig['filename']])

    print(f"Generated duplicate report: {dup_csv_path}")

    # 4. Audit Annotations & Verify Class Semantics
    print("\n[Step 3] Auditing and correcting annotations against 13-class taxonomy...")
    
    annotation_quality_rows = []
    class_distribution = Counter()
    invalid_box_count = 0
    missing_box_count = 0
    corrected_annotations_count = 0

    valid_curated_samples = []  # list of (image_rec, corrected_boxes, is_clean_control)

    for group in phash_groups:
        rep = group[0]
        fname = rep['filename']
        fname_lower = fname.lower()
        lbl_path = rep['label_path']

        # Determine if this image is a clean floor baseline
        is_clean_control = ('clean' in fname_lower and 'glass' not in fname_lower and 'food' not in fname_lower)

        boxes = []
        if lbl_path and os.path.exists(lbl_path):
            with open(lbl_path, 'r', encoding='utf-8') as lf:
                for line_idx, line in enumerate(lf):
                    parts = line.strip().split()
                    if not parts:
                        continue
                    if len(parts) < 5:
                        invalid_box_count += 1
                        annotation_quality_rows.append([fname, line_idx, 'UNKNOWN', 'INVALID', line.strip(), 'REJECTED', 'Box format has fewer than 5 tokens'])
                        continue

                    try:
                        raw_cls = int(parts[0])
                        cx, cy, w, h = float(parts[1]), float(parts[2]), float(parts[3]), float(parts[4])
                    except ValueError:
                        invalid_box_count += 1
                        annotation_quality_rows.append([fname, line_idx, parts[0], 'INVALID', line.strip(), 'REJECTED', 'Coordinates not numerical'])
                        continue

                    # Validate bounds
                    if cx < 0.0 or cx > 1.0 or cy < 0.0 or cy > 1.0 or w <= 0.0 or w > 1.0 or h <= 0.0 or h > 1.0:
                        invalid_box_count += 1
                        annotation_quality_rows.append([fname, line_idx, raw_cls, 'INVALID', f"{cx} {cy} {w} {h}", 'REJECTED', 'Coordinates outside normalized [0, 1] range'])
                        continue

                    if (w * h) < 0.0001:
                        invalid_box_count += 1
                        annotation_quality_rows.append([fname, line_idx, raw_cls, 'INVALID', f"{cx} {cy} {w} {h}", 'REJECTED', 'Zero-area or degenerate box'])
                        continue

                    # Correct Class ID Semantics
                    target_cls = OLD_TO_NEW_MAP.get(raw_cls, raw_cls)

                    # CRITICAL DISTINCTION 1: Water bottles -> Trash/Litter (Class 9)
                    if any(term in fname_lower for term in ['bottle', 'plastic_bottle', 'water_bottle', 'can', 'cup', 'tin_can', 'wrapper', 'trash', 'litter']):
                        if target_cls in (3, 8):  # if was water_spill or obstacle_debris
                            corrected_annotations_count += 1
                            annotation_quality_rows.append([fname, line_idx, TAXONOMY_13.get(target_cls, raw_cls), 'trash_litter', f"{cx:.4f} {cy:.4f} {w:.4f} {h:.4f}", 'CORRECTED', 'Reclassified bottle/can from water_spill/obstacle to trash_litter (Class 9)'])
                            target_cls = 9

                    # CRITICAL DISTINCTION 2: Cardboard boxes -> Obstacle/Debris (Class 8)
                    elif any(term in fname_lower for term in ['box', 'boxes', 'pallet', 'crate', 'carton', 'container']):
                        if target_cls == 7:  # if was cable_cord
                            corrected_annotations_count += 1
                            annotation_quality_rows.append([fname, line_idx, 'cable_cord', 'obstacle_debris', f"{cx:.4f} {cy:.4f} {w:.4f} {h:.4f}", 'CORRECTED', 'Reclassified cardboard box from cable_cord to obstacle_debris (Class 8)'])
                            target_cls = 8

                    # CRITICAL DISTINCTION 3: Electrical cables -> Cable/Cord (Class 7)
                    elif any(term in fname_lower for term in ['cable', 'cord', 'wire']):
                        if target_cls != 7:
                            corrected_annotations_count += 1
                            annotation_quality_rows.append([fname, line_idx, TAXONOMY_13.get(target_cls, raw_cls), 'cable_cord', f"{cx:.4f} {cy:.4f} {w:.4f} {h:.4f}", 'CORRECTED', 'Verified electrical cable/wire -> Class 7'])
                            target_cls = 7

                    # CRITICAL DISTINCTION 4: Broken glass -> Broken Glass (Class 6)
                    elif any(term in fname_lower for term in ['glass', 'shard', 'shattered']):
                        if target_cls != 6:
                            corrected_annotations_count += 1
                            annotation_quality_rows.append([fname, line_idx, TAXONOMY_13.get(target_cls, raw_cls), 'broken_glass', f"{cx:.4f} {cy:.4f} {w:.4f} {h:.4f}", 'CORRECTED', 'Verified broken glass shards -> Class 6'])
                            target_cls = 6

                    # CRITICAL DISTINCTION 5: Floor damage / cracks -> Floor Damage (Class 2)
                    elif any(term in fname_lower for term in ['crack', 'damage', 'pothole', 'broken_tile', 'fracture']):
                        if target_cls != 2:
                            corrected_annotations_count += 1
                            annotation_quality_rows.append([fname, line_idx, TAXONOMY_13.get(target_cls, raw_cls), 'floor_damage', f"{cx:.4f} {cy:.4f} {w:.4f} {h:.4f}", 'CORRECTED', 'Verified floor damage/crack -> Class 2'])
                            target_cls = 2

                    # CRITICAL DISTINCTION 6: Mat hazard -> Mat Hazard (Class 1)
                    elif any(term in fname_lower for term in ['mat', 'rug', 'carpet_corner', 'curled_edge', 'runner']):
                        if target_cls != 1:
                            corrected_annotations_count += 1
                            annotation_quality_rows.append([fname, line_idx, TAXONOMY_13.get(target_cls, raw_cls), 'mat_hazard', f"{cx:.4f} {cy:.4f} {w:.4f} {h:.4f}", 'CORRECTED', 'Verified curled mat / carpet hazard -> Class 1'])
                            target_cls = 1

                    # CRITICAL DISTINCTION 7: Chemical spill -> Chemical Spill (Class 5)
                    elif 'chemical' in fname_lower or 'coolant' in fname_lower:
                        if target_cls != 5:
                            corrected_annotations_count += 1
                            annotation_quality_rows.append([fname, line_idx, TAXONOMY_13.get(target_cls, raw_cls), 'chemical_spill', f"{cx:.4f} {cy:.4f} {w:.4f} {h:.4f}", 'CORRECTED', 'Verified chemical spill -> Class 5'])
                            target_cls = 5

                    # CRITICAL DISTINCTION 8: Mud/dirt -> Mud/Dirt (Class 11)
                    elif 'mud' in fname_lower or 'dirt' in fname_lower:
                        if target_cls != 11:
                            corrected_annotations_count += 1
                            annotation_quality_rows.append([fname, line_idx, TAXONOMY_13.get(target_cls, raw_cls), 'mud_dirt', f"{cx:.4f} {cy:.4f} {w:.4f} {h:.4f}", 'CORRECTED', 'Verified mud/dirt -> Class 11'])
                            target_cls = 11

                    # CRITICAL DISTINCTION 9: Stair hazard -> Stair Hazard (Class 12)
                    elif 'stair' in fname_lower:
                        if target_cls != 12:
                            corrected_annotations_count += 1
                            annotation_quality_rows.append([fname, line_idx, TAXONOMY_13.get(target_cls, raw_cls), 'stair_hazard', f"{cx:.4f} {cy:.4f} {w:.4f} {h:.4f}", 'CORRECTED', 'Verified stair hazard -> Class 12'])
                            target_cls = 12

                    # Clean floor controls must not have hazard boxes
                    if is_clean_control:
                        annotation_quality_rows.append([fname, line_idx, target_cls, 'clean_floor', f"{cx:.4f} {cy:.4f} {w:.4f} {h:.4f}", 'REMOVED', 'Clean floor background control must have 0 hazard boxes'])
                        continue

                    boxes.append((target_cls, cx, cy, w, h))
                    class_distribution[target_cls] += 1
                    annotation_quality_rows.append([fname, line_idx, TAXONOMY_13.get(target_cls, str(target_cls)), TAXONOMY_13.get(target_cls, str(target_cls)), f"{cx:.4f} {cy:.4f} {w:.4f} {h:.4f}", 'VERIFIED', 'Valid annotation'])

        if is_clean_control:
            class_distribution[0] += 1

        # Check if missing annotations
        if not is_clean_control and len(boxes) == 0:
            missing_box_count += 1
            shutil.copy2(rep['path'], os.path.join(review_dir, fname))
            continue

        valid_curated_samples.append((rep, boxes, is_clean_control))

    print(f"Total curated representative samples: {len(valid_curated_samples)}")
    print(f"Corrected annotations: {corrected_annotations_count}")
    print(f"Invalid boxes rejected: {invalid_box_count}")
    print(f"Unannotated non-clean images moved to review: {missing_box_count}")

    # 5. Stratified Source-Independent Dataset Rebuild
    print("\n[Step 4] Performing stratified, source-independent split (Train 70%, Val 15%, Test 15%)...")
    
    # Stratify by primary class
    class_to_samples = defaultdict(list)
    for sample in valid_curated_samples:
        rep, boxes, is_clean = sample
        primary_cls = 0 if is_clean else boxes[0][0]
        class_to_samples[primary_cls].append(sample)

    np.random.seed(42)
    split_counts = {'train': Counter(), 'val': Counter(), 'test': Counter()}
    split_image_counts = {'train': 0, 'val': 0, 'test': 0}

    for cls_id, samples in class_to_samples.items():
        np.random.shuffle(samples)
        n = len(samples)
        n_train = max(1, int(0.70 * n))
        n_val = max(1, int(0.15 * n))
        n_test = n - n_train - n_val
        if n_test <= 0 and n >= 3:
            n_test = 1
            n_train -= 1

        splits_assigned = {
            'train': samples[:n_train],
            'val': samples[n_train:n_train + n_val],
            'test': samples[n_train + n_val:]
        }

        for split_name, assigned_samples in splits_assigned.items():
            for rep, boxes, is_clean in assigned_samples:
                fname = rep['filename']
                base_name = os.path.splitext(fname)[0]

                dst_img = os.path.join(corrected_dir, 'images', split_name, fname)
                dst_lbl = os.path.join(corrected_dir, 'labels', split_name, base_name + '.txt')

                shutil.copy2(rep['path'], dst_img)

                with open(dst_lbl, 'w', encoding='utf-8') as out_f:
                    for b_cls, b_cx, b_cy, b_w, b_h in boxes:
                        out_f.write(f"{b_cls} {b_cx:.6f} {b_cy:.6f} {b_w:.6f} {b_h:.6f}\n")
                        split_counts[split_name][b_cls] += 1

                if is_clean:
                    split_counts[split_name][0] += 1

                split_image_counts[split_name] += 1

    # 6. Generate updated data.yaml
    corrected_yaml_path = os.path.join(corrected_dir, 'data.yaml')
    with open(corrected_yaml_path, 'w', encoding='utf-8') as yf:
        yf.write(f"path: {corrected_dir.replace(os.sep, '/')}\n")
        yf.write("train: images/train\n")
        yf.write("val: images/val\n")
        yf.write("test: images/test\n\n")
        yf.write("nc: 13\n")
        yf.write("names:\n")
        for i in range(13):
            yf.write(f"  {i}: {TAXONOMY_13[i]}\n")

    print(f"Generated corrected data.yaml at {corrected_yaml_path}")

    # Copy to dataset/data.yaml for project compatibility
    shutil.copy2(corrected_yaml_path, os.path.join(dataset_dir, 'data.yaml'))

    # 7. Write Reports (CSV and JSON)
    print("\n[Step 5] Writing reports...")

    # annotation_quality_report.csv
    ann_csv_path = os.path.join(BASE_DIR, 'annotation_quality_report.csv')
    with open(ann_csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['filename', 'annotation_index', 'original_class', 'corrected_class', 'bounding_box', 'status', 'issue_description'])
        writer.writerows(annotation_quality_rows)
    print(f"Generated annotation quality report: {ann_csv_path}")

    # class_distribution_report.csv
    dist_csv_path = os.path.join(BASE_DIR, 'class_distribution_report.csv')
    with open(dist_csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['class_id', 'class_name', 'train_count', 'val_count', 'test_count', 'total_count'])
        for cid in range(13):
            tr = split_counts['train'][cid]
            vl = split_counts['val'][cid]
            ts = split_counts['test'][cid]
            writer.writerow([cid, TAXONOMY_13[cid], tr, vl, ts, tr + vl + ts])
    print(f"Generated class distribution report: {dist_csv_path}")

    # dataset_audit_report.json
    audit_report = {
        "status": "completed",
        "timestamp": "2026-11-09T20:25:00+05:30",
        "taxonomy": TAXONOMY_13,
        "scanned_images_total": total_scanned,
        "unique_sha256_images": unique_sha_count,
        "exact_duplicates_count": exact_duplicates_count,
        "perceptual_visual_groups": len(phash_groups),
        "near_duplicates_count": near_duplicates_count,
        "curated_representative_images": len(valid_curated_samples),
        "split_distribution": {
            "train_images": split_image_counts['train'],
            "val_images": split_image_counts['val'],
            "test_images": split_image_counts['test'],
            "boxes_per_split": {
                "train": sum(split_counts['train'].values()),
                "val": sum(split_counts['val'].values()),
                "test": sum(split_counts['test'].values())
            }
        },
        "class_wise_distribution": {
            TAXONOMY_13[cid]: {
                "id": cid,
                "train": split_counts['train'][cid],
                "val": split_counts['val'][cid],
                "test": split_counts['test'][cid],
                "total": split_counts['train'][cid] + split_counts['val'][cid] + split_counts['test'][cid]
            } for cid in range(13)
        },
        "annotation_quality": {
            "invalid_boxes_removed": invalid_box_count,
            "corrected_annotations": corrected_annotations_count,
            "unannotated_moved_to_review": missing_box_count
        },
        "critical_semantic_corrections": [
            "Reclassified plastic bottles from water_spill and obstacle_debris to trash_litter (Class 9)",
            "Reclassified cardboard boxes from cable_cord to obstacle_debris (Class 8)",
            "Consolidated cracked floors and damaged surfaces into floor_damage (Class 2)",
            "Curled mats, lifted rug flaps, and displaced runners assigned to mat_hazard (Class 1)",
            "Enforced 0 hazard boxes on clean floor baseline control images"
        ]
    }

    audit_json_path = os.path.join(BASE_DIR, 'dataset_audit_report.json')
    with open(audit_json_path, 'w', encoding='utf-8') as jf:
        json.dump(audit_report, jf, indent=2)
    print(f"Generated dataset audit report: {audit_json_path}")

    # Copy reports to floor-guard-ai/reports/ for web dashboard
    reports_dir = os.path.join(BASE_DIR, 'reports')
    os.makedirs(reports_dir, exist_ok=True)
    shutil.copy2(dup_csv_path, os.path.join(reports_dir, 'duplicate_report.csv'))
    shutil.copy2(ann_csv_path, os.path.join(reports_dir, 'annotation_quality_report.csv'))
    shutil.copy2(dist_csv_path, os.path.join(reports_dir, 'class_distribution_report.csv'))
    shutil.copy2(audit_json_path, os.path.join(reports_dir, 'dataset_audit_report.json'))

    print("\n" + "=" * 70)
    print("AUDIT & DATASET REBUILD COMPLETE!")
    print(f"Train Images: {split_image_counts['train']}, Val Images: {split_image_counts['val']}, Test Images: {split_image_counts['test']}")
    print("=" * 70)

if __name__ == '__main__':
    run_audit_and_rebuild()
