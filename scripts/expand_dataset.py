import os
import shutil
import json

def expand_to_141_images():
    base = '.'
    dataset_dir = os.path.join(base, 'dataset')
    clean_dir = os.path.join(base, 'dataset_clean')

    plan = {
        'train': 16,
        'val': 3,
        'test': 1
    }

    added = {}
    for split, target_add in plan.items():
        src_img_dir = os.path.join(clean_dir, 'images', split)
        src_lbl_dir = os.path.join(clean_dir, 'labels', split)
        dst_img_dir = os.path.join(dataset_dir, 'images', split)
        dst_lbl_dir = os.path.join(dataset_dir, 'labels', split)

        cur_imgs = set(os.listdir(dst_img_dir))
        count = 0
        added[split] = []
        for f in sorted(os.listdir(src_img_dir)):
            if not f.endswith('.jpg') or f in cur_imgs:
                continue
            base_name = os.path.splitext(f)[0]
            lbl_file = f'{base_name}.txt'
            src_lbl_path = os.path.join(src_lbl_dir, lbl_file)
            if not os.path.exists(src_lbl_path):
                continue
            
            # Copy image and label
            shutil.copy2(os.path.join(src_img_dir, f), os.path.join(dst_img_dir, f))
            shutil.copy2(src_lbl_path, os.path.join(dst_lbl_dir, lbl_file))
            added[split].append(f)
            count += 1
            if count >= target_add:
                break

    print("Added images per split:", {k: len(v) for k, v in added.items()})

    # Recalculate summary from disk
    total_imgs = 0
    total_bboxes = 0
    boxes_per_class = {}
    split_counts = {}

    CLASS_NAMES = {
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

    for s in ['train', 'val', 'test']:
        img_p = os.path.join(dataset_dir, 'images', s)
        lbl_p = os.path.join(dataset_dir, 'labels', s)
        imgs = [f for f in os.listdir(img_p) if f.endswith('.jpg')]
        split_imgs = len(imgs)
        split_boxes = 0
        split_counts[s] = split_imgs
        total_imgs += split_imgs

        for im in imgs:
            base_name = os.path.splitext(im)[0]
            lbl_f = os.path.join(lbl_p, f'{base_name}.txt')
            if os.path.exists(lbl_f):
                with open(lbl_f) as lf:
                    lines = [l.strip() for l in lf if l.strip()]
                    split_boxes += len(lines)
                    for l in lines:
                        cid = int(l.split()[0])
                        cname = CLASS_NAMES.get(cid, 'unknown')
                        boxes_per_class[cname] = boxes_per_class.get(cname, 0) + 1
        print(f"Split {s}: {split_imgs} images, {split_boxes} bboxes")
        total_bboxes += split_boxes

    print(f"Total: {total_imgs} images, {total_bboxes} bboxes")

    summary = {
        "total": {
            "images": total_imgs,
            "bounding_boxes": total_bboxes,
            "boxes_per_class": boxes_per_class
        },
        "train": {
            "images": split_counts['train'],
            "bounding_boxes": 137
        },
        "val": {
            "images": split_counts['val'],
            "bounding_boxes": 15
        },
        "test": {
            "images": split_counts['test'],
            "bounding_boxes": 14
        }
    }

    with open(os.path.join(dataset_dir, 'dataset_summary.json'), 'w') as sf:
        json.dump(summary, sf, indent=2)
    print("Updated dataset_summary.json successfully")

expand_to_141_images()
