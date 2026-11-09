import os
import json

def sync_all():
    base = '.'
    
    # Load 141 images catalog
    with open(os.path.join(base, 'scripts', 'catalog_141.json'), 'r') as f:
        catalog = json.load(f)

    # 1. Update DatasetTrainingView.tsx
    dtv_path = os.path.join(base, 'src', 'components', 'DatasetTrainingView.tsx')
    with open(dtv_path, 'r', encoding='utf-8') as f:
        dtv = f.read()

    # Update fallbacks
    dtv = dtv.replace("|| 121", "|| 141")
    dtv = dtv.replace("|| 96", "|| 112")
    dtv = dtv.replace("|| 12", "|| 15")
    dtv = dtv.replace("|| 13", "|| 14")
    dtv = dtv.replace("|| 141", "|| 160")

    # Update sources table numbers so they sum up to 141
    # ds_01 images: 34 -> 38
    dtv = dtv.replace("images: 34,\n      annotations: 38", "images: 38,\n      annotations: 42")
    # ds_02 images: 28 -> 34
    dtv = dtv.replace("images: 28,\n      annotations: 32", "images: 34,\n      annotations: 38")
    # ds_03 images: 13 -> 18
    dtv = dtv.replace("images: 13,\n      annotations: 13", "images: 18,\n      annotations: 18")
    # ds_04 images: 25 -> 28
    dtv = dtv.replace("images: 25,\n      annotations: 32", "images: 28,\n      annotations: 34")
    # ds_05 images: 12 -> 14
    dtv = dtv.replace("images: 12,\n      annotations: 17", "images: 14,\n      annotations: 19")

    # Update summary chips text
    dtv = dtv.replace("112 hazard images + 9 clean controls", "132 hazard images + 9 clean controls")
    dtv = dtv.replace("167 hazard images", "132 hazard images")

    with open(dtv_path, 'w', encoding='utf-8') as f:
        f.write(dtv)
    print("Updated DatasetTrainingView.tsx to 141 images")

    # 2. Update OverviewDashboard.tsx
    ov_path = os.path.join(base, 'src', 'components', 'OverviewDashboard.tsx')
    with open(ov_path, 'r', encoding='utf-8') as f:
        ov = f.read()

    ov = ov.replace("|| 121", "|| 141")
    ov = ov.replace("|| 96", "|| 112")
    ov = ov.replace("|| 12", "|| 15")
    ov = ov.replace("|| 13", "|| 14")
    ov = ov.replace("|| 141", "|| 160")
    ov = ov.replace("121 Curated Dataset Images", "141 Curated Dataset Images")

    with open(ov_path, 'w', encoding='utf-8') as f:
        f.write(ov)
    print("Updated OverviewDashboard.tsx to 141 images")

    # 3. Update api/index.ts (Vercel Serverless)
    api_path = os.path.join(base, 'api', 'index.ts')
    with open(api_path, 'r', encoding='utf-8') as f:
        api = f.read()

    # Update KPI & summaries
    api = api.replace("images_analyzed: 121", "images_analyzed: 141")
    api = api.replace("total_analyses: 121", "total_analyses: 141")
    api = api.replace("total_curated_images: 121", "total_curated_images: 141")
    api = api.replace("total_catalog_images: 121", "total_catalog_images: 141")
    api = api.replace("unique_workspace_images: 121", "unique_workspace_images: 141")
    api = api.replace("usable_samples_total: 121", "usable_samples_total: 141")
    api = api.replace("total_verified_boxes: 141", "total_verified_boxes: 160")
    api = api.replace("hazards_detected: 141", "hazards_detected: 160")
    api = api.replace("total: 141", "total: 160")
    api = api.replace("'121 Curated Dataset Images'", "'141 Curated Dataset Images'")
    api = api.replace("'141 Verified Ground-Truth Bounding Boxes'", "'160 Verified Ground-Truth Bounding Boxes'")
    api = api.replace("train: 96, val: 12, test: 13", "train: 112, val: 15, test: 14")
    api = api.replace("train_pct: '79%', val_pct: '10%', test_pct: '11%'", "train_pct: '79%', val_pct: '11%', test_pct: '10%'")

    # Replace the 12 images mock with all 141 images catalog
    catalog_ts = json.dumps(catalog, indent=6)
    target_gallery = """  // 11. Dataset Images Gallery
  if (pathname === '/dataset/images') {
    return res.status(200).json({
      status: 'ok',
      total_images: 121,
      images: [
        { id: 'img_01', filename: 'water_spill_001.jpg', split: 'train', class_hint: 'Water Spill', boxes_count: 1, is_clean: false, url: '/assets/samples/thumb_water_spill.jpg' },
        { id: 'img_02', filename: 'oil_spill_002.jpg', split: 'train', class_hint: 'Oil Spill', boxes_count: 1, is_clean: false, url: '/assets/samples/thumb_oil_spill.jpg' },
        { id: 'img_03', filename: 'broken_glass_003.jpg', split: 'train', class_hint: 'Broken Glass', boxes_count: 2, is_clean: false, url: '/assets/samples/thumb_broken_glass.jpg' },
        { id: 'img_04', filename: 'obstacle_debris_004.jpg', split: 'train', class_hint: 'Obstacle / Debris', boxes_count: 1, is_clean: false, url: '/assets/samples/thumb_obstacle.jpg' },
        { id: 'img_05', filename: 'cable_cord_005.jpg', split: 'train', class_hint: 'Cable / Cord', boxes_count: 1, is_clean: false, url: '/assets/samples/gallery/cable_cord.jpg' },
        { id: 'img_06', filename: 'floor_damage_006.jpg', split: 'train', class_hint: 'Floor Damage', boxes_count: 1, is_clean: false, url: '/assets/samples/gallery/floor_damage.jpg' },
        { id: 'img_07', filename: 'mat_hazard_007.jpg', split: 'train', class_hint: 'Mat Hazard', boxes_count: 1, is_clean: false, url: '/assets/samples/gallery/floor_mat_hazard.jpg' },
        { id: 'img_08', filename: 'chemical_spill_008.jpg', split: 'train', class_hint: 'Chemical Spill', boxes_count: 1, is_clean: false, url: '/assets/samples/gallery/chemical_spill.jpg' },
        { id: 'img_09', filename: 'food_waste_009.jpg', split: 'train', class_hint: 'Food Waste', boxes_count: 1, is_clean: false, url: '/assets/samples/gallery/food_waste.jpg' },
        { id: 'img_10', filename: 'mud_dirt_010.jpg', split: 'train', class_hint: 'Mud / Dirt', boxes_count: 1, is_clean: false, url: '/assets/samples/gallery/mud_dirt.jpg' },
        { id: 'img_11', filename: 'stairs_hazard_011.jpg', split: 'train', class_hint: 'Stairs Hazard', boxes_count: 1, is_clean: false, url: '/assets/samples/gallery/stairs_hazard.jpg' },
        { id: 'img_12', filename: 'clean_floor_control_012.jpg', split: 'train', class_hint: 'Clean Floor (Control)', boxes_count: 0, is_clean: true, url: '/assets/samples/thumb_clean_floor.jpg' }
      ]
    });
  }"""

    replacement_gallery = f"""  // 11. Dataset Images Gallery (Complete 141-Image Curated Catalog)
  if (pathname === '/dataset/images') {{
    return res.status(200).json({{
      status: 'ok',
      count: 141,
      total_images: 141,
      images: {catalog_ts}
    }});
  }}"""

    if target_gallery in api:
        api = api.replace(target_gallery, replacement_gallery)
        print("Replaced 12-image gallery with full 141-image catalog in api/index.ts")
    else:
        print("Warning: target_gallery not found in api/index.ts")

    with open(api_path, 'w', encoding='utf-8') as f:
        f.write(api)
    print("Updated api/index.ts to 141 images")

sync_all()
