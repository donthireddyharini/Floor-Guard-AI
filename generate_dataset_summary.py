import os
import glob
import json

BASE_DIR = r"c:\Users\donth_\Downloads\harry_client\floor-guard-ai"
dataset_dir = os.path.join(BASE_DIR, "dataset")

splits = ['train', 'val', 'test']
summary = {
    'total': {'images': 0, 'bounding_boxes': 0, 'boxes_per_class': {}},
    'train': {'images': 0, 'bounding_boxes': 0, 'boxes_per_class': {}},
    'val': {'images': 0, 'bounding_boxes': 0, 'boxes_per_class': {}},
    'test': {'images': 0, 'bounding_boxes': 0, 'boxes_per_class': {}}
}

class_names = {
    0: 'clean_floor',
    1: 'mat_hazard',
    2: 'floor_damage',
    3: 'water_spill',
    4: 'oil_spill',
    5: 'chemical_spill',
    6: 'broken_glass',
    7: 'cable_cord',
    8: 'obstacle_debris',
    9: 'trash_litter',
    10: 'food_waste',
    11: 'mud_dirt',
    12: 'stair_hazard'
}

for s in splits:
    img_dir = os.path.join(dataset_dir, 'images', s)
    lbl_dir = os.path.join(dataset_dir, 'labels', s)
    imgs = glob.glob(os.path.join(img_dir, "*.*"))
    summary[s]['images'] = len(imgs)
    summary['total']['images'] += len(imgs)

    boxes_cnt = 0
    for img_p in imgs:
        base = os.path.splitext(os.path.basename(img_p))[0]
        lbl_p = os.path.join(lbl_dir, base + ".txt")
        if os.path.exists(lbl_p):
            with open(lbl_p, 'r') as f:
                for line in f:
                    parts = line.strip().split()
                    if parts:
                        boxes_cnt += 1
                        cid = int(parts[0])
                        cname = class_names.get(cid, str(cid))
                        summary[s]['boxes_per_class'][cname] = summary[s]['boxes_per_class'].get(cname, 0) + 1
                        summary['total']['boxes_per_class'][cname] = summary['total']['boxes_per_class'].get(cname, 0) + 1
    summary[s]['bounding_boxes'] = boxes_cnt
    summary['total']['bounding_boxes'] += boxes_cnt

out_path = os.path.join(dataset_dir, 'dataset_summary.json')
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(summary, f, indent=2)

print(f"Generated {out_path}:")
print(json.dumps(summary, indent=2))
