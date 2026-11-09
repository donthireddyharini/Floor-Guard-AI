#!/usr/bin/env python3
"""
Floor Guard AI — Standard Clean Dataset Consolidator
Consolidates all verified, genuine hazard images and labels into a clean,
standardized ML workflow dataset directory: dataset/images/ and dataset/labels/
with train, val, and test splits and data.yaml.
Removes all raw cluttered directories and old temporary files.
"""

import os
import shutil
import json
from pathlib import Path
from PIL import Image

BASE_DIR = Path(__file__).resolve().parent.parent
DATASET_DIR = BASE_DIR / 'dataset'

SPLITS = ['train', 'val', 'test']
for s in SPLITS:
    (DATASET_DIR / 'images' / s).mkdir(parents=True, exist_ok=True)
    (DATASET_DIR / 'labels' / s).mkdir(parents=True, exist_ok=True)

CLASS_MAP = {0: 'water_spill', 1: 'oil_spill', 2: 'broken_glass', 3: 'obstacle'}

def process_file_list(txt_path, split_name, existing_names):
    count = 0
    with open(txt_path, 'r', encoding='utf-8') as f:
        lines = [l.strip().replace('\\', '/') for l in f if l.strip()]

    for rel_path in lines:
        src_img = BASE_DIR / rel_path
        if not src_img.exists():
            continue

        base_name = src_img.name
        if base_name in existing_names:
            continue
        existing_names.add(base_name)

        src_lbl = Path(str(src_img).replace('images', 'labels')).with_suffix('.txt')

        # Verify image
        try:
            with Image.open(src_img) as im:
                im.verify()
        except Exception as e:
            print(f"Skipping corrupt image {src_img}: {e}")
            continue

        dest_img = DATASET_DIR / 'images' / split_name / base_name
        dest_lbl = DATASET_DIR / 'labels' / split_name / src_lbl.name

        shutil.copy2(src_img, dest_img)
        if src_lbl.exists():
            shutil.copy2(src_lbl, dest_lbl)
        else:
            with open(dest_lbl, 'w') as fp:
                pass # empty label

        count += 1
    return count

def add_expanded_benchmark(existing_names):
    bench_dir = BASE_DIR / 'data' / 'benchmark_expanded'
    if not bench_dir.exists():
        return {'train': 0, 'val': 0, 'test': 0}

    img_dir = bench_dir / 'images'
    lbl_dir = bench_dir / 'labels'
    if not img_dir.exists():
        return {'train': 0, 'val': 0, 'test': 0}

    files = sorted([f for f in os.listdir(img_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
    
    # Distribute: 15 to train, 5 to val, 5 to test
    counts = {'train': 0, 'val': 0, 'test': 0}
    for idx, f in enumerate(files):
        if f in existing_names:
            continue
        existing_names.add(f)

        src_img = img_dir / f
        src_lbl = lbl_dir / Path(f).with_suffix('.txt')

        try:
            with Image.open(src_img) as im:
                im.verify()
        except Exception:
            continue

        if idx % 5 == 0:
            s = 'test'
        elif idx % 5 == 1:
            s = 'val'
        else:
            s = 'train'

        dest_img = DATASET_DIR / 'images' / s / f
        dest_lbl = DATASET_DIR / 'labels' / s / src_lbl.name

        shutil.copy2(src_img, dest_img)
        if src_lbl.exists():
            shutil.copy2(src_lbl, dest_lbl)
        else:
            with open(dest_lbl, 'w') as fp:
                pass
        counts[s] += 1

    return counts

def main():
    print("=" * 60)
    print("BUILDING CLEAN, CONSOLIDATED DATASET (ML WORKFLOW STRUCTURE)")
    print("=" * 60)

    existing_names = set()

    # 1. Transfer existing splits
    splits_files = {
        'train': BASE_DIR / 'data' / 'splits' / 'train.txt',
        'val': BASE_DIR / 'data' / 'splits' / 'val.txt',
        'test': BASE_DIR / 'data' / 'splits' / 'test.txt'
    }

    base_counts = {}
    for s, p in splits_files.items():
        if p.exists():
            base_counts[s] = process_file_list(p, s, existing_names)
        else:
            base_counts[s] = 0

    print(f"Base split items copied: {base_counts}")

    # 2. Integrate expanded benchmark items cleanly
    bench_counts = add_expanded_benchmark(existing_names)
    print(f"Expanded benchmark items integrated: {bench_counts}")

    # 3. Create dataset/data.yaml
    yaml_content = f"""# Floor Guard AI — Clean Consolidated Dataset
path: {str(DATASET_DIR).replace('\\', '/')}
train: images/train
val: images/val
test: images/test

names:
  0: water_spill
  1: oil_spill
  2: broken_glass
  3: obstacle
"""
    with open(DATASET_DIR / 'data.yaml', 'w', encoding='utf-8') as f:
        f.write(yaml_content)

    # 4. Inventory counts and bounding boxes
    summary = {}
    total_imgs = 0
    total_boxes = 0
    class_boxes = {0: 0, 1: 0, 2: 0, 3: 0}
    clean_floors = 0

    for s in SPLITS:
        s_img_dir = DATASET_DIR / 'images' / s
        s_lbl_dir = DATASET_DIR / 'labels' / s
        imgs = [f for f in os.listdir(s_img_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        s_clean = 0
        s_boxes = 0

        for im in imgs:
            lbl_file = s_lbl_dir / Path(im).with_suffix('.txt')
            if lbl_file.exists():
                with open(lbl_file, 'r', encoding='utf-8') as lfp:
                    lines = [l.strip() for l in lfp if l.strip()]
                if len(lines) == 0:
                    s_clean += 1
                else:
                    for line in lines:
                        parts = line.split()
                        cid = int(parts[0])
                        class_boxes[cid] = class_boxes.get(cid, 0) + 1
                        s_boxes += 1
            else:
                s_clean += 1

        summary[s] = {
            'images': len(imgs),
            'clean_negatives': s_clean,
            'hazards': len(imgs) - s_clean,
            'boxes': s_boxes
        }
        total_imgs += len(imgs)
        total_boxes += s_boxes
        clean_floors += s_clean

    summary['total'] = {
        'images': total_imgs,
        'clean_floor_negatives': clean_floors,
        'hazard_images': total_imgs - clean_floors,
        'bounding_boxes': total_boxes,
        'boxes_per_class': {CLASS_MAP[cid]: count for cid, count in class_boxes.items()}
    }

    with open(DATASET_DIR / 'dataset_summary.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)

    print("\nDataset Summary:")
    print(f"  Train: {summary['train']['images']} images ({summary['train']['boxes']} bboxes)")
    print(f"  Val:   {summary['val']['images']} images ({summary['val']['boxes']} bboxes)")
    print(f"  Test:  {summary['test']['images']} images ({summary['test']['boxes']} bboxes)")
    print(f"  Total Images: {total_imgs} | Clean Negatives: {clean_floors} | Bounding Boxes: {total_boxes}")
    print(f"  Classes: {summary['total']['boxes_per_class']}")
    print(f"Generated clean dataset configuration: {DATASET_DIR / 'data.yaml'}")

    # 5. Clean up old cluttered data/ directories
    data_dir = BASE_DIR / 'data'
    unwanted_subdirs = ['raw', 'processed', 'benchmark_expanded', 'splits']
    for u in unwanted_subdirs:
        p = data_dir / u
        if p.exists():
            print(f"Removing cluttered directory: {p.relative_to(BASE_DIR)}")
            shutil.rmtree(p, ignore_errors=True)

    # Remove old clutter manifests
    old_manifests = [
        data_dir / 'pilot_manifest.json',
        data_dir / 'huggingface_manifest.json',
        data_dir / 'floorguard_yolo_abs.yaml'
    ]
    for om in old_manifests:
        if om.exists():
            om.unlink()

    print("\n" + "=" * 60)
    print("CLEAN DATASET SETUP COMPLETE!")
    print("=" * 60)

if __name__ == '__main__':
    main()
