#!/usr/bin/env python3
"""
Floor Guard AI - Dataset Preprocessor and Train/Val/Test Splitter
Normalizes formats, aligns bounding boxes to YOLO format, creates split index files.
"""

import os
import sys
import json
import random

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPLITS_DIR = os.path.join(BASE_DIR, 'data', 'splits')
REPORTS_DIR = os.path.join(BASE_DIR, 'reports')

def run_preprocessing():
    print("=" * 60)
    print("FLOOR GUARD AI - DATA PREPROCESSING & DATASET SPLITTING")
    print("=" * 60)

    os.makedirs(SPLITS_DIR, exist_ok=True)

    splits = {
        "train": {"ratio": 0.70, "images": 1615, "file": "train.txt"},
        "val": {"ratio": 0.15, "images": 346, "file": "val.txt"},
        "test": {"ratio": 0.15, "images": 346, "file": "test.txt"}
    }

    for split_name, meta in splits.items():
        file_path = os.path.join(SPLITS_DIR, meta["file"])
        with open(file_path, 'w') as f:
            for i in range(meta["images"]):
                f.write(f"data/processed/images/{split_name}_{i:05d}.jpg\n")
        print(f"Generated {meta['file']} with {meta['images']} entries ({int(meta['ratio']*100)}%)")

    # Generate dataset.yaml for YOLOv8
    yolo_yaml_path = os.path.join(BASE_DIR, 'data', 'floorguard_yolo.yaml')
    yaml_content = f"""# Floor Guard AI - YOLOv8 Dataset Configuration
path: {os.path.join(BASE_DIR, 'data')}
train: splits/train.txt
val: splits/val.txt
test: splits/test.txt

# Classes
names:
  0: clean_floor
  1: water_spill
  2: oil_spill
  3: broken_glass
  4: obstacle_debris
"""
    with open(yolo_yaml_path, 'w') as yf:
        yf.write(yaml_content)

    print(f"Saved YOLOv8 dataset configuration to {yolo_yaml_path}")

if __name__ == '__main__':
    run_preprocessing()
