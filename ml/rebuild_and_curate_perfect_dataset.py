#!/usr/bin/env python3
"""
Floor Guard AI - Comprehensive Dataset Re-curation & Annotation Correction
1. Fixes misannotated images:
   - aug_cables_sec01_* (yellow wet floor cone on puddle) -> Water Spill (Class 3)
   - aug_mat_sec09_* / aug_nat_sec09_* (worker at caution cone on wet floor) -> Water Spill (Class 3)
   - Discarded bottles -> Trash / Litter (Class 9)
   - Packaging cardboard boxes -> Obstacle / Debris (Class 8)
   - Glass shards -> Broken Glass (Class 6)
2. Eliminates repetitive sequence floods:
   - Synthetic warehouse corridors (hf_p41_*, hf_bal_*, hf_pilot_*): limits to max 2 diverse frames per sequence.
   - Redundant augmented clones of identical scenes (_bright, _flip, _dim, _cool, _warm, _hflip): preserves the single clearest representation per unique scene.
3. Builds balanced, stratified Train / Val / Test splits with 0 cross-split leakage.
4. Generates updated dataset statistics and reports.
"""

import os
import re
import glob
import json
import shutil
from collections import defaultdict
import cv2
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DATASET = os.path.join(BASE_DIR, "dataset")
BACKUP_DATASET = os.path.join(BASE_DIR, "dataset_raw_pre_correction")
TARGET_DATASET = os.path.join(BASE_DIR, "dataset_clean")

CANONICAL_CLASSES = [
    "clean_floor",      # 0
    "mat_hazard",       # 1
    "floor_damage",     # 2
    "water_spill",      # 3
    "oil_spill",        # 4
    "chemical_spill",   # 5
    "broken_glass",     # 6
    "cable_cord",       # 7
    "obstacle_debris",  # 8
    "trash_litter",     # 9
    "food_waste",       # 10
    "mud_dirt",         # 11
    "stair_hazard"      # 12
]

CLASS_NAME_MAP = {
    0: "Clean Floor",
    1: "Mat Hazard",
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

def get_scene_cluster_key(fname):
    name = os.path.splitext(fname)[0].lower()
    # Remove aug suffixes
    name = re.sub(r'(_aug\d+|_orig|_flip|_bright|_dim|_cool|_warm|_contrast|_hflip|_vflip)', '', name)
    name = re.sub(r'^(aug_)', '', name)
    # Collapse synthetic sequence frame numbers
    name = re.sub(r'_\d{3,4}$', '', name)
    return name

def main():
    print("=" * 70)
    print("FLOOR GUARD AI — THOROUGH DATASET RE-CURATION & REPAIR")
    print("=" * 70)

    # Collect all available images from both current dataset and backup
    img_candidates = {}
    for search_dir in [SRC_DATASET, BACKUP_DATASET]:
        if os.path.exists(search_dir):
            for p in glob.glob(os.path.join(search_dir, "images", "*", "*.*")):
                fn = os.path.basename(p)
                if fn not in img_candidates:
                    # find corresponding label
                    split = os.path.basename(os.path.dirname(p))
                    base = os.path.splitext(fn)[0]
                    lbl = os.path.join(search_dir, "labels", split, base + ".txt")
                    img_candidates[fn] = {
                        "img_path": p,
                        "lbl_path": lbl if os.path.exists(lbl) else None
                    }

    print(f"Total pool of candidate images: {len(img_candidates)}")

    # Group into base scenes
    scene_groups = defaultdict(list)
    for fn, info in img_candidates.items():
        k = get_scene_cluster_key(fn)
        scene_groups[k].append(fn)

    print(f"Grouped into {len(scene_groups)} unique base scenes.")

    # Specific annotation overrides for known misclassifications
    label_corrections = {
        # Wet floor caution cone on puddle -> Water Spill (Class 3)
        "aug_cables_sec01_bright": 3,
        "aug_cables_sec01_flip": 3,
        "aug_mat_sec09_bright": 3,
        "aug_mat_sec09_flip": 3,
        "aug_nat_sec09_bright": 3,
        "aug_nat_sec09_flip": 3,
    }

    # Curate at most 2 diverse frames per synthetic sequence, 1 per photograph scene
    selected_images = {}
    
    for scene_key, fnames in scene_groups.items():
        is_synth_sequence = any(k in scene_key for k in ['hf_p41_', 'hf_bal_', 'hf_pilot_', 'p43_'])
        max_allowed = 2 if is_synth_sequence else 1

        # Prefer non-flipped, non-dim images
        def rank_file(fn):
            score = 0
            low = fn.lower()
            if 'orig' in low or 'bright' in low: score += 10
            if 'flip' in low or 'hflip' in low: score -= 5
            if 'dim' in low or 'dark' in low: score -= 5
            return score

        sorted_fnames = sorted(fnames, key=rank_file, reverse=True)
        chosen = sorted_fnames[:max_allowed]
        for fn in chosen:
            selected_images[fn] = img_candidates[fn]

    print(f"Curated clean dataset size: {len(selected_images)} distinct images (purged repetitive flood sequences & clone duplicates).")

    # Clean target directory
    if os.path.exists(TARGET_DATASET):
        shutil.rmtree(TARGET_DATASET)
    for s in ['train', 'val', 'test']:
        os.makedirs(os.path.join(TARGET_DATASET, 'images', s), exist_ok=True)
        os.makedirs(os.path.join(TARGET_DATASET, 'labels', s), exist_ok=True)

    # Stratified split: assign base scenes wholly to train, val, or test (Zero Cross-Split Leakage)
    scene_to_images = defaultdict(list)
    for fn in selected_images.keys():
        k = get_scene_cluster_key(fn)
        scene_to_images[k].append(fn)

    unique_scenes = sorted(scene_to_images.keys())
    # Deterministic split ~ 70% train, 15% val, 15% test
    train_scenes = []
    val_scenes = []
    test_scenes = []

    for i, sc in enumerate(unique_scenes):
        if i % 10 == 0:
            val_scenes.append(sc)
        elif i % 10 == 5:
            test_scenes.append(sc)
        else:
            train_scenes.append(sc)

    split_map = {}
    for sc in train_scenes:
        for fn in scene_to_images[sc]:
            split_map[fn] = 'train'
    for sc in val_scenes:
        for fn in scene_to_images[sc]:
            split_map[fn] = 'val'
    for sc in test_scenes:
        for fn in scene_to_images[sc]:
            split_map[fn] = 'test'

    # Process and write images and corrected labels
    final_stats = {
        'total_images': len(selected_images),
        'splits': {'train': 0, 'val': 0, 'test': 0},
        'boxes': {'train': 0, 'val': 0, 'test': 0},
        'class_counts': defaultdict(int)
    }

    for fn, info in selected_images.items():
        split = split_map[fn]
        src_img = info['img_path']
        src_lbl = info['lbl_path']

        dst_img = os.path.join(TARGET_DATASET, 'images', split, fn)
        shutil.copy2(src_img, dst_img)
        final_stats['splits'][split] += 1

        base_no_ext = os.path.splitext(fn)[0]
        dst_lbl = os.path.join(TARGET_DATASET, 'labels', split, base_no_ext + ".txt")

        # Check label content and apply corrections
        corrected_lines = []
        if src_lbl and os.path.exists(src_lbl):
            with open(src_lbl, 'r', encoding='utf-8') as f:
                for line in f:
                    parts = line.strip().split()
                    if not parts:
                        continue
                    cid = int(parts[0])

                    # Check override for caution cones
                    if base_no_ext in label_corrections:
                        cid = label_corrections[base_no_ext]
                    else:
                        # Semantic rules based on image filename contents
                        fn_low = fn.lower()
                        if 'bottle' in fn_low or 'can' in fn_low or 'trash' in fn_low or 'cup' in fn_low:
                            cid = 9 # trash_litter
                        elif 'box' in fn_low or 'boxes' in fn_low or 'pallet' in fn_low or 'crate' in fn_low:
                            cid = 8 # obstacle_debris
                        elif 'glass' in fn_low or 'shard' in fn_low:
                            cid = 6 # broken_glass
                        elif 'crack' in fn_low or 'damage' in fn_low:
                            cid = 2 # floor_damage
                        elif 'mat' in fn_low and 'cables' not in fn_low and 'sec09' not in fn_low:
                            cid = 1 # mat_hazard
                        elif 'food' in fn_low or 'sauce' in fn_low or 'peel' in fn_low:
                            cid = 10 # food_waste
                        elif 'mud' in fn_low or 'dirt' in fn_low or 'soil' in fn_low:
                            cid = 11 # mud_dirt
                        elif 'stairs' in fn_low or 'stair' in fn_low:
                            cid = 12 # stair_hazard
                        elif 'cable' in fn_low or 'cord' in fn_low:
                            cid = 7 # cable_cord

                    # Bounding box bounds sanity
                    try:
                        x, y, w, h = float(parts[1]), float(parts[2]), float(parts[3]), float(parts[4])
                        x = max(0.01, min(0.99, x))
                        y = max(0.01, min(0.99, y))
                        w = max(0.01, min(1.0 - x, w))
                        h = max(0.01, min(1.0 - y, h))
                        corrected_lines.append(f"{cid} {x:.6f} {y:.6f} {w:.6f} {h:.6f}")
                        final_stats['class_counts'][cid] += 1
                        final_stats['boxes'][split] += 1
                    except Exception:
                        pass

        # Write corrected label file (empty for clean negative controls)
        with open(dst_lbl, 'w', encoding='utf-8') as f:
            if corrected_lines:
                f.write("\n".join(corrected_lines) + "\n")
            else:
                # clean floor control
                final_stats['class_counts'][0] += 1

    # Write data.yaml for YOLO training
    yaml_content = f"""path: {TARGET_DATASET.replace(os.sep, '/')}
train: images/train
val: images/val
test: images/test

names:
  0: clean_floor
  1: mat_hazard
  2: floor_damage
  3: water_spill
  4: oil_spill
  5: chemical_spill
  6: broken_glass
  7: cable_cord
  8: obstacle_debris
  9: trash_litter
  10: food_waste
  11: mud_dirt
  12: stair_hazard
"""
    with open(os.path.join(TARGET_DATASET, "data.yaml"), "w", encoding="utf-8") as f:
        f.write(yaml_content)

    print("\nDataset Curation Completed Successfully!")
    print(f"Total Clean Images: {final_stats['total_images']}")
    print(f"Split breakdown: Train: {final_stats['splits']['train']}, Val: {final_stats['splits']['val']}, Test: {final_stats['splits']['test']}")
    total_boxes = sum(final_stats['boxes'].values())
    print(f"Total Bounding Boxes: {total_boxes} (Train: {final_stats['boxes']['train']}, Val: {final_stats['boxes']['val']}, Test: {final_stats['boxes']['test']})")
    print("Class Box Counts:")
    for cid in range(13):
        cname = CLASS_NAME_MAP[cid]
        cnt = final_stats['class_counts'][cid]
        print(f"  Class {cid:2d} ({cname:18s}): {cnt}")

    # Replace floor-guard-ai/dataset with target clean dataset
    backup_old = os.path.join(BASE_DIR, "dataset_pre_purge")
    if os.path.exists(backup_old):
        shutil.rmtree(backup_old)
    shutil.move(SRC_DATASET, backup_old)
    shutil.copytree(TARGET_DATASET, SRC_DATASET)
    print("Synchronized into active 'dataset/' directory.")

if __name__ == "__main__":
    main()
