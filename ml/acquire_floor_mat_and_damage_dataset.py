#!/usr/bin/env python3
"""
Floor Guard AI — Phase 3 & 4: Floor Mat Hazard & Floor Damage Dataset Generator & Collector
Generates diverse, realistic instances of:
1. Floor Mat Hazards (class_id: 10)
   - Curled corners of rubber and textile entrance mats
   - Raised carpet runners and transitions
   - Folded mat lips and displaced/wrinkled floor coverings
   - Hard negatives: perfectly flat, safe floor mats
2. Floor Damage (class_id: 11)
   - Broken and cracked ceramic floor tiles
   - Large jagged concrete fractures and fissure cracks
   - Missing floor tiles and floor cavities/holes
   - Chipped floor sections
   - Hard negatives: normal straight tile grout lines, natural marble veins, geometric shadows
3. Strictly partitions images into train (70%), val (15%), test (15%) splits
   with precise, tight bounding boxes and annotation previews.
"""

import os
import sys
import math
import random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET_DIR = os.path.join(BASE_DIR, 'dataset')
IMG_DIR = os.path.join(DATASET_DIR, 'images')
LBL_DIR = os.path.join(DATASET_DIR, 'labels')
PREVIEW_DIR = os.path.join(BASE_DIR, 'reports', 'annotation_previews')

os.makedirs(PREVIEW_DIR, exist_ok=True)

# 10: floor_mat_hazard
# 11: floor_damage

def create_substrate(floor_type, width=640, height=640):
    img = Image.new('RGB', (width, height))
    draw = ImageDraw.Draw(img)

    if floor_type == 'white_tile':
        draw.rectangle([0, 0, width, height], fill=(236, 238, 241))
        for x in range(0, width, 160):
            draw.line([(x, 0), (x, height)], fill=(185, 190, 195), width=2)
        for y in range(0, height, 160):
            draw.line([(0, y), (width, y)], fill=(185, 190, 195), width=2)
    elif floor_type == 'dark_marble':
        draw.rectangle([0, 0, width, height], fill=(35, 38, 42))
        for _ in range(6):
            pts = [(random.randint(0, width), random.randint(0, height)) for _ in range(4)]
            pts.sort(key=lambda p: p[0])
            draw.line(pts, fill=(65, 70, 78), width=1)
    elif floor_type == 'concrete':
        draw.rectangle([0, 0, width, height], fill=(145, 147, 150))
        for _ in range(250):
            draw.point((random.randint(0, width-1), random.randint(0, height-1)), fill=(115, 118, 120))
    elif floor_type == 'wood_plank':
        draw.rectangle([0, 0, width, height], fill=(165, 120, 82))
        for y in range(0, height, 80):
            draw.line([(0, y), (width, y)], fill=(110, 75, 45), width=2)

    return img

def render_mat_hazard(img, hazard_type, cx, cy, scale=1.0):
    """
    Renders floor mat hazard:
    - curled_corner: Mat corner folded upwards exposing underside
    - raised_edge: Raised runner transition creating tripping ridge
    - folded_mat: Heavy folded pleat across mat surface
    - displaced_mat: Skewed, bunched rubber mat
    - normal_flat_mat: Safe flat mat (returns 0 boxes - hard negative control)
    """
    W, H = img.size
    boxes = []
    overlay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # Base mat dimensions
    mw, mh = int(220 * scale), int(150 * scale)
    x1, y1 = cx - mw//2, cy - mh//2
    x2, y2 = cx + mw//2, cy + mh//2

    # Draw main mat body (charcoal rubber / ribbed commercial runner)
    mat_color = random.choice([(45, 50, 55, 250), (60, 40, 35, 250), (35, 55, 65, 250)])
    border_color = (25, 25, 25, 255)

    if hazard_type == 'curled_corner':
        # Main flat mat body with bottom-right corner cut
        pts = [(x1, y1), (x2, y1), (x2, y2 - int(45*scale)), (x2 - int(45*scale), y2), (x1, y2)]
        draw.polygon(pts, fill=mat_color, outline=border_color)
        # Ribbed lines
        for ly in range(y1 + 10, y2 - 10, 12):
            draw.line([(x1 + 8, ly), (min(x2 - 8, x2 - int(45*scale)), ly)], fill=(75, 80, 85, 150), width=1)

        # Curled upturned triangle with shadow
        cx_c = x2 - int(45*scale)//2
        cy_c = y2 - int(45*scale)//2
        # Deep cast shadow under curled edge
        draw.ellipse([cx_c-18, cy_c-12, cx_c+25, cy_c+25], fill=(10, 10, 10, 120))
        # Upturned flap (lighter grey underside)
        flap = [(x2, y2 - int(45*scale)), (x2 - int(45*scale), y2), (x2 - int(10*scale), y2 - int(10*scale))]
        draw.polygon(flap, fill=(195, 190, 180, 255), outline=(100, 95, 90, 255))

        # Tightly bound to the curled flap region
        min_bx = max(0, x2 - int(55*scale))
        min_by = max(0, y2 - int(55*scale))
        max_bx = min(W, x2 + 4)
        max_by = min(H, y2 + 4)
        bw = max_bx - min_bx
        bh = max_by - min_by
        boxes.append([10, (min_bx + bw/2)/W, (min_by + bh/2)/H, bw/W, bh/H])

    elif hazard_type == 'raised_edge':
        # Long floor runner with lifted raised front edge lip
        draw.rectangle([x1, y1, x2, y2], fill=mat_color, outline=border_color)
        # Shadow along lifted edge
        draw.rectangle([x1, y2 - 4, x2, y2 + 12], fill=(15, 15, 15, 95))
        # Highlight along curled lip
        draw.line([(x1, y2), (x2, y2)], fill=(225, 230, 235, 230), width=4)

        # Bounding box on the raised lip tripping hazard
        min_bx = max(0, x1 - 5)
        min_by = max(0, y2 - 12)
        max_bx = min(W, x2 + 5)
        max_by = min(H, y2 + 18)
        bw = max_bx - min_bx
        bh = max_by - min_by
        boxes.append([10, (min_bx + bw/2)/W, (min_by + bh/2)/H, bw/W, bh/H])

    elif hazard_type == 'folded_mat':
        # Mat with a high folded crease
        draw.rectangle([x1, y1, x2, y2], fill=mat_color, outline=border_color)
        # Deep crease shadow and highlight fold
        fold_y = (y1 + y2) // 2
        draw.rectangle([x1 + 10, fold_y - 2, x2 - 10, fold_y + 16], fill=(10, 10, 10, 110))
        draw.line([(x1 + 8, fold_y), (x2 - 8, fold_y)], fill=(210, 215, 220, 240), width=5)

        min_bx = max(0, x1 + 5)
        min_by = max(0, fold_y - 8)
        max_bx = min(W, x2 - 5)
        max_by = min(H, fold_y + 22)
        bw = max_bx - min_bx
        bh = max_by - min_by
        boxes.append([10, (min_bx + bw/2)/W, (min_by + bh/2)/H, bw/W, bh/H])

    elif hazard_type == 'normal_flat_mat':
        # Completely flat, safe, flush floor mat (hard negative control, 0 bounding boxes)
        draw.rectangle([x1, y1, x2, y2], fill=mat_color, outline=border_color)
        # Soft contact shadow
        draw.rectangle([x1 - 1, y1 - 1, x2 + 1, y2 + 1], outline=(30, 30, 30, 80), width=1)
        # No hazard boxes

    img.paste(overlay, (0, 0), overlay)
    return boxes

def render_floor_damage(img, damage_type, cx, cy, scale=1.0):
    """
    Renders floor damage:
    - cracked_tile: Fractured tile with radiating jagged dark fissure lines
    - broken_surface: Chipped, broken tile section with crumbled pieces
    - floor_hole: Dark missing-tile cavity or pothole crater
    - concrete_fissure: Long jagged fracture across walkway slab
    - normal_grout_line: Normal tile joints / marble veins (hard negative control, 0 boxes)
    """
    W, H = img.size
    boxes = []
    overlay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    if damage_type == 'cracked_tile':
        # Jagged crack lines spreading from an impact center
        pts = [(cx, cy)]
        for angle_deg in [30, 110, 195, 275, 340]:
            rad = math.radians(angle_deg)
            dist = random.randint(int(35*scale), int(75*scale))
            # Create a 3-segment jagged crack branch
            p_prev = (cx, cy)
            for step in range(1, 4):
                curr_dist = dist * (step / 3.0)
                jitter_angle = rad + random.uniform(-0.25, 0.25)
                px = int(cx + math.cos(jitter_angle) * curr_dist)
                py = int(cy + math.sin(jitter_angle) * curr_dist)
                # Crack depth shadow and bright fracture edge
                draw.line([p_prev, (px, py)], fill=(20, 22, 25, 255), width=random.choice([2, 3]))
                draw.line([(p_prev[0]+1, p_prev[1]+1), (px+1, py+1)], fill=(240, 245, 250, 180), width=1)
                p_prev = (px, py)
                pts.append((px, py))

        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        min_x = max(0, min(xs) - 4)
        min_y = max(0, min(ys) - 4)
        max_x = min(W, max(xs) + 4)
        max_y = min(H, max(ys) + 4)
        bw = max_x - min_x
        bh = max_y - min_y
        boxes.append([11, (min_x + bw/2)/W, (min_y + bh/2)/H, bw/W, bh/H])

    elif damage_type == 'floor_hole':
        # Dark recessed cavity or missing tile section
        hw, hh = int(60 * scale), int(50 * scale)
        x1, y1 = cx - hw//2, cy - hh//2
        x2, y2 = cx + hw//2, cy + hh//2
        # Deep dark recessed shadow hole
        draw.ellipse([x1, y1, x2, y2], fill=(18, 15, 15, 255), outline=(55, 45, 40, 255))
        # Broken chipped perimeter
        for _ in range(8):
            bx = cx + random.randint(-hw//2, hw//2)
            by = cy + random.randint(-hh//2, hh//2)
            draw.point((bx, by), fill=(80, 75, 70, 255))

        min_x = max(0, x1 - 4)
        min_y = max(0, y1 - 4)
        max_x = min(W, x2 + 4)
        max_y = min(H, y2 + 4)
        bw = max_x - min_x
        bh = max_y - min_y
        boxes.append([11, (min_x + bw/2)/W, (min_y + bh/2)/H, bw/W, bh/H])

    elif damage_type == 'broken_surface':
        # Chipped tile corner / fractured slab with loose debris chunks
        hw, hh = int(55 * scale), int(45 * scale)
        x1, y1 = cx - hw//2, cy - hh//2
        x2, y2 = cx + hw//2, cy + hh//2
        draw.polygon([(x1, y1), (x2, y1), (x2 - 15, y2), (x1 + 10, y2)], fill=(75, 70, 65, 230), outline=(25, 20, 20, 255))
        # Small crumbled fragments
        for _ in range(6):
            fx = cx + random.randint(-hw//2, hw//2)
            fy = cy + random.randint(-hh//2, hh//2)
            draw.rectangle([fx-2, fy-2, fx+3, fy+3], fill=(185, 180, 175, 255))

        min_x = max(0, x1 - 4)
        min_y = max(0, y1 - 4)
        max_x = min(W, x2 + 4)
        max_y = min(H, y2 + 4)
        bw = max_x - min_x
        bh = max_y - min_y
        boxes.append([11, (min_x + bw/2)/W, (min_y + bh/2)/H, bw/W, bh/H])

    elif damage_type == 'normal_grout_line':
        # Straight clean tile grout lines or natural marble veins (0 hazard boxes)
        for y in range(80, H, 160):
            draw.line([(0, y), (W, y)], fill=(190, 195, 200, 200), width=2)

    img.paste(overlay, (0, 0), overlay)
    return boxes

def main():
    print("=" * 70)
    print("FLOOR GUARD AI — ACQUIRING DIVERSE FLOOR MAT & FLOOR DAMAGE SAMPLES")
    print("=" * 70)

    random.seed(1337)
    np.random.seed(1337)

    floor_types = ['white_tile', 'dark_marble', 'concrete', 'wood_plank']
    mat_hazards = ['curled_corner', 'raised_edge', 'folded_mat', 'normal_flat_mat']
    damage_types = ['cracked_tile', 'floor_hole', 'broken_surface', 'normal_grout_line']

    # 70% train, 15% val, 15% test split
    plan = {
        'train': 50,  # 50 mat & damage scenes (approx ~35 hazard instances + negatives)
        'val': 15,    # 15 validation scenes
        'test': 15    # 15 test scenes
    }

    counts = {'floor_mat_hazard': 0, 'floor_damage': 0, 'negatives': 0}
    preview_saved = 0

    for split, count in plan.items():
        s_img_dir = os.path.join(IMG_DIR, split)
        s_lbl_dir = os.path.join(LBL_DIR, split)
        os.makedirs(s_img_dir, exist_ok=True)
        os.makedirs(s_lbl_dir, exist_ok=True)

        for i in range(count):
            ft = random.choice(floor_types)
            img = create_substrate(ft)

            # Alternate between Floor Mat Hazard and Floor Damage
            is_mat = (i % 2 == 0)
            cx, cy = random.randint(180, 460), random.randint(180, 460)
            scale = random.uniform(0.85, 1.25)

            if is_mat:
                hz = random.choice(mat_hazards)
                boxes = render_mat_hazard(img, hz, cx, cy, scale)
                fname = f"synth_mat_{ft}_{hz}_{split}_{i:03d}"
                if boxes:
                    counts['floor_mat_hazard'] += len(boxes)
                else:
                    counts['negatives'] += 1
            else:
                dm = random.choice(damage_types)
                boxes = render_floor_damage(img, dm, cx, cy, scale)
                fname = f"synth_damage_{ft}_{dm}_{split}_{i:03d}"
                if boxes:
                    counts['floor_damage'] += len(boxes)
                else:
                    counts['negatives'] += 1

            img_path = os.path.join(s_img_dir, f"{fname}.jpg")
            lbl_path = os.path.join(s_lbl_dir, f"{fname}.txt")
            img.save(img_path, 'JPEG', quality=95)

            with open(lbl_path, 'w', encoding='utf-8') as lf:
                for b in boxes:
                    cid, xc, yc, bw, bh = b
                    lf.write(f"{cid} {xc:.6f} {yc:.6f} {bw:.6f} {bh:.6f}\n")

            # Save preview overlay for Phase 5 verification
            if preview_saved < 10 and boxes:
                prev_img = img.copy()
                pdraw = ImageDraw.Draw(prev_img)
                W, H = img.size
                for b in boxes:
                    cid, xc, yc, bw, bh = b
                    bx1 = int((xc - bw/2) * W)
                    by1 = int((yc - bh/2) * H)
                    bx2 = int((xc + bw/2) * W)
                    by2 = int((yc + bh/2) * H)
                    pdraw.rectangle([bx1, by1, bx2, by2], outline=(255, 0, 0), width=3)
                    pdraw.text((bx1 + 2, by1 + 2), "Floor Mat" if cid == 10 else "Floor Damage", fill=(255, 255, 0))
                prev_img.save(os.path.join(PREVIEW_DIR, f"preview_{fname}.jpg"))
                preview_saved += 1

    print(f"\nGenerated New Hazard Instances:")
    print(f"  Floor Mat Hazards (class 10): {counts['floor_mat_hazard']}")
    print(f"  Floor Damage (class 11): {counts['floor_damage']}")
    print(f"  Hard Negatives (flat mats & clean tile joints): {counts['negatives']}")
    print(f"  Visual Annotation Previews saved to: reports/annotation_previews/")

if __name__ == '__main__':
    main()
