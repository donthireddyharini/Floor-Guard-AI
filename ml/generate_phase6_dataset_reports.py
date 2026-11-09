#!/usr/bin/env python3
"""
Floor Guard AI — Phase 6: Dataset Manifest & Distribution Reporter
Generates:
- reports/final_dataset_manifest.json
- reports/class_balance_report.json
- reports/train_val_test_distribution.json
Updates dataset/dataset_summary.json.
"""

import os
import sys
import glob
import json
from collections import defaultdict

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET_DIR = os.path.join(BASE_DIR, 'dataset')
REPORTS_DIR = os.path.join(BASE_DIR, 'reports')

CANONICAL_CLASSES = {
    0: 'water_spill',
    1: 'oil_spill',
    2: 'chemical_spill',
    3: 'broken_glass',
    4: 'cable_cord',
    5: 'obstacle_debris',
    6: 'trash_litter',
    7: 'food_waste',
    8: 'mud_dirt',
    9: 'stairs_hazard',
    10: 'floor_mat_hazard',
    11: 'floor_damage'
}

def main():
    print("=" * 70)
    print("FLOOR GUARD AI — PHASE 6 DATASET REPORTS GENERATION")
    print("=" * 70)

    splits = ['train', 'val', 'test']
    split_images = {}
    split_boxes = {s: defaultdict(int) for s in splits}
    clean_negatives = {s: 0 for s in splits}
    image_catalog = []

    for s in splits:
        img_dir = os.path.join(DATASET_DIR, 'images', s)
        lbl_dir = os.path.join(DATASET_DIR, 'labels', s)

        imgs = glob.glob(os.path.join(img_dir, "*.*"))
        split_images[s] = len(imgs)

        for ipath in imgs:
            fname = os.path.basename(ipath)
            base = os.path.splitext(fname)[0]
            lpath = os.path.join(lbl_dir, f"{base}.txt")

            boxes_in_img = []
            if os.path.exists(lpath):
                with open(lpath, 'r', encoding='utf-8') as lf:
                    lines = [l.strip() for l in lf if l.strip()]

                if not lines:
                    clean_negatives[s] += 1
                else:
                    for line in lines:
                        parts = line.split()
                        if len(parts) == 5:
                            cid = int(parts[0])
                            if cid in CANONICAL_CLASSES:
                                cname = CANONICAL_CLASSES[cid]
                                split_boxes[s][cname] += 1
                                boxes_in_img.append(cname)
            else:
                clean_negatives[s] += 1

            image_catalog.append({
                "filename": fname,
                "split": s,
                "is_clean_negative": len(boxes_in_img) == 0,
                "detected_hazards": boxes_in_img
            })

    total_imgs = sum(split_images.values())
    total_boxes = sum(sum(b.values()) for b in split_boxes.values())

    # 1. reports/final_dataset_manifest.json
    manifest = {
        "manifest_version": "7.0.0-canonical-12hazards",
        "taxonomy": "Floor Guard AI 12-Hazard + Clean Floor Baseline",
        "total_images": total_imgs,
        "total_bounding_boxes": total_boxes,
        "clean_floor_negative_controls": sum(clean_negatives.values()),
        "classes": list(CANONICAL_CLASSES.values()),
        "splits_summary": {
            s: {
                "image_count": split_images[s],
                "clean_negatives": clean_negatives[s],
                "bounding_boxes": sum(split_boxes[s].values()),
                "ratio_percent": round(split_images[s] / total_imgs * 100, 1)
            } for s in splits
        }
    }
    with open(os.path.join(REPORTS_DIR, 'final_dataset_manifest.json'), 'w') as f:
        json.dump(manifest, f, indent=2)

    # 2. reports/class_balance_report.json
    all_class_counts = {c: sum(split_boxes[s][c] for s in splits) for c in CANONICAL_CLASSES.values()}
    balance_report = {
        "report_title": "Floor Guard AI 12-Class Hazard Balance Analysis",
        "total_boxes_audited": total_boxes,
        "class_counts": all_class_counts,
        "newly_integrated_classes": {
            "floor_mat_hazard": all_class_counts['floor_mat_hazard'],
            "floor_damage": all_class_counts['floor_damage']
        },
        "sampling_strategy": "Class-aware loss weighting applied during training to counter minor frequency variances."
    }
    with open(os.path.join(REPORTS_DIR, 'class_balance_report.json'), 'w') as f:
        json.dump(balance_report, f, indent=2)

    # 3. reports/train_val_test_distribution.json
    dist_report = {
        "split_ratios": {
            "train": f"{round(split_images['train']/total_imgs*100, 1)}%",
            "val": f"{round(split_images['val']/total_imgs*100, 1)}%",
            "test": f"{round(split_images['test']/total_imgs*100, 1)}%"
        },
        "per_split_breakdown": {
            s: {
                "images": split_images[s],
                "clean_negatives": clean_negatives[s],
                "class_boxes": dict(split_boxes[s])
            } for s in splits
        }
    }
    with open(os.path.join(REPORTS_DIR, 'train_val_test_distribution.json'), 'w') as f:
        json.dump(dist_report, f, indent=2)

    # 4. Update dataset/dataset_summary.json
    dataset_summary = {
        "total": {
            "images": total_imgs,
            "clean_negatives": sum(clean_negatives.values()),
            "bounding_boxes": total_boxes,
            "taxonomy": "Canonical 12-Hazard Floor Hazard Taxonomy"
        },
        "train": {
            "images": split_images['train'],
            "clean_negatives": clean_negatives['train'],
            "total_boxes": sum(split_boxes['train'].values()),
            "boxes_per_class": dict(split_boxes['train'])
        },
        "val": {
            "images": split_images['val'],
            "clean_negatives": clean_negatives['val'],
            "total_boxes": sum(split_boxes['val'].values()),
            "boxes_per_class": dict(split_boxes['val'])
        },
        "test": {
            "images": split_images['test'],
            "clean_negatives": clean_negatives['test'],
            "total_boxes": sum(split_boxes['test'].values()),
            "boxes_per_class": dict(split_boxes['test'])
        }
    }
    with open(os.path.join(DATASET_DIR, 'dataset_summary.json'), 'w') as f:
        json.dump(dataset_summary, f, indent=2)

    print(f"Generated Phase 6 reports for {total_imgs} images ({total_boxes} boxes across 12 hazard classes):")
    print("  - reports/final_dataset_manifest.json")
    print("  - reports/class_balance_report.json")
    print("  - reports/train_val_test_distribution.json")
    print("  - dataset/dataset_summary.json updated.")

if __name__ == '__main__':
    main()
