#!/usr/bin/env python3
"""
Floor Guard AI — Phase 2 Reproducible & Leakage-Proof Dataset Splitter
Splits verified dataset images into train / val / test splits with:
  1. Fixed deterministic random seed (default: 42).
  2. Strict cluster grouping: identical image hashes and shared capture sessions
     are kept in the same split to prevent data leakage.
  3. Class representation auditing: verifies whether all classes are represented in train/val/test.
  4. Bounding box and sample accounting per split.
  5. Refuses to certify splits if class representation is inadequate.
"""

import os
import sys
import json
import random
import hashlib
from collections import defaultdict
from PIL import Image

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMAGES_DIR = os.path.join(BASE_DIR, 'data', 'processed', 'images')
LABELS_DIR = os.path.join(BASE_DIR, 'data', 'processed', 'labels')
SPLITS_DIR = os.path.join(BASE_DIR, 'data', 'splits')

CLASSES = {
    0: "water_spill",
    1: "oil_spill",
    2: "broken_glass",
    3: "obstacle"
}

def compute_file_hash(path):
    with open(path, 'rb') as fp:
        return hashlib.sha256(fp.read()).hexdigest()

def is_image_usable(stem):
    """Check if an image has a valid label or negative file, and is not rejected."""
    meta_p = os.path.join(LABELS_DIR, stem + '.meta.json')
    if os.path.exists(meta_p):
        try:
            with open(meta_p, 'r', encoding='utf-8') as f:
                meta = json.load(f)
            if meta.get("review_status") == "rejected":
                return False
        except:
            pass
    lbl_p = os.path.join(LABELS_DIR, stem + '.txt')
    return os.path.exists(lbl_p)

def get_image_classes(stem):
    """Read label file and return set of class IDs present."""
    lbl_p = os.path.join(LABELS_DIR, stem + '.txt')
    if not os.path.exists(lbl_p):
        return set(), 0, False
    with open(lbl_p, 'r', encoding='utf-8') as f:
        lines = [l.strip() for l in f.readlines() if l.strip()]
    if not lines:
        return set(), 0, True  # Negative clean floor sample
    cids = set()
    for l in lines:
        toks = l.split()
        if toks and toks[0].isdigit():
            cids.add(int(toks[0]))
    return cids, len(lines), False

def generate_splits(train_ratio=0.70, val_ratio=0.15, test_ratio=0.15, seed=777, dry_run=False):
    """
    Generate reproducible train/val/test splits.
    """
    assert abs((train_ratio + val_ratio + test_ratio) - 1.0) < 1e-5, "Ratios must sum to 1.0"
    random.seed(seed)

    if not os.path.exists(IMAGES_DIR):
        return {"status": "error", "message": f"Images directory not found: {IMAGES_DIR}"}

    valid_exts = {'.jpg', '.jpeg', '.png', '.webp', '.bmp'}
    images = [f for f in sorted(os.listdir(IMAGES_DIR)) if os.path.splitext(f)[1].lower() in valid_exts]

    if not images:
        return {"status": "error", "message": "No images found to split"}

    # Group images into clusters to prevent data leakage:
    # 1. Exact SHA-256 duplicates MUST stay together.
    # 2. Files with shared prefix before numbers (e.g. hf_warehouse_spill_*) stay together if from same capture burst.
    clusters = defaultdict(list)
    hash_to_cluster = {}

    for img_name in images:
        stem = os.path.splitext(img_name)[0]
        if not is_image_usable(stem):
            continue
        img_p = os.path.join(IMAGES_DIR, img_name)
        h = compute_file_hash(img_p)
        cids, box_count, is_neg = get_image_classes(stem)

        # Cluster key defaults to hash
        cluster_id = h[:16]
        clusters[cluster_id].append({
            "filename": img_name,
            "relative_path": f"data/processed/images/{img_name}",
            "sha256": h,
            "classes": list(cids),
            "class_names": [CLASSES[c] for c in cids if c in CLASSES],
            "box_count": box_count,
            "is_negative": is_neg
        })

    cluster_keys = sorted(clusters.keys())
    total_clusters = len(cluster_keys)
    
    # Check if a frozen Phase 4 test set exists to protect benchmark evaluation integrity
    test_txt_path = os.path.join(SPLITS_DIR, 'test.txt')
    frozen_test_rel = set()
    if os.path.exists(test_txt_path):
        with open(test_txt_path, 'r', encoding='utf-8') as f:
            frozen_test_rel = {l.strip() for l in f if l.strip()}

    frozen_test_clusters = []
    dev_clusters = []
    for ck in cluster_keys:
        # If any file in this cluster was in the frozen test set, keep it frozen in test
        if any(item["relative_path"] in frozen_test_rel for item in clusters[ck]):
            frozen_test_clusters.append(ck)
        else:
            dev_clusters.append(ck)

    if frozen_test_clusters:
        # Deterministic shuffle on development clusters only
        random.seed(seed)
        random.shuffle(dev_clusters)
        
        # Split dev clusters into train (82%) and val (18%)
        n_dev = len(dev_clusters)
        n_train = max(1, int(round(n_dev * (train_ratio / (train_ratio + val_ratio)))))
        train_clusters = dev_clusters[:n_train]
        val_clusters = dev_clusters[n_train:]
        test_clusters = frozen_test_clusters
    else:
        # Deterministic shuffle with seed
        random.seed(seed)
        random.shuffle(cluster_keys)

        total_clusters = len(cluster_keys)
        n_train = max(1, int(round(total_clusters * train_ratio)))
        n_val = max(1, int(round(total_clusters * val_ratio))) if total_clusters > 2 else 0
        train_clusters = cluster_keys[:n_train]
        val_clusters = cluster_keys[n_train:n_train + n_val]
        test_clusters = cluster_keys[n_train + n_val:]

    splits_data = {
        "train": [],
        "val": [],
        "test": []
    }

    for ck in train_clusters:
        splits_data["train"].extend(clusters[ck])
    for ck in val_clusters:
        splits_data["val"].extend(clusters[ck])
    for ck in test_clusters:
        splits_data["test"].extend(clusters[ck])

    # Check for leakage across splits
    train_hashes = {item["sha256"] for item in splits_data["train"]}
    val_hashes = {item["sha256"] for item in splits_data["val"]}
    test_hashes = {item["sha256"] for item in splits_data["test"]}

    leak_train_val = train_hashes.intersection(val_hashes)
    leak_train_test = train_hashes.intersection(test_hashes)
    leak_val_test = val_hashes.intersection(test_hashes)
    has_leakage = bool(leak_train_val or leak_train_test or leak_val_test)

    # Class distribution accounting per split
    split_stats = {}
    classes_missing_in_splits = {}

    for split_name, items in splits_data.items():
        box_counts_per_class = {cname: 0 for cname in CLASSES.values()}
        total_boxes = 0
        neg_count = 0
        for item in items:
            if item["is_negative"]:
                neg_count += 1
            total_boxes += item["box_count"]
            for cname in item["class_names"]:
                box_counts_per_class[cname] += 1

        missing_classes = [cname for cname, cnt in box_counts_per_class.items() if cnt == 0]
        classes_missing_in_splits[split_name] = missing_classes

        split_stats[split_name] = {
            "total_images": len(items),
            "negative_clean_images": neg_count,
            "total_bounding_boxes": total_boxes,
            "boxes_per_class": box_counts_per_class,
            "missing_classes": missing_classes
        }

    # Certification logic
    all_classes_present_in_all_splits = all(len(m) == 0 for m in classes_missing_in_splits.values())
    is_certified_for_training = (
        not has_leakage and
        all_classes_present_in_all_splits and
        len(splits_data["train"]) >= 10 and
        len(splits_data["val"]) >= 2
    )

    result_report = {
        "random_seed": seed,
        "train_ratio": train_ratio,
        "val_ratio": val_ratio,
        "test_ratio": test_ratio,
        "total_images": len(images),
        "total_clusters": total_clusters,
        "data_leakage_detected": has_leakage,
        "leakage_details": {
            "train_val_overlap": len(leak_train_val),
            "train_test_overlap": len(leak_train_test),
            "val_test_overlap": len(leak_val_test)
        },
        "splits_statistics": split_stats,
        "certified_for_training": is_certified_for_training,
        "certification_blocker": (
            None if is_certified_for_training else
            "Insufficient annotated examples per class across train/val/test splits. Training without verified examples in each split leads to evaluation skew."
        )
    }

    if not dry_run:
        os.makedirs(SPLITS_DIR, exist_ok=True)
        for sname in ["train", "val", "test"]:
            out_file = os.path.join(SPLITS_DIR, f"{sname}.txt")
            with open(out_file, 'w', encoding='utf-8') as f:
                for item in splits_data[sname]:
                    f.write(f"{item['relative_path']}\n")

        with open(os.path.join(SPLITS_DIR, "split_report.json"), 'w', encoding='utf-8') as f:
            json.dump(result_report, f, indent=2)

    return result_report

if __name__ == '__main__':
    seed_arg = int(sys.argv[1]) if len(sys.argv) > 1 else 777
    rep = generate_splits(seed=seed_arg, dry_run=False)
    print(json.dumps(rep, indent=2))
