#!/usr/bin/env python3
"""
Floor Guard AI — Comprehensive Balanced Dataset Generator
Generates balanced, multi-condition training samples across all 12 floor hazard classes,
with strong representation of bottles (trash_litter), spills, glass, cables, and obstacles.
"""

import os
import sys
import random
import numpy as np
import cv2
from PIL import Image, ImageEnhance, ImageFilter

BASE_DIR = r"c:\Users\donth_\Downloads\harry_client\floor-guard-ai"
DATASET_DIR = os.path.join(BASE_DIR, "dataset")

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
    "stairs_hazard",    # 9
    "floor_crack",      # 10
    "improper_mat"      # 11
]

def make_augmentations(img, boxes, prefix, out_items):
    """
    Generate diverse photometric & geometric augmentations:
    - Original
    - Horizontal Flip
    - Brightness (+25%, -22%)
    - Contrast (+30%, -20%)
    - Color hue variations
    - Warm & Cool lighting
    """
    w, h = img.size
    
    # 1. Orig
    out_items.append((f"{prefix}_orig", img.copy(), [b.copy() for b in boxes]))
    
    # 2. HFlip
    flipped_im = img.transpose(Image.FLIP_LEFT_RIGHT)
    flipped_boxes = []
    for b in boxes:
        cls_id, xc, yc, bw, bh = b
        flipped_boxes.append([cls_id, round(1.0 - xc, 4), yc, bw, bh])
    out_items.append((f"{prefix}_hflip", flipped_im, flipped_boxes))
    
    # 3. Bright
    enh_b = ImageEnhance.Brightness(img)
    out_items.append((f"{prefix}_bright", enh_b.enhance(1.25), [b.copy() for b in boxes]))
    
    # 4. Dim
    out_items.append((f"{prefix}_dim", enh_b.enhance(0.78), [b.copy() for b in boxes]))
    
    # 5. Contrast
    enh_c = ImageEnhance.Contrast(img)
    out_items.append((f"{prefix}_contrast", enh_c.enhance(1.30), [b.copy() for b in boxes]))
    
    # 6. HFlip + Bright
    enh_fb = ImageEnhance.Brightness(flipped_im)
    out_items.append((f"{prefix}_hflip_bright", enh_fb.enhance(1.18), [b.copy() for b in flipped_boxes]))
    
    # 7. Slight Warm / Hue shift
    arr = np.array(img).astype(float)
    arr[:, :, 0] = np.clip(arr[:, :, 0] * 1.08, 0, 255)
    arr[:, :, 2] = np.clip(arr[:, :, 2] * 0.92, 0, 255)
    warm_im = Image.fromarray(arr.astype(np.uint8))
    out_items.append((f"{prefix}_warm", warm_im, [b.copy() for b in boxes]))
    
    # 8. Slight Cool shift
    arr2 = np.array(img).astype(float)
    arr2[:, :, 2] = np.clip(arr2[:, :, 2] * 1.10, 0, 255)
    arr2[:, :, 0] = np.clip(arr2[:, :, 0] * 0.92, 0, 255)
    cool_im = Image.fromarray(arr2.astype(np.uint8))
    out_items.append((f"{prefix}_cool", cool_im, [b.copy() for b in boxes]))

def main():
    print("=== Generating Balanced Multi-Hazard Training Dataset ===")
    
    # Source 1: User's real bottle image
    user_bottle_path = os.path.join(BASE_DIR, "uploads", "originals", "1793940774293_5xw7se.jpeg")
    user_bottle_im = Image.open(user_bottle_path).convert('RGB')
    uw, uh = user_bottle_im.size
    
    # Exact bottle box: [475, 560, 835, 650]
    bottle_xc = round((475 + 835) / 2 / uw, 4)
    bottle_yc = round((560 + 650) / 2 / uh, 4)
    bottle_bw = round((835 - 475) / uw, 4)
    bottle_bh = round((650 - 560) / uh, 4)
    user_bottle_boxes = [[6, bottle_xc, bottle_yc, bottle_bw, bottle_bh]]
    
    # Source 2: Extracted bottle panel (r2_c1_plastic_bottle.jpg)
    panel_bottle_path = os.path.join(DATASET_DIR, "extracted_panels", "r2_c1_plastic_bottle.jpg")
    panel_bottle_im = Image.open(panel_bottle_path).convert('RGB').resize((640, 480), Image.Resampling.LANCZOS)
    panel_bottle_boxes = [[6, 0.52, 0.72, 0.45, 0.28]]
    
    # Source 3: Cropped focused user bottle
    crop_bottle_im = user_bottle_im.crop((320, 420, 960, 780)).resize((640, 480), Image.Resampling.LANCZOS)
    cw, ch = 960 - 320, 780 - 420
    c_xc = round(((475 + 835)/2 - 320) / cw, 4)
    c_yc = round(((560 + 650)/2 - 420) / ch, 4)
    c_bw = round((835 - 475) / cw, 4)
    c_bh = round((650 - 560) / ch, 4)
    crop_bottle_boxes = [[6, c_xc, c_yc, c_bw, c_bh]]
    
    all_generated = []
    
    # Generate variations for User Bottle
    make_augmentations(user_bottle_im, user_bottle_boxes, "user_coca_bottle_full", all_generated)
    make_augmentations(crop_bottle_im, crop_bottle_boxes, "user_coca_bottle_crop", all_generated)
    make_augmentations(panel_bottle_im, panel_bottle_boxes, "panel_plastic_bottle", all_generated)
    
    # Also generate color label variants of user bottle (green label Sprite, blue label Pepsi, gold label)
    for color_name, hue_adjust in [("green_label", (0.8, 1.3, 0.8)), ("blue_label", (0.8, 0.9, 1.4)), ("gold_label", (1.3, 1.2, 0.7))]:
        arr = np.array(user_bottle_im).astype(float)
        arr[:, :, 0] = np.clip(arr[:, :, 0] * hue_adjust[0], 0, 255)
        arr[:, :, 1] = np.clip(arr[:, :, 1] * hue_adjust[1], 0, 255)
        arr[:, :, 2] = np.clip(arr[:, :, 2] * hue_adjust[2], 0, 255)
        c_im = Image.fromarray(arr.astype(np.uint8))
        make_augmentations(c_im, user_bottle_boxes, f"user_bottle_{color_name}", all_generated)
    
    # Now expand underrepresented classes from extracted panels
    panels = {
        "chemical_spill": ("r2_c3_chemical_spill.jpg", [[4, 0.60, 0.75, 0.65, 0.38]]),
        "stairs_hazard": ("r0_c3_stairs_hazard.jpg", [[9, 0.58, 0.55, 0.78, 0.72]]),
        "food_waste": ("r1_c1_food_waste.jpg", [[7, 0.52, 0.68, 0.32, 0.26]]),
        "cable_cord": ("r0_c1_cable_cord.jpg", [[5, 0.52, 0.62, 0.88, 0.38]]),
        "mud_dirt": ("r2_c2_mud_soil_tracks.jpg", [[8, 0.50, 0.60, 0.78, 0.68]]),
        "water_spill": ("r0_c0_water_spill.jpg", [[0, 0.48, 0.68, 0.65, 0.45]]),
        "oil_spill": ("r1_c0_oil_spill.jpg", [[1, 0.50, 0.65, 0.70, 0.45]]),
        "obstacle_debris": ("r1_c3_pallet_obstacle.jpg", [[3, 0.62, 0.60, 0.72, 0.55]])
    }
    
    for hname, (pfile, pboxes) in panels.items():
        ppath = os.path.join(DATASET_DIR, "extracted_panels", pfile)
        if os.path.exists(ppath):
            pim = Image.open(ppath).convert('RGB').resize((640, 480), Image.Resampling.LANCZOS)
            make_augmentations(pim, pboxes, f"panel_{hname}_exp", all_generated)
    
    print(f"Total new augmented items prepared: {len(all_generated)}")
    
    # Shuffle and distribute into train (75%), val (15%), test (10%)
    random.seed(1337)
    random.shuffle(all_generated)
    
    n_total = len(all_generated)
    n_train = int(n_total * 0.75)
    n_val = int(n_total * 0.15)
    
    train_items = all_generated[:n_train]
    val_items = all_generated[n_train:n_train + n_val]
    test_items = all_generated[n_train + n_val:]
    
    for split_name, items in [("train", train_items), ("val", val_items), ("test", test_items)]:
        img_out = os.path.join(DATASET_DIR, "images", split_name)
        lbl_out = os.path.join(DATASET_DIR, "labels", split_name)
        for name, img, boxes in items:
            ip = os.path.join(img_out, f"{name}.jpg")
            lp = os.path.join(lbl_out, f"{name}.txt")
            img.save(ip, quality=95)
            with open(lp, "w") as f:
                for b in boxes:
                    f.write(f"{b[0]} {b[1]:.4f} {b[2]:.4f} {b[3]:.4f} {b[4]:.4f}\n")
        print(f"Saved {len(items)} samples to {split_name} split.")

    # Trim excessive broken glass files to prevent class bias (downsample 105 down to 25 in train)
    train_lbl_dir = os.path.join(DATASET_DIR, "labels", "train")
    train_img_dir = os.path.join(DATASET_DIR, "images", "train")
    
    glass_files = [f for f in os.listdir(train_lbl_dir) if f.startswith("phele_glass_")]
    if len(glass_files) > 25:
        to_remove = glass_files[25:]
        for f in to_remove:
            base = os.path.splitext(f)[0]
            lp = os.path.join(train_lbl_dir, f"{base}.txt")
            ip = os.path.join(train_img_dir, f"{base}.jpg")
            if os.path.exists(lp): os.remove(lp)
            if os.path.exists(ip): os.remove(ip)
        print(f"Trimmed {len(to_remove)} redundant glass files for class balance.")

if __name__ == '__main__':
    main()
