#!/usr/bin/env python3
"""
Floor Guard AI — Phase 1 & 5: Annotation Migration to 12 Hazard Classes
Migrates existing loose mat and floor crack annotations:
  - 'mat' / 'carpet' -> class 10 (floor_mat_hazard)
  - 'crack' / 'hole' / 'damage' -> class 11 (floor_damage)
Updates dataset/data.yaml to nc: 12.
"""

import os
import sys
import glob

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET_DIR = os.path.join(BASE_DIR, 'dataset')
LABELS_DIR = os.path.join(DATASET_DIR, 'labels')
DATA_YAML = os.path.join(DATASET_DIR, 'data.yaml')

CLASS_NAMES = [
    'water_spill',       # 0
    'oil_spill',         # 1
    'chemical_spill',    # 2
    'broken_glass',      # 3
    'cable_cord',        # 4
    'obstacle_debris',   # 5
    'trash_litter',      # 6
    'food_waste',        # 7
    'mud_dirt',          # 8
    'stairs_hazard',     # 9
    'floor_mat_hazard',  # 10
    'floor_damage'       # 11
]

def migrate_labels():
    print("=" * 70)
    print("FLOOR GUARD AI — MIGRATING ANNOTATIONS TO 12 HAZARD TAXONOMY")
    print("=" * 70)

    updated_mat = 0
    updated_damage = 0

    for split in ['train', 'val', 'test']:
        s_lbl = os.path.join(LABELS_DIR, split)
        for lf in glob.glob(os.path.join(s_lbl, "*.txt")):
            fname = os.path.basename(lf).lower()

            target_class = None
            if 'mat' in fname or 'carpet' in fname:
                if 'flat' not in fname:  # Do not convert flat mat negatives
                    target_class = 10
            elif 'crack' in fname or 'hole' in fname or 'damage' in fname:
                if 'grout' not in fname:  # Do not convert normal grout negatives
                    target_class = 11

            if target_class is None:
                continue

            with open(lf, 'r', encoding='utf-8') as f:
                lines = [l.strip() for l in f if l.strip()]

            new_lines = []
            for line in lines:
                parts = line.split()
                if len(parts) == 5:
                    cid = int(parts[0])
                    # If previously mapped to obstacle (5), update to specific hazard class
                    if cid in (5, target_class):
                        parts[0] = str(target_class)
                        if target_class == 10:
                            updated_mat += 1
                        else:
                            updated_damage += 1
                    new_lines.append(" ".join(parts))

            if new_lines:
                with open(lf, 'w', encoding='utf-8') as f:
                    f.write("\n".join(new_lines) + "\n")

    print(f"Migration completed:")
    print(f"  Floor mat hazard boxes updated: {updated_mat}")
    print(f"  Floor damage boxes updated: {updated_damage}")

    # Update dataset/data.yaml
    yaml_content = f"""path: {os.path.abspath(DATASET_DIR).replace('\\', '/')}
train: images/train
val: images/val
test: images/test

nc: 12
names:
  0: water_spill
  1: oil_spill
  2: chemical_spill
  3: broken_glass
  4: cable_cord
  5: obstacle_debris
  6: trash_litter
  7: food_waste
  8: mud_dirt
  9: stairs_hazard
  10: floor_mat_hazard
  11: floor_damage
"""
    with open(DATA_YAML, 'w', encoding='utf-8') as f:
        f.write(yaml_content)
    print(f"Updated {DATA_YAML} with nc: 12 and 12 canonical hazard classes.")

if __name__ == '__main__':
    migrate_labels()
