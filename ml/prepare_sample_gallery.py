#!/usr/bin/env python3
"""
Floor Guard AI - Prepares the permanent 11-category sample gallery
in public/assets/samples/gallery/ for direct interactive testing.
"""

import os
import shutil

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GALLERY_DIR = os.path.join(BASE_DIR, 'public', 'assets', 'samples', 'gallery')
os.makedirs(GALLERY_DIR, exist_ok=True)

# Sources for the 11 canonical sample images
SOURCE_MAP = {
    'water_spill.jpg': [
        os.path.join(BASE_DIR, 'public', 'assets', 'samples', 'sample_water_spill.jpg'),
        os.path.join(BASE_DIR, 'uploads', 'originals', 'sample_water_spill.jpg'),
        os.path.join(BASE_DIR, 'dataset', 'images', 'test', 'hf_pilot_water_spill_0013.jpg')
    ],
    'oil_spill.jpg': [
        os.path.join(BASE_DIR, 'public', 'assets', 'samples', 'thumb_oil_spill.jpg'),
        os.path.join(BASE_DIR, 'dataset', 'images', 'test', 'hf_pilot_oil_spill_0014.jpg')
    ],
    'chemical_spill.jpg': [
        os.path.join(BASE_DIR, 'dataset', 'images', 'test', 'floor_hazard_chemical_coolant_spill_aug4_contrast.jpg'),
        os.path.join(BASE_DIR, 'dataset', 'images', 'train', 'floor_hazard_chemical_coolant_spill_aug0_orig.jpg')
    ],
    'broken_glass.jpg': [
        os.path.join(BASE_DIR, 'public', 'assets', 'samples', 'thumb_broken_glass.jpg'),
        os.path.join(BASE_DIR, 'dataset', 'images', 'test', 'phele_glass_train_508.jpg'),
        os.path.join(BASE_DIR, 'dataset', 'images', 'test', 'floor_hazard_broken_glass_store_aug3_dim.jpg')
    ],
    'cable_cord.jpg': [
        os.path.join(BASE_DIR, 'dataset', 'images', 'test', 'floor_hazard_cable_cord_hallway_aug0_orig.jpg'),
        os.path.join(BASE_DIR, 'dataset', 'images', 'test', 'floor_hazard_cable_cord_hallway_aug4_contrast.jpg')
    ],
    'obstacle_debris.jpg': [
        os.path.join(BASE_DIR, 'public', 'assets', 'samples', 'thumb_obstacle.jpg'),
        os.path.join(BASE_DIR, 'dataset', 'images', 'test', 'hf_bal_obstacle_0043.jpg')
    ],
    'trash_litter.jpg': [
        os.path.join(BASE_DIR, 'dataset', 'images', 'test', 'clear_bottle_cap_angle_bright.jpg'),
        os.path.join(BASE_DIR, 'dataset', 'images', 'test', 'floor_hazard_plastic_bottle_rolling_aug4_contrast.jpg')
    ],
    'food_waste.jpg': [
        os.path.join(BASE_DIR, 'dataset', 'images', 'test', 'floor_hazard_food_waste_peel_aug4_contrast.jpg'),
        os.path.join(BASE_DIR, 'dataset', 'images', 'train', 'aug_food_sec05_bright.jpg')
    ],
    'mud_dirt.jpg': [
        os.path.join(BASE_DIR, 'dataset', 'images', 'test', 'floor_hazard_mud_tracks_soil_aug4_contrast.jpg'),
        os.path.join(BASE_DIR, 'dataset', 'images', 'train', 'floor_hazard_mud_tracks_soil_aug0_orig.jpg')
    ],
    'stairs_hazard.jpg': [
        os.path.join(BASE_DIR, 'dataset', 'images', 'test', 'floor_hazard_stairs_slip_hazard_aug4_contrast.jpg'),
        os.path.join(BASE_DIR, 'dataset', 'images', 'train', 'floor_hazard_stairs_slip_hazard_aug0_orig.jpg')
    ],
    'clean_floor.jpg': [
        os.path.join(BASE_DIR, 'public', 'assets', 'samples', 'thumb_clean_floor.jpg'),
        os.path.join(BASE_DIR, 'uploads', 'originals', 'thumb_clean_floor.jpg')
    ]
}

def setup_gallery():
    print("Setting up sample gallery for all 11 canonical categories...")
    for target_name, candidates in SOURCE_MAP.items():
        dst = os.path.join(GALLERY_DIR, target_name)
        copied = False
        for src in candidates:
            if os.path.exists(src):
                shutil.copy(src, dst)
                print(f"  Copied {os.path.basename(src)} -> {target_name}")
                copied = True
                break
        if not copied:
            print(f"  WARNING: No candidate source found for {target_name}")

    print("Sample gallery setup complete.")

if __name__ == '__main__':
    setup_gallery()
