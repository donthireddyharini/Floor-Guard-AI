#!/usr/bin/env python3
"""
Floor Guard AI — Multi-Hazard Dataset Expansion & Pipeline
Expands dataset from 4 hazard classes to 10 universal floor hazard classes:
  0: water_spill (Liquid puddles, wet walkway pooling)
  1: oil_spill (Viscous motor oil, grease, petroleum)
  2: broken_glass (Shattered bottles, sharp fragments)
  3: obstacle_debris (Wooden pallets, crates, boxes, aisle blockages)
  4: chemical_spill (Neon green coolant, toxic industrial fluids)
  5: cable_cord (Trailing electrical wires, extension cords, trip cords)
  6: trash_litter (Plastic bottles, cans, rolling objects)
  7: food_waste (Dropped fruit peel, food scraps, organic slips)
  8: mud_dirt (Wet mud tracks, soil smear, scattered gravel/grit)
  9: stairs_hazard (Wet staircase steps, stairway slip zones)
"""

import os
import sys
import json
import random
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMAGE_GRID_PATH = r"C:/Users/donth_/.gemini/antigravity/brain/48597527-673a-4324-b41f-6a04ea6f4416/.user_uploaded/media_1792954711997_291505e9.jpg"

CLASSES = [
    "water_spill",      # 0
    "oil_spill",        # 1
    "broken_glass",     # 2
    "obstacle_debris",  # 3
    "chemical_spill",   # 4
    "cable_cord",       # 5
    "trash_litter",     # 6
    "food_waste",       # 7
    "mud_dirt",         # 8
    "stairs_hazard"     # 9
]

# Panel definitions with normalized bounding boxes: [cls_id, xc, yc, w, h]
PANEL_SPECS = [
    {
        "name": "water_spill_marble",
        "crop": (0, 0, 254, 189),
        "boxes": [
            [0, 0.48, 0.68, 0.65, 0.45],
            [3, 0.08, 0.45, 0.15, 0.40]  # caution cone as obstacle/marker
        ]
    },
    {
        "name": "cable_cord_hallway",
        "crop": (256, 0, 510, 189),
        "boxes": [
            [5, 0.52, 0.62, 0.88, 0.38]  # cable_cord (class 5)
        ]
    },
    {
        "name": "broken_glass_store",
        "crop": (512, 0, 766, 189),
        "boxes": [
            [2, 0.55, 0.58, 0.75, 0.52]  # broken_glass (class 2)
        ]
    },
    {
        "name": "stairs_slip_hazard",
        "crop": (768, 0, 1024, 189),
        "boxes": [
            [9, 0.58, 0.55, 0.78, 0.72]  # stairs_hazard (class 9)
        ]
    },
    {
        "name": "oil_spill_warehouse",
        "crop": (0, 192, 254, 380),
        "boxes": [
            [1, 0.50, 0.65, 0.70, 0.45]  # oil_spill (class 1)
        ]
    },
    {
        "name": "food_waste_peel",
        "crop": (256, 192, 510, 380),
        "boxes": [
            [7, 0.52, 0.68, 0.32, 0.26]  # food_waste (class 7)
        ]
    },
    {
        "name": "wet_surface_patio",
        "crop": (512, 192, 766, 380),
        "boxes": [
            [0, 0.55, 0.65, 0.80, 0.58]  # water_spill (class 0)
        ]
    },
    {
        "name": "pallet_obstacle_aisle",
        "crop": (768, 192, 1024, 380),
        "boxes": [
            [3, 0.62, 0.60, 0.72, 0.55]  # obstacle_debris (class 3)
        ]
    },
    {
        "name": "gravel_scatter_floor",
        "crop": (0, 383, 254, 575),
        "boxes": [
            [8, 0.52, 0.72, 0.75, 0.38]  # mud_dirt (class 8)
        ]
    },
    {
        "name": "plastic_bottle_rolling",
        "crop": (256, 383, 510, 575),
        "boxes": [
            [6, 0.52, 0.72, 0.45, 0.28]  # trash_litter (class 6)
        ]
    },
    {
        "name": "mud_tracks_soil",
        "crop": (512, 383, 766, 575),
        "boxes": [
            [8, 0.50, 0.60, 0.78, 0.68]  # mud_dirt (class 8)
        ]
    },
    {
        "name": "chemical_coolant_spill",
        "crop": (768, 383, 1024, 575),
        "boxes": [
            [4, 0.60, 0.75, 0.65, 0.38]  # chemical_spill (class 4)
        ]
    }
]

def augment_image_and_boxes(img, boxes, aug_type):
    """Apply augmentation to PIL image and adjust normalized bounding boxes."""
    w, h = img.size
    aug_boxes = [b.copy() for b in boxes]

    if aug_type == "orig":
        return img, aug_boxes

    if aug_type == "hflip":
        flipped_img = img.transpose(Image.FLIP_LEFT_RIGHT)
        for b in aug_boxes:
            b[1] = round(1.0 - b[1], 4)  # flip xc
        return flipped_img, aug_boxes

    if aug_type == "bright":
        enhancer = ImageEnhance.Brightness(img)
        return enhancer.enhance(1.22), aug_boxes

    if aug_type == "dim":
        enhancer = ImageEnhance.Brightness(img)
        return enhancer.enhance(0.82), aug_boxes

    if aug_type == "contrast":
        enhancer = ImageEnhance.Contrast(img)
        return enhancer.enhance(1.25), aug_boxes

    if aug_type == "hflip_bright":
        flipped_img = img.transpose(Image.FLIP_LEFT_RIGHT)
        enhancer = ImageEnhance.Brightness(flipped_img)
        for b in aug_boxes:
            b[1] = round(1.0 - b[1], 4)
        return enhancer.enhance(1.15), aug_boxes

    return img, aug_boxes

def generate_multi_hazard_dataset():
    print(f"Loading master multi-hazard composite from: {IMAGE_GRID_PATH}")
    master_im = Image.open(IMAGE_GRID_PATH).convert('RGB')

    aug_modes = ["orig", "hflip", "bright", "dim", "contrast", "hflip_bright"]

    splits = {
        "train": [],
        "val": [],
        "test": []
    }

    random.seed(42)

    for spec in PANEL_SPECS:
        crop_box = spec["crop"]
        panel_img = master_im.crop(crop_box)
        # Upscale to standard resolution (640x480) for high training fidelity
        panel_img = panel_img.resize((640, 480), Image.Resampling.LANCZOS)

        for a_idx, aug in enumerate(aug_modes):
            aug_im, aug_boxes = augment_image_and_boxes(panel_img, spec["boxes"], aug)
            item_name = f"floor_hazard_{spec['name']}_aug{a_idx}_{aug}"

            # Split distribution: 4 train, 1 val, 1 test
            if a_idx in [0, 1, 2, 5]:
                split = "train"
            elif a_idx == 3:
                split = "val"
            else:
                split = "test"

            splits[split].append({
                "name": item_name,
                "image": aug_im,
                "boxes": aug_boxes,
                "hazard": spec["name"]
            })

    # Save images and label files
    total_added = 0
    class_counts = {c: 0 for c in CLASSES}

    for split, items in splits.items():
        img_dir = os.path.join(BASE_DIR, "dataset", "images", split)
        lbl_dir = os.path.join(BASE_DIR, "dataset", "labels", split)
        os.makedirs(img_dir, exist_ok=True)
        os.makedirs(lbl_dir, exist_ok=True)

        for item in items:
            img_path = os.path.join(img_dir, f"{item['name']}.jpg")
            lbl_path = os.path.join(lbl_dir, f"{item['name']}.txt")

            item["image"].save(img_path, quality=95)

            with open(lbl_path, "w") as lf:
                for b in item["boxes"]:
                    cls_id, xc, yc, bw, bh = b
                    lf.write(f"{cls_id} {xc:.4f} {yc:.4f} {bw:.4f} {bh:.4f}\n")
                    class_counts[CLASSES[cls_id]] += 1

            total_added += 1

    print(f"Successfully generated {total_added} high-fidelity hazard samples across 10 classes.")
    print("Class Box Counts Added:")
    for c, cnt in class_counts.items():
        print(f"  - {c}: {cnt} instances")

    # Update dataset/data.yaml with all 10 classes
    yaml_path = os.path.join(BASE_DIR, "dataset", "data.yaml")
    yaml_content = f"""# Floor Guard AI — Universal 10-Class Floor Hazard Dataset
path: {BASE_DIR.replace(os.sep, '/')}/dataset
train: images/train
val: images/val
test: images/test

names:
  0: water_spill
  1: oil_spill
  2: broken_glass
  3: obstacle_debris
  4: chemical_spill
  5: cable_cord
  6: trash_litter
  7: food_waste
  8: mud_dirt
  9: stairs_hazard
"""
    with open(yaml_path, "w") as f:
        f.write(yaml_content)
    print(f"Updated {yaml_path} with 10 universal hazard classes.")

if __name__ == '__main__':
    generate_multi_hazard_dataset()
