#!/usr/bin/env python3
"""
Floor Guard AI — Comprehensive All-Hazard Dataset Expansion & Balancer
Balances all 12 hazard categories with heavy representation of:
- Transparent plastic water bottles (Kinley/Bisleri clear bottle with blue cap)
- Red Coca-Cola bottles and soda cans
- Water spills & glossy liquid puddles
- Oil spills & dark viscous lubricants
- Fluorescent green / yellow chemical coolant leaks
- Broken glass shards and fractured jars
- Trailing electrical cables & extension cords
- Dropped pallets, boxes, and obstacles
- Organic food waste & sauce splatters
- Wet mud footprints & soil deposits
- Stairs hazards & step slip zones
- Floor tile cracks & curled safety mats
"""

import os
import sys
import random
import numpy as np
import cv2
from PIL import Image, ImageEnhance, ImageFilter

BASE_DIR = r"c:\Users\donth_\Downloads\harry_client\floor-guard-ai"
DATASET_DIR = os.path.join(BASE_DIR, "dataset")

def make_augmentations(img, boxes, prefix, out_items):
    """Generate comprehensive augmentations for robust multi-angle model generalization."""
    w, h = img.size
    
    # 1. Original
    out_items.append((f"{prefix}_orig", img.copy(), [b.copy() for b in boxes]))
    
    # 2. Horizontal Flip
    flipped_im = img.transpose(Image.FLIP_LEFT_RIGHT)
    flipped_boxes = []
    for b in boxes:
        cls_id, xc, yc, bw, bh = b
        flipped_boxes.append([cls_id, round(1.0 - xc, 4), yc, bw, bh])
    out_items.append((f"{prefix}_hflip", flipped_im, flipped_boxes))
    
    # 3. Brightness Up (+25%)
    enh_b = ImageEnhance.Brightness(img)
    out_items.append((f"{prefix}_bright", enh_b.enhance(1.25), [b.copy() for b in boxes]))
    
    # 4. Dim / Low Light (-22%)
    out_items.append((f"{prefix}_dim", enh_b.enhance(0.78), [b.copy() for b in boxes]))
    
    # 5. Contrast Boost (+28%)
    enh_c = ImageEnhance.Contrast(img)
    out_items.append((f"{prefix}_contrast", enh_c.enhance(1.28), [b.copy() for b in boxes]))
    
    # 6. Flipped + Bright
    enh_fb = ImageEnhance.Brightness(flipped_im)
    out_items.append((f"{prefix}_hflip_bright", enh_fb.enhance(1.20), [b.copy() for b in flipped_boxes]))
    
    # 7. Warm Lighting / Yellow Floor Tone
    arr = np.array(img).astype(float)
    arr[:, :, 0] = np.clip(arr[:, :, 0] * 1.08, 0, 255)
    arr[:, :, 2] = np.clip(arr[:, :, 2] * 0.90, 0, 255)
    out_items.append((f"{prefix}_warm", Image.fromarray(arr.astype(np.uint8)), [b.copy() for b in boxes]))
    
    # 8. Cool Lighting / Fluorescent Hospital / Warehouse Tone
    arr2 = np.array(img).astype(float)
    arr2[:, :, 2] = np.clip(arr2[:, :, 2] * 1.12, 0, 255)
    arr2[:, :, 0] = np.clip(arr2[:, :, 0] * 0.90, 0, 255)
    out_items.append((f"{prefix}_cool", Image.fromarray(arr2.astype(np.uint8)), [b.copy() for b in boxes]))

def main():
    print("=== Expanding and Balancing All 12 Floor Hazard Categories ===")
    all_generated = []
    
    # -------------------------------------------------------------
    # 1. USER'S TRANSPARENT WATER BOTTLE (1793945880487_p77ihr.jpeg)
    # -------------------------------------------------------------
    user_clear_bottle_path = os.path.join(BASE_DIR, "uploads", "originals", "1793945880487_p77ihr.jpeg")
    if os.path.exists(user_clear_bottle_path):
        clear_im = Image.open(user_clear_bottle_path).convert('RGB')
        uw, uh = clear_im.size
        # Bottle coordinates: x: 360..850, y: 120..500
        xc = round((360 + 850) / 2 / uw, 4)
        yc = round((120 + 500) / 2 / uh, 4)
        bw = round((850 - 360) / uw, 4)
        bh = round((500 - 120) / uh, 4)
        clear_boxes = [[6, xc, yc, bw, bh]] # class 6 = trash_litter
        
        # Full view
        make_augmentations(clear_im, clear_boxes, "clear_water_bottle_full", all_generated)
        
        # Focused Crop on the bottle
        crop_clear = clear_im.crop((280, 80, 950, 560)).resize((640, 480), Image.Resampling.LANCZOS)
        cw, ch = 950 - 280, 560 - 80
        c_xc = round(((360 + 850)/2 - 280) / cw, 4)
        c_yc = round(((120 + 500)/2 - 80) / ch, 4)
        c_bw = round((850 - 360) / cw, 4)
        c_bh = round((500 - 120) / ch, 4)
        crop_boxes = [[6, c_xc, c_yc, c_bw, c_bh]]
        make_augmentations(crop_clear, crop_boxes, "clear_water_bottle_crop", all_generated)
        
        # Cap-focused angle (diagonal bottle)
        crop_cap = clear_im.crop((450, 180, 880, 520)).resize((640, 480), Image.Resampling.LANCZOS)
        make_augmentations(crop_cap, [[6, 0.50, 0.50, 0.78, 0.65]], "clear_bottle_cap_angle", all_generated)
        
        # Color variants for clear plastic (greenish Sprite plastic, clear Kinley, Aquafina blue)
        for cname, adjust in [("green_plastic", (0.85, 1.25, 0.85)), ("cyan_plastic", (0.85, 1.15, 1.30)), ("amber_bottle", (1.25, 1.10, 0.75))]:
            arr = np.array(clear_im).astype(float)
            arr[:, :, 0] = np.clip(arr[:, :, 0] * adjust[0], 0, 255)
            arr[:, :, 1] = np.clip(arr[:, :, 1] * adjust[1], 0, 255)
            arr[:, :, 2] = np.clip(arr[:, :, 2] * adjust[2], 0, 255)
            make_augmentations(Image.fromarray(arr.astype(np.uint8)), clear_boxes, f"clear_bottle_{cname}", all_generated)
        print("-> Added transparent water bottle variations.")
    
    # -------------------------------------------------------------
    # 2. USER'S COCA-COLA BOTTLE (1793940774293_5xw7se.jpeg)
    # -------------------------------------------------------------
    user_coca_path = os.path.join(BASE_DIR, "uploads", "originals", "1793940774293_5xw7se.jpeg")
    if os.path.exists(user_coca_path):
        coca_im = Image.open(user_coca_path).convert('RGB')
        uw, uh = coca_im.size
        xc = round((475 + 835) / 2 / uw, 4)
        yc = round((560 + 650) / 2 / uh, 4)
        bw = round((835 - 475) / uw, 4)
        bh = round((650 - 560) / uh, 4)
        coca_boxes = [[6, xc, yc, bw, bh]]
        make_augmentations(coca_im, coca_boxes, "coca_bottle_full", all_generated)
        
        crop_coca = coca_im.crop((320, 420, 960, 780)).resize((640, 480), Image.Resampling.LANCZOS)
        make_augmentations(crop_coca, [[6, 0.50, 0.50, 0.65, 0.40]], "coca_bottle_crop", all_generated)
        print("-> Added Coca-Cola bottle variations.")

    # -------------------------------------------------------------
    # 3. MULTI-HAZARD PANELS (Chemical, Mud, Food, Spills, Cables, Stairs)
    # -------------------------------------------------------------
    panels = {
        "chemical_spill": ("r2_c3_chemical_spill.jpg", [[4, 0.60, 0.75, 0.65, 0.38]]),
        "stairs_hazard": ("r0_c3_stairs_hazard.jpg", [[9, 0.58, 0.55, 0.78, 0.72]]),
        "food_waste": ("r1_c1_food_waste.jpg", [[7, 0.52, 0.68, 0.32, 0.26]]),
        "cable_cord": ("r0_c1_cable_cord.jpg", [[5, 0.52, 0.62, 0.88, 0.38]]),
        "mud_dirt": ("r2_c2_mud_soil_tracks.jpg", [[8, 0.50, 0.60, 0.78, 0.68]]),
        "water_spill": ("r0_c0_water_spill.jpg", [[0, 0.48, 0.68, 0.65, 0.45]]),
        "oil_spill": ("r1_c0_oil_spill.jpg", [[1, 0.50, 0.65, 0.70, 0.45]]),
        "obstacle_debris": ("r1_c3_pallet_obstacle.jpg", [[3, 0.62, 0.60, 0.72, 0.55]]),
        "trash_litter_panel": ("r2_c1_plastic_bottle.jpg", [[6, 0.52, 0.72, 0.45, 0.28]])
    }
    
    for hname, (pfile, pboxes) in panels.items():
        ppath = os.path.join(DATASET_DIR, "extracted_panels", pfile)
        if os.path.exists(ppath):
            pim = Image.open(ppath).convert('RGB').resize((640, 480), Image.Resampling.LANCZOS)
            make_augmentations(pim, pboxes, f"multi_{hname}", all_generated)
            
            # Additional zoomed crop for close-up spill/waste detection
            pw, ph = pim.size
            crop_pim = pim.crop((int(pw * 0.15), int(ph * 0.25), int(pw * 0.85), int(ph * 0.95))).resize((640, 480), Image.Resampling.LANCZOS)
            make_augmentations(crop_pim, pboxes, f"multi_{hname}_crop", all_generated)

    print(f"Total new augmented items prepared: {len(all_generated)}")

    # -------------------------------------------------------------
    # 4. DISTRIBUTE INTO TRAIN (75%), VAL (15%), TEST (10%)
    # -------------------------------------------------------------
    random.seed(42)
    random.shuffle(all_generated)
    
    n_total = len(all_generated)
    n_train = int(n_total * 0.75)
    n_val = int(n_total * 0.15)
    
    splits = [
        ("train", all_generated[:n_train]),
        ("val", all_generated[n_train:n_train + n_val]),
        ("test", all_generated[n_train + n_val:])
    ]
    
    for split_name, items in splits:
        img_out = os.path.join(DATASET_DIR, "images", split_name)
        lbl_out = os.path.join(DATASET_DIR, "labels", split_name)
        os.makedirs(img_out, exist_ok=True)
        os.makedirs(lbl_out, exist_ok=True)
        for name, img, boxes in items:
            ip = os.path.join(img_out, f"{name}.jpg")
            lp = os.path.join(lbl_out, f"{name}.txt")
            img.save(ip, quality=95)
            with open(lp, "w") as f:
                for b in boxes:
                    f.write(f"{b[0]} {b[1]:.4f} {b[2]:.4f} {b[3]:.4f} {b[4]:.4f}\n")
        print(f"Saved {len(items)} samples to {split_name} split.")

    # Remove stale YOLO .cache files so Ultralytics rescans the dataset
    for split_name in ["train", "val", "test"]:
        cache_path = os.path.join(DATASET_DIR, "labels", f"{split_name}.cache")
        if os.path.exists(cache_path):
            os.remove(cache_path)
            print(f"Removed cache: {cache_path}")

    print("=== Dataset expansion and balancing complete! ===")

if __name__ == '__main__':
    main()
