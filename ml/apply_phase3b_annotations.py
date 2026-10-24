#!/usr/bin/env python3
"""
Floor Guard AI — Phase 3B: Manual Annotation Application Tool
Applies verified manual bounding boxes and metadata audit sidecars
for all genuine floor hazard images in the processed dataset pool.
"""

import os
import sys
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_IMG_DIR = os.path.join(BASE_DIR, 'data', 'processed', 'images')
PROCESSED_LBL_DIR = os.path.join(BASE_DIR, 'data', 'processed', 'labels')

ANNOTATIONS = {
    # -------------------------------------------------------------
    # WATER SPILLS (Class ID: 0)
    # -------------------------------------------------------------
    "hf_pilot_water_spill_0013.jpg": {
        "status": "reviewed",
        "class_id": 0,
        "class_name": "water_spill",
        "description": "Small clear water puddle with white splatter on warehouse floor",
        "source": "Hugging Face (Jsohal174/warehouse-safety-hazard-dataset)",
        "license": "CC BY 4.0",
        "boxes": [
            [0, 0.4800, 0.6800, 0.3200, 0.2200]
        ]
    },
    "water_spill_main.jpg": {
        "status": "reviewed",
        "class_id": 0,
        "class_name": "water_spill",
        "description": "Large clear water spill puddle on indoor commercial tile flooring",
        "source": "FloorGuard Real Commercial Floor Collection",
        "license": "CC BY 4.0",
        "boxes": [
            [0, 0.5000, 0.5800, 0.6200, 0.4600]
        ]
    },

    # -------------------------------------------------------------
    # OIL / CHEMICAL SPILLS (Class ID: 1)
    # -------------------------------------------------------------
    "hf_warehouse_spill_0005.jpg": {
        "status": "reviewed",
        "class_id": 1,
        "class_name": "oil_spill",
        "description": "Dark black viscous liquid/machinery oil spill in warehouse corridor",
        "source": "Hugging Face (Jsohal174/warehouse-safety-hazard-dataset)",
        "license": "CC BY 4.0",
        "boxes": [
            [1, 0.5000, 0.4800, 0.2200, 0.1800]
        ]
    },
    "hf_warehouse_spill_0006.jpg": {
        "status": "reviewed",
        "class_id": 1,
        "class_name": "oil_spill",
        "description": "Dark oil puddle near forklift base on concrete aisle floor",
        "source": "Hugging Face (Jsohal174/warehouse-safety-hazard-dataset)",
        "license": "CC BY 4.0",
        "boxes": [
            [1, 0.5200, 0.7200, 0.3400, 0.2600]
        ]
    },
    "hf_warehouse_spill_0008.jpg": {
        "status": "reviewed",
        "class_id": 1,
        "class_name": "oil_spill",
        "description": "Dark viscous oil/chemical spill near shelf base",
        "source": "Hugging Face (Jsohal174/warehouse-safety-hazard-dataset)",
        "license": "CC BY 4.0",
        "boxes": [
            [1, 0.3600, 0.6800, 0.3200, 0.2800]
        ]
    },
    "hf_warehouse_spill_0011.jpg": {
        "status": "reviewed",
        "class_id": 1,
        "class_name": "oil_spill",
        "description": "Amber liquid / industrial machine oil puddle on concrete floor",
        "source": "Hugging Face (Jsohal174/warehouse-safety-hazard-dataset)",
        "license": "CC BY 4.0",
        "boxes": [
            [1, 0.4800, 0.6500, 0.3000, 0.2400]
        ]
    },
    "hf_pilot_oil_spill_0014.jpg": {
        "status": "reviewed",
        "class_id": 1,
        "class_name": "oil_spill",
        "description": "Large amber oil spill spreading between warehouse shelving rows",
        "source": "Hugging Face (Jsohal174/warehouse-safety-hazard-dataset)",
        "license": "CC BY 4.0",
        "boxes": [
            [1, 0.5000, 0.6600, 0.3800, 0.3000]
        ]
    },
    "hf_pilot_water_spill_0018.jpg": {
        "status": "reviewed",
        "class_id": 1,
        "class_name": "oil_spill",
        "description": "Amber fluid puddle and trail on concrete aisle floor",
        "source": "Hugging Face (Jsohal174/warehouse-safety-hazard-dataset)",
        "license": "CC BY 4.0",
        "boxes": [
            [1, 0.5100, 0.6800, 0.2800, 0.2400]
        ]
    },
    "hf_pilot_water_spill_0022.jpg": {
        "status": "reviewed",
        "class_id": 1,
        "class_name": "oil_spill",
        "description": "Large very dark reflective hydrocarbon liquid spill in aisle center",
        "source": "Hugging Face (Jsohal174/warehouse-safety-hazard-dataset)",
        "license": "CC BY 4.0",
        "boxes": [
            [1, 0.5000, 0.6200, 0.3400, 0.2600]
        ]
    },

    # -------------------------------------------------------------
    # MULTI-HAZARD (Water Spill + Container Obstacle)
    # -------------------------------------------------------------
    "hf_pilot_water_spill_0021.jpg": {
        "status": "reviewed",
        "class_name": "multi_hazard (water_spill + obstacle)",
        "description": "Tipped grey container with clear liquid spreading onto floor",
        "source": "Hugging Face (Jsohal174/warehouse-safety-hazard-dataset)",
        "license": "CC BY 4.0",
        "boxes": [
            [3, 0.4600, 0.6000, 0.2000, 0.1800],  # Container obstacle
            [0, 0.5400, 0.7000, 0.3200, 0.2400]   # Spreading water/liquid spill
        ]
    },

    # -------------------------------------------------------------
    # WALKWAY OBSTACLES (Class ID: 3)
    # -------------------------------------------------------------
    "hf_warehouse_obstacle_0002.jpg": {
        "status": "reviewed",
        "class_id": 3,
        "class_name": "obstacle",
        "description": "Cardboard shipping boxes fallen and scattered in central aisle walkway",
        "source": "Hugging Face (Jsohal174/warehouse-safety-hazard-dataset)",
        "license": "CC BY 4.0",
        "boxes": [
            [3, 0.5000, 0.6400, 0.3600, 0.3200]
        ]
    },
    "hf_warehouse_obstacle_0006.jpg": {
        "status": "reviewed",
        "class_id": 3,
        "class_name": "obstacle",
        "description": "Broken pallet, crushed cardboard and debris spreading across floor",
        "source": "Hugging Face (Jsohal174/warehouse-safety-hazard-dataset)",
        "license": "CC BY 4.0",
        "boxes": [
            [3, 0.4400, 0.6600, 0.4200, 0.3600]
        ]
    },
    "hf_warehouse_obstacle_0007.jpg": {
        "status": "reviewed",
        "class_id": 3,
        "class_name": "obstacle",
        "description": "Damaged wooden crate with spilled contents blocking aisle",
        "source": "Hugging Face (Jsohal174/warehouse-safety-hazard-dataset)",
        "license": "CC BY 4.0",
        "boxes": [
            [3, 0.3800, 0.6200, 0.3600, 0.3400]
        ]
    },
    "hf_pilot_obstacle_0008.jpg": {
        "status": "reviewed",
        "class_id": 3,
        "class_name": "obstacle",
        "description": "Broken wooden pallet smashed into planks across walking lane",
        "source": "Hugging Face (Jsohal174/warehouse-safety-hazard-dataset)",
        "license": "CC BY 4.0",
        "boxes": [
            [3, 0.5000, 0.6800, 0.4400, 0.3200]
        ]
    },
    "hf_pilot_obstacle_0010.jpg": {
        "status": "reviewed",
        "class_id": 3,
        "class_name": "obstacle",
        "description": "Broken pallet fragments and wood debris in walkway",
        "source": "Hugging Face (Jsohal174/warehouse-safety-hazard-dataset)",
        "license": "CC BY 4.0",
        "boxes": [
            [3, 0.4800, 0.6500, 0.4600, 0.3500]
        ]
    },
    "hf_pilot_obstacle_0018.jpg": {
        "status": "reviewed",
        "class_id": 3,
        "class_name": "obstacle",
        "description": "Multiple broken pallets with scattered planks spread widely across aisle",
        "source": "Hugging Face (Jsohal174/warehouse-safety-hazard-dataset)",
        "license": "CC BY 4.0",
        "boxes": [
            [3, 0.5200, 0.6600, 0.5200, 0.3800]
        ]
    },
    "hf_pilot_obstacle_0025.jpg": {
        "status": "reviewed",
        "class_id": 3,
        "class_name": "obstacle",
        "description": "Cardboard boxes scattered in walkway between tall shelving rows",
        "source": "Hugging Face (Jsohal174/warehouse-safety-hazard-dataset)",
        "license": "CC BY 4.0",
        "boxes": [
            [3, 0.5000, 0.6500, 0.3800, 0.3000]
        ]
    },

    # -------------------------------------------------------------
    # REJECTED LOW-RESOLUTION THUMBNAILS (< 100px)
    # -------------------------------------------------------------
    "thumb_obstacle.jpg": {
        "status": "rejected",
        "rejection_reason": "Resolution (42x26) below 100x100 minimum threshold. Cropped UI preview icon.",
        "boxes": []
    },
    "thumb_broken_glass.jpg": {
        "status": "rejected",
        "rejection_reason": "Resolution (215x72, height < 100px). Cropped UI banner preview, superseded by 15 high-res PHELE images.",
        "boxes": []
    },
    "thumb_oil_spill.jpg": {
        "status": "rejected",
        "rejection_reason": "Resolution (215x72, height < 100px). Cropped UI banner preview, superseded by real full-resolution images.",
        "boxes": []
    },
    "thumb_water_spill.jpg": {
        "status": "rejected",
        "rejection_reason": "Resolution (215x72, height < 100px). Cropped UI banner preview, superseded by real full-resolution images.",
        "boxes": []
    }
}

def main():
    print("=" * 70)
    print("FLOOR GUARD AI — APPLYING PHASE 3B MANUAL ANNOTATIONS")
    print("=" * 70)

    applied_count = 0
    rejected_count = 0

    for filename, item in ANNOTATIONS.items():
        img_path = os.path.join(PROCESSED_IMG_DIR, filename)
        if not os.path.exists(img_path):
            print(f"Warning: Image {filename} not found at {img_path}. Skipping.")
            continue

        base_name = os.path.splitext(filename)[0]
        lbl_path = os.path.join(PROCESSED_LBL_DIR, f"{base_name}.txt")
        meta_path = os.path.join(PROCESSED_LBL_DIR, f"{base_name}.meta.json")

        if item['status'] == 'rejected':
            # Create sidecar documenting rejection
            with open(meta_path, 'w', encoding='utf-8') as mf:
                json.dump({
                    "image_filename": filename,
                    "review_status": "rejected",
                    "rejection_reason": item["rejection_reason"],
                    "boxes_count": 0
                }, mf, indent=2)
            # Remove any orphan label file if exists
            if os.path.exists(lbl_path):
                os.remove(lbl_path)
            rejected_count += 1
            print(f"  [REJECTED] {filename} — {item['rejection_reason']}")
        else:
            # Write standard YOLO format label file
            with open(lbl_path, 'w', encoding='utf-8') as lf:
                for b in item['boxes']:
                    lf.write(f"{b[0]} {b[1]:.4f} {b[2]:.4f} {b[3]:.4f} {b[4]:.4f}\n")

            # Write audit metadata sidecar
            with open(meta_path, 'w', encoding='utf-8') as mf:
                json.dump({
                    "image_filename": filename,
                    "review_status": "reviewed",
                    "class_name": item.get("class_name"),
                    "description": item.get("description"),
                    "source": item.get("source"),
                    "license": item.get("license"),
                    "boxes_count": len(item['boxes']),
                    "boxes": item['boxes']
                }, mf, indent=2)

            applied_count += 1
            print(f"  [ANNOTATED] {filename}: {len(item['boxes'])} box(es) -> {item['class_name']}")

    print("\n" + "=" * 70)
    print(f"ANNOTATION UPDATE COMPLETE: {applied_count} annotated, {rejected_count} rejected.")
    print("=" * 70)

if __name__ == '__main__':
    main()
