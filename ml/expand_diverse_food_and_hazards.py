#!/usr/bin/env python3
"""
Floor Guard AI — Phase 3 & 4: Diverse Food Waste & Multi-Hazard Dataset Synthesis & Ingestion
Generates realistic, diverse food waste (rice, bread crumbs, fruit scraps, vegetable waste,
spilled sauces, food residue) and tightly bounded hazard instances across varied floor substrates
(white ceramic tile, dark marble, hardwood, warehouse concrete) with precise bounding boxes
and hard-negative controls (reflections, shadows, empty plates, caution signs without spills).
"""

import os
import sys
import math
import random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET_DIR = os.path.join(BASE_DIR, 'dataset')
IMG_DIR = os.path.join(DATASET_DIR, 'images')
LBL_DIR = os.path.join(DATASET_DIR, 'labels')

# Canonical Class IDs
# 0: water_spill
# 1: oil_spill
# 2: chemical_spill
# 3: broken_glass
# 4: cable_cord
# 5: obstacle_debris
# 6: trash_litter
# 7: food_waste
# 8: mud_dirt
# 9: stairs_hazard

def create_floor_background(floor_type, width=640, height=640):
    """Generates authentic realistic floor textures."""
    img = Image.new('RGB', (width, height))
    draw = ImageDraw.Draw(img)

    if floor_type == 'white_tile':
        # White/cream tiles with grout lines and slight specular reflection
        base_color = (235, 238, 240)
        draw.rectangle([0, 0, width, height], fill=base_color)
        tile_w, tile_h = 160, 160
        for x in range(0, width, tile_w):
            draw.line([(x, 0), (x, height)], fill=(185, 190, 195), width=2)
        for y in range(0, height, tile_h):
            draw.line([(0, y), (width, y)], fill=(185, 190, 195), width=2)
        # Add subtle overhead light glare
        glare = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        gdraw = ImageDraw.Draw(glare)
        gdraw.ellipse([width*0.3, height*0.2, width*0.7, height*0.4], fill=(255, 255, 255, 45))
        glare = glare.filter(ImageFilter.GaussianBlur(radius=25))
        img.paste(glare, (0, 0), glare)

    elif floor_type == 'dark_marble':
        # Dark charcoal/black marble with fine veins
        draw.rectangle([0, 0, width, height], fill=(32, 34, 38))
        for _ in range(8):
            pts = [(random.randint(0, width), random.randint(0, height)) for _ in range(5)]
            pts.sort(key=lambda p: p[0])
            draw.line(pts, fill=(65, 70, 78), width=1)
        # Specular glint
        glint = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        gdraw = ImageDraw.Draw(glint)
        gdraw.ellipse([width*0.5, height*0.6, width*0.8, height*0.8], fill=(255, 255, 255, 30))
        glint = glint.filter(ImageFilter.GaussianBlur(radius=20))
        img.paste(glint, (0, 0), glint)

    elif floor_type == 'wood_plank':
        # Warm oak/walnut wood planks
        draw.rectangle([0, 0, width, height], fill=(168, 122, 85))
        plank_h = 80
        for y in range(0, height, plank_h):
            draw.line([(0, y), (width, y)], fill=(110, 75, 48), width=2)
            # Wood grain noise
            for x in range(0, width, 40):
                draw.line([(x, y+2), (x+random.randint(20, 60), y+plank_h-2)], fill=(150, 105, 70), width=1)

    elif floor_type == 'concrete':
        # Industrial warehouse grey concrete with subtle texture
        draw.rectangle([0, 0, width, height], fill=(145, 148, 150))
        # Specks and pores
        for _ in range(300):
            rx, ry = random.randint(0, width-1), random.randint(0, height-1)
            draw.point((rx, ry), fill=(115, 118, 120))
        for _ in range(200):
            rx, ry = random.randint(0, width-1), random.randint(0, height-1)
            draw.point((rx, ry), fill=(175, 178, 180))

    return img

def render_food_waste(img, food_type, cx, cy, scale=1.0):
    """
    Renders realistic food waste instances tightly:
    - scattered_rice
    - bread_crust
    - fruit_scraps (banana peel / apple core)
    - vegetable_waste (lettuce / carrot trimmings)
    - spilled_sauce (curry / tomato sauce splatters)
    - mixed_crumbs
    Returns: list of exact normalized bounding boxes [class_id, xc, yc, w, h]
    """
    W, H = img.size
    boxes = []
    overlay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    if food_type == 'scattered_rice':
        # Multiple small white grains scattered in a cluster
        min_x, min_y, max_x, max_y = W, H, 0, 0
        num_grains = random.randint(18, 35)
        for _ in range(num_grains):
            gx = cx + int(random.gauss(0, 35 * scale))
            gy = cy + int(random.gauss(0, 30 * scale))
            gw, gh = random.randint(3, 6), random.randint(7, 12)
            angle = random.randint(0, 180)
            # Grain shadow
            draw.ellipse([gx-gw-1, gy-gh-1, gx+gw+1, gy+gh+1], fill=(40, 40, 40, 60))
            # Grain body
            draw.ellipse([gx-gw, gy-gh, gx+gw, gy+gh], fill=(245, 248, 245, 240))
            min_x = min(min_x, gx - gw - 2)
            min_y = min(min_y, gy - gh - 2)
            max_x = max(max_x, gx + gw + 2)
            max_y = max(max_y, gy + gh + 2)

        min_x = max(0, min_x)
        min_y = max(0, min_y)
        max_x = min(W, max_x)
        max_y = min(H, max_y)
        bw = max_x - min_x
        bh = max_y - min_y
        boxes.append([7, (min_x + bw/2)/W, (min_y + bh/2)/H, bw/W, bh/H])

    elif food_type == 'bread_crust':
        # Dropped slice of crusty bread and surrounding crumbs
        bw, bh = int(65 * scale), int(45 * scale)
        x1, y1 = cx - bw//2, cy - bh//2
        x2, y2 = cx + bw//2, cy + bh//2
        # Soft shadow
        draw.ellipse([x1-4, y1+4, x2+6, y2+8], fill=(30, 25, 20, 80))
        # Golden brown crust
        draw.chord([x1, y1, x2, y2], 0, 360, fill=(195, 140, 75, 245), outline=(130, 85, 35, 255))
        # Crumb texture
        for _ in range(12):
            draw.point((random.randint(x1+5, x2-5), random.randint(y1+5, y2-5)), fill=(230, 190, 130, 255))
        # Crumbs scattered nearby
        for _ in range(8):
            c_x = cx + random.randint(-bw, bw)
            c_y = cy + random.randint(-bh, bh)
            draw.ellipse([c_x-2, c_y-2, c_x+2, c_y+2], fill=(200, 150, 80, 230))

        min_x = max(0, x1 - 8)
        min_y = max(0, y1 - 8)
        max_x = min(W, x2 + 8)
        max_y = min(H, y2 + 8)
        boxes.append([7, (min_x + (max_x-min_x)/2)/W, (min_y + (max_y-min_y)/2)/H, (max_x-min_x)/W, (max_y-min_y)/H])

    elif food_type == 'fruit_scraps':
        # Banana peel: 3 curved yellow/brown strips radiating from a center
        min_x, min_y, max_x, max_y = W, H, 0, 0
        # Shadow
        draw.ellipse([cx-45*scale, cy-25*scale, cx+50*scale, cy+35*scale], fill=(25, 20, 15, 75))
        # Peel segments
        peel_pts = [
            [(cx, cy), (cx+int(40*scale), cy-int(30*scale)), (cx+int(60*scale), cy-int(20*scale)), (cx+int(25*scale), cy+int(5*scale))],
            [(cx, cy), (cx-int(50*scale), cy-int(10*scale)), (cx-int(70*scale), cy+int(15*scale)), (cx-int(20*scale), cy+int(20*scale))],
            [(cx, cy), (cx+int(10*scale), cy+int(45*scale)), (cx+int(25*scale), cy+int(60*scale)), (cx-int(5*scale), cy+int(35*scale))]
        ]
        for poly in peel_pts:
            draw.polygon(poly, fill=(235, 205, 50, 240), outline=(140, 100, 20, 255))
            for pt in poly:
                min_x = min(min_x, pt[0])
                min_y = min(min_y, pt[1])
                max_x = max(max_x, pt[0])
                max_y = max(max_y, pt[1])
        # Dark tip
        draw.ellipse([cx-int(8*scale), cy-int(8*scale), cx+int(8*scale), cy+int(8*scale)], fill=(75, 45, 20, 255))

        min_x = max(0, int(min_x - 5))
        min_y = max(0, int(min_y - 5))
        max_x = min(W, int(max_x + 5))
        max_y = min(H, int(max_y + 5))
        bw = max_x - min_x
        bh = max_y - min_y
        boxes.append([7, (min_x + bw/2)/W, (min_y + bh/2)/H, bw/W, bh/H])

    elif food_type == 'spilled_sauce':
        # Puddle of red tomato sauce or curry with splatters
        color = random.choice([
            (190, 40, 30, 225),   # Red marinara / ketchup
            (210, 140, 25, 220),  # Yellow curry / mustard
            (140, 50, 25, 230)    # Brown gravy / barbecue
        ])
        min_x, min_y, max_x, max_y = W, H, 0, 0
        rad = int(35 * scale)
        # Main pool
        draw.ellipse([cx-rad, cy-int(rad*0.7), cx+rad, cy+int(rad*0.7)], fill=color)
        # Droplets / splatters radiating out
        for _ in range(9):
            ang = random.uniform(0, 2*math.pi)
            dist = random.uniform(rad*0.8, rad*1.6)
            sx = int(cx + math.cos(ang) * dist)
            sy = int(cy + math.sin(ang) * dist * 0.7)
            s_rad = random.randint(2, 6)
            draw.ellipse([sx-s_rad, sy-s_rad, sx+s_rad, sy+s_rad], fill=color)
            min_x = min(min_x, sx-s_rad)
            min_y = min(min_y, sy-s_rad)
            max_x = max(max_x, sx+s_rad)
            max_y = max(max_y, sy+s_rad)

        min_x = max(0, min(min_x, cx-rad-3))
        min_y = max(0, min(min_y, cy-int(rad*0.7)-3))
        max_x = min(W, max(max_x, cx+rad+3))
        max_y = min(H, max(max_y, cy+int(rad*0.7)+3))
        bw = max_x - min_x
        bh = max_y - min_y
        boxes.append([7, (min_x + bw/2)/W, (min_y + bh/2)/H, bw/W, bh/H])

    elif food_type == 'vegetable_waste':
        # Green salad leaves / tomato slice / onion trimmings
        min_x, min_y, max_x, max_y = W, H, 0, 0
        # Dropped lettuce leaf
        draw.polygon([
            (cx-int(30*scale), cy),
            (cx-int(15*scale), cy-int(25*scale)),
            (cx+int(25*scale), cy-int(20*scale)),
            (cx+int(35*scale), cy+int(15*scale)),
            (cx, cy+int(20*scale))
        ], fill=(70, 160, 50, 235), outline=(45, 110, 30, 255))
        # Sliced tomato piece
        tx, ty = cx + int(25*scale), cy + int(15*scale)
        draw.ellipse([tx-int(12*scale), ty-int(12*scale), tx+int(12*scale), ty+int(12*scale)], fill=(215, 45, 35, 240))

        min_x = max(0, cx - int(35*scale))
        min_y = max(0, cy - int(30*scale))
        max_x = min(W, cx + int(45*scale))
        max_y = min(H, cy + int(32*scale))
        bw = max_x - min_x
        bh = max_y - min_y
        boxes.append([7, (min_x + bw/2)/W, (min_y + bh/2)/H, bw/W, bh/H])

    img.paste(overlay, (0, 0), overlay)
    return boxes

def render_cable(img, cx, cy, scale=1.0):
    """Renders a realistic electrical cord crossing floor with tight bounding box."""
    W, H = img.size
    overlay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    pts = []
    x_curr = max(20, cx - int(140 * scale))
    y_curr = cy + random.randint(-20, 20)
    pts.append((x_curr, y_curr))
    for i in range(5):
        x_curr += int(55 * scale)
        y_curr += random.randint(-25, 25)
        pts.append((min(W-20, x_curr), max(20, min(H-20, y_curr))))

    # Cable drop shadow
    shadow_pts = [(p[0]+2, p[1]+3) for p in pts]
    draw.line(shadow_pts, fill=(20, 20, 20, 80), width=6)
    # Cable body (black or bright yellow extension cord)
    color = random.choice([(35, 38, 42, 255), (235, 195, 30, 255), (210, 80, 40, 255)])
    draw.line(pts, fill=color, width=4)

    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    min_x, max_x = max(0, min(xs)-4), min(W, max(xs)+4)
    min_y, max_y = max(0, min(ys)-4), min(H, max(ys)+4)
    bw, bh = max_x - min_x, max_y - min_y

    img.paste(overlay, (0, 0), overlay)
    return [[4, (min_x + bw/2)/W, (min_y + bh/2)/H, bw/W, bh/H]]

def render_hard_negative(img, neg_type):
    """
    Renders authentic negative control elements on clean floors (0 hazard boxes):
    - clean_plates: Clean empty dinner plate on floor (should NOT be detected as food waste)
    - caution_cone: Yellow wet floor cone on dry clean floor (should NOT be water spill)
    - window_shadow: Strong diagonal geometric window shadow
    - tile_specular: High contrast light glare reflection
    """
    W, H = img.size
    draw = ImageDraw.Draw(img)

    if neg_type == 'clean_plate':
        # White ceramic plate with blue rim, completely empty and clean
        cx, cy = W//2, H//2
        r = 55
        draw.ellipse([cx-r-2, cy-r+4, cx+r+2, cy+r+8], fill=(30, 30, 30, 60)) # shadow
        draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=(245, 245, 248), outline=(60, 110, 180), width=3)
        draw.ellipse([cx-r+15, cy-r+15, cx+r-15, cy+r-15], fill=(255, 255, 255), outline=(210, 215, 220), width=1)

    elif neg_type == 'caution_cone':
        # Yellow safety cone on clean dry floor
        cx, cy = W//2, H//2
        # Drop shadow
        draw.ellipse([cx-40, cy+35, cx+40, cy+50], fill=(25, 25, 25, 75))
        # Cone triangle
        draw.polygon([(cx, cy-70), (cx-35, cy+40), (cx+35, cy+40)], fill=(245, 200, 20), outline=(180, 140, 10))
        # Wet floor symbol / black silhouette on cone
        draw.rectangle([cx-15, cy-10, cx+15, cy+15], fill=(25, 25, 25))

    elif neg_type == 'window_shadow':
        # Diagonal dark shadow bands simulating sun through window blinds
        overlay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        odraw = ImageDraw.Draw(overlay)
        for offset in range(-100, W+100, 80):
            odraw.polygon([(offset, 0), (offset+35, 0), (offset+155, H), (offset+120, H)], fill=(0, 0, 0, 55))
        img.paste(overlay, (0, 0), overlay)

    elif neg_type == 'tile_specular':
        # Glaring bright specular reflection from ceiling lamps
        glare = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        gdraw = ImageDraw.Draw(glare)
        gdraw.ellipse([W*0.2, H*0.3, W*0.5, H*0.5], fill=(255, 255, 255, 80))
        gdraw.ellipse([W*0.6, H*0.6, W*0.85, H*0.75], fill=(255, 255, 255, 70))
        glare = glare.filter(ImageFilter.GaussianBlur(radius=15))
        img.paste(glare, (0, 0), glare)

    return [] # Zero bounding boxes for hard negative controls

def main():
    print("=" * 65)
    print("FLOOR GUARD AI — EXPANDING DIVERSE FOOD WASTE & HAZARD DATASET")
    print("=" * 65)

    random.seed(42)
    np.random.seed(42)

    floor_types = ['white_tile', 'dark_marble', 'wood_plank', 'concrete']
    food_varieties = [
        'scattered_rice', 'bread_crust', 'fruit_scraps',
        'spilled_sauce', 'vegetable_waste'
    ]

    splits = {
        'train': 48,  # 48 diverse food waste + cables + hard negatives
        'val': 16,    # 16 validation instances
        'test': 16    # 16 test benchmark instances
    }

    generated_counts = {'food_waste': 0, 'cable_cord': 0, 'clean_hard_negative': 0}

    for split, count in splits.items():
        s_img_dir = os.path.join(IMG_DIR, split)
        s_lbl_dir = os.path.join(LBL_DIR, split)
        os.makedirs(s_img_dir, exist_ok=True)
        os.makedirs(s_lbl_dir, exist_ok=True)

        for i in range(count):
            ft = random.choice(floor_types)
            img = create_floor_background(ft)

            boxes = []
            category_mode = random.choices(
                ['food_single', 'food_multi', 'cable', 'hard_negative'],
                weights=[0.45, 0.25, 0.15, 0.15]
            )[0]

            if category_mode == 'food_single':
                fv = random.choice(food_varieties)
                cx, cy = random.randint(180, 460), random.randint(180, 460)
                scale = random.uniform(0.8, 1.3)
                b = render_food_waste(img, fv, cx, cy, scale)
                boxes.extend(b)
                generated_counts['food_waste'] += len(b)
                fname = f"synth_div_food_{ft}_{fv}_{split}_{i:03d}"

            elif category_mode == 'food_multi':
                # Multiple scattered food items (e.g. rice + sauce splatter)
                fv1 = random.choice(food_varieties)
                fv2 = random.choice(food_varieties)
                cx1, cy1 = random.randint(150, 300), random.randint(180, 460)
                cx2, cy2 = random.randint(340, 490), random.randint(180, 460)
                b1 = render_food_waste(img, fv1, cx1, cy1, scale=0.85)
                b2 = render_food_waste(img, fv2, cx2, cy2, scale=0.85)
                boxes.extend(b1 + b2)
                generated_counts['food_waste'] += len(b1) + len(b2)
                fname = f"synth_multi_food_{ft}_{split}_{i:03d}"

            elif category_mode == 'cable':
                cx, cy = random.randint(200, 440), random.randint(200, 440)
                scale = random.uniform(0.9, 1.3)
                b = render_cable(img, cx, cy, scale)
                boxes.extend(b)
                generated_counts['cable_cord'] += len(b)
                fname = f"synth_cable_{ft}_{split}_{i:03d}"

            else:
                # Hard negative control
                nt = random.choice(['clean_plate', 'caution_cone', 'window_shadow', 'tile_specular'])
                render_hard_negative(img, nt)
                generated_counts['clean_hard_negative'] += 1
                fname = f"synth_neg_clean_{ft}_{nt}_{split}_{i:03d}"

            # Save JPEG image
            img_path = os.path.join(s_img_dir, f"{fname}.jpg")
            img.save(img_path, 'JPEG', quality=95)

            # Save YOLO txt label
            lbl_path = os.path.join(s_lbl_dir, f"{fname}.txt")
            with open(lbl_path, 'w', encoding='utf-8') as lf:
                for box in boxes:
                    cid, xc, yc, bw, bh = box
                    lf.write(f"{cid} {xc:.6f} {yc:.6f} {bw:.6f} {bh:.6f}\n")

    print("\nDataset expansion complete:")
    print(f"  Food waste boxes generated: {generated_counts['food_waste']}")
    print(f"  Cable cord boxes generated: {generated_counts['cable_cord']}")
    print(f"  Clean hard-negative controls: {generated_counts['clean_hard_negative']}")

if __name__ == '__main__':
    main()
