#!/usr/bin/env python3
"""
Floor Guard AI — Phase 2 Annotation Management & Tooling Utility
Supports manual annotation, bounding-box validation, clean-floor negative labeling,
and annotation audit sidecar generation in standard YOLO format.

Standards & Conventions:
  - Classes:
      0: water_spill
      1: oil_spill
      2: broken_glass
      3: obstacle
  - Label format: <class_id> <x_center> <y_center> <width> <height> (normalized 0.0 - 1.0)
  - Negative samples (clean floor): empty (0-byte) text files.
  - Integrity: No automated model hallucination labeled as verified ground truth.
"""

import os
import sys
import json
import argparse
from datetime import datetime, timezone
from PIL import Image

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMAGES_DIR = os.path.join(BASE_DIR, 'data', 'processed', 'images')
LABELS_DIR = os.path.join(BASE_DIR, 'data', 'processed', 'labels')

CLASSES = {
    0: "water_spill",
    1: "oil_spill",
    2: "broken_glass",
    3: "obstacle"
}
CLASS_NAME_TO_ID = {v: k for k, v in CLASSES.items()}

def get_image_info(filename):
    """Retrieve absolute path, exists status, and dimensions."""
    stem = os.path.splitext(filename)[0]
    # Check in images dir
    candidate = os.path.join(IMAGES_DIR, filename)
    if not os.path.exists(candidate):
        # Try matching by stem with any image extension
        for ext in ['.jpg', '.jpeg', '.png', '.webp', '.bmp']:
            p = os.path.join(IMAGES_DIR, stem + ext)
            if os.path.exists(p):
                candidate = p
                filename = stem + ext
                break

    if not os.path.exists(candidate):
        return None, None, 0, 0

    try:
        with Image.open(candidate) as im:
            w, h = im.size
        return candidate, filename, w, h
    except Exception:
        return candidate, filename, 0, 0

def list_dataset(args):
    """List all dataset images and their current annotation status."""
    if not os.path.exists(IMAGES_DIR):
        print(f"Error: Images directory does not exist: {IMAGES_DIR}")
        return

    os.makedirs(LABELS_DIR, exist_ok=True)
    images = sorted(os.listdir(IMAGES_DIR))
    print("=" * 80)
    print(f"{'IMAGE FILENAME':<32} {'RESOLUTION':<12} {'STATUS':<20} {'BOXES':<6} {'CLASSES'}")
    print("=" * 80)

    for f in images:
        ext = os.path.splitext(f)[1].lower()
        if ext not in ['.jpg', '.jpeg', '.png', '.webp', '.bmp']:
            continue
        p = os.path.join(IMAGES_DIR, f)
        stem = os.path.splitext(f)[0]
        lbl_p = os.path.join(LABELS_DIR, stem + '.txt')

        try:
            with Image.open(p) as im:
                res_str = f"{im.size[0]}x{im.size[1]}"
        except Exception:
            res_str = "CORRUPT"

        if not os.path.exists(lbl_p):
            status = "UNANNOTATED"
            box_count = 0
            cls_str = "-"
        else:
            with open(lbl_p, 'r', encoding='utf-8') as lbf:
                lines = [l.strip() for l in lbf.readlines() if l.strip()]
            if len(lines) == 0:
                status = "CLEAN_FLOOR (NEG)"
                box_count = 0
                cls_str = "[Background Negative]"
            else:
                status = "LABELED"
                box_count = len(lines)
                class_names = []
                for l in lines:
                    tok = l.split()
                    if tok and tok[0].isdigit():
                        cid = int(tok[0])
                        class_names.append(CLASSES.get(cid, str(cid)))
                cls_str = ", ".join(sorted(set(class_names)))

        print(f"{f:<32} {res_str:<12} {status:<20} {box_count:<6} {cls_str}")
    print("=" * 80)

def show_image_annotations(args):
    """Show details and bounding boxes for a specific image."""
    img_path, filename, w, h = get_image_info(args.filename)
    if not img_path or not os.path.exists(img_path):
        print(f"Error: Image '{args.filename}' not found in {IMAGES_DIR}")
        return

    stem = os.path.splitext(filename)[0]
    lbl_p = os.path.join(LABELS_DIR, stem + '.txt')
    meta_p = os.path.join(LABELS_DIR, stem + '.meta.json')

    print(f"\n--- Annotation Details for: {filename} ---")
    print(f"Path: {img_path}")
    print(f"Resolution: {w} x {h}")

    if not os.path.exists(lbl_p):
        print("Status: UNANNOTATED (no label file on disk)")
        return

    with open(lbl_p, 'r', encoding='utf-8') as f:
        lines = [l.strip() for l in f.readlines() if l.strip()]

    meta = {}
    if os.path.exists(meta_p):
        try:
            with open(meta_p, 'r', encoding='utf-8') as mf:
                meta = json.load(mf)
        except Exception:
            pass

    if len(lines) == 0:
        print("Status: VERIFIED NEGATIVE SAMPLE (Clean Floor - 0 bounding boxes)")
        if meta:
            print(f"Annotator: {meta.get('annotator', 'N/A')} | Verified At: {meta.get('updated_at', 'N/A')}")
        return

    print(f"Status: LABELED ({len(lines)} bounding boxes)")
    if meta:
        print(f"Annotator: {meta.get('annotator', 'N/A')} | Verified At: {meta.get('updated_at', 'N/A')}")

    print("\nBounding Boxes:")
    for idx, l in enumerate(lines):
        toks = l.split()
        if len(toks) != 5:
            print(f"  [{idx}] INVALID LINE SYNTAX: {l}")
            continue
        cid = int(toks[0])
        xc, yc, bw, bh = float(toks[1]), float(toks[2]), float(toks[3]), float(toks[4])
        # Convert to pixel coords
        px1 = int((xc - bw/2) * w)
        py1 = int((yc - bh/2) * h)
        px2 = int((xc + bw/2) * w)
        py2 = int((yc + bh/2) * h)
        print(f"  [{idx}] Class: {CLASSES.get(cid, cid)} (ID {cid})")
        print(f"       Normalized: xc={xc:.4f}, yc={yc:.4f}, w={bw:.4f}, h={bh:.4f}")
        print(f"       Pixel Box:  [x1={px1}, y1={py1}, x2={px2}, y2={py2}] ({px2-px1}x{py2-py1} px)")

def add_box(args):
    """Add a validated bounding box to an image's label file."""
    img_path, filename, w, h = get_image_info(args.filename)
    if not img_path or not os.path.exists(img_path):
        print(f"Error: Image '{args.filename}' not found in {IMAGES_DIR}")
        return

    if w == 0 or h == 0:
        print(f"Error: Unable to read image dimensions for {filename}")
        return

    # Resolve class ID
    target_cls = args.class_name.lower().strip()
    if target_cls.isdigit():
        class_id = int(target_cls)
    elif target_cls in CLASS_NAME_TO_ID:
        class_id = CLASS_NAME_TO_ID[target_cls]
    else:
        print(f"Error: Unknown class '{args.class_name}'. Supported: {list(CLASS_NAME_TO_ID.keys())}")
        return

    if class_id not in CLASSES:
        print(f"Error: Class ID {class_id} outside valid range [0..{len(CLASSES)-1}]")
        return

    # Parse coordinates
    if args.format == 'pixel':
        x1, y1, x2, y2 = args.coords
        if x2 <= x1 or y2 <= y1:
            print("Error: Invalid pixel box: x2 must be > x1 and y2 must be > y1")
            return
        # Convert to normalized xc, yc, w, h
        bw = (x2 - x1) / w
        bh = (y2 - y1) / h
        xc = (x1 + x2) / (2.0 * w)
        yc = (y1 + y2) / (2.0 * h)
    else:
        xc, yc, bw, bh = args.coords

    # Range validation
    if not (0.0 <= xc <= 1.0 and 0.0 <= yc <= 1.0 and 0.0 < bw <= 1.0 and 0.0 < bh <= 1.0):
        print(f"Error: Normalized coords out of bounds: xc={xc}, yc={yc}, w={bw}, h={bh}")
        return

    xmin = xc - bw/2.0
    xmax = xc + bw/2.0
    ymin = yc - bh/2.0
    ymax = yc + bh/2.0

    if xmin < -0.01 or xmax > 1.01 or ymin < -0.01 or ymax > 1.01:
        print(f"Error: Box coordinates extend beyond image boundaries: [{xmin:.3f}, {ymin:.3f}, {xmax:.3f}, {ymax:.3f}]")
        return

    stem = os.path.splitext(filename)[0]
    os.makedirs(LABELS_DIR, exist_ok=True)
    lbl_p = os.path.join(LABELS_DIR, stem + '.txt')
    meta_p = os.path.join(LABELS_DIR, stem + '.meta.json')

    # Format YOLO line
    yolo_line = f"{class_id} {xc:.6f} {yc:.6f} {bw:.6f} {bh:.6f}\n"

    # Append to label file
    with open(lbl_p, 'a', encoding='utf-8') as f:
        f.write(yolo_line)

    # Write metadata sidecar
    now_iso = datetime.now(timezone.utc).isoformat()
    meta = {
        "image_file": filename,
        "label_file": stem + '.txt',
        "annotator": args.annotator or "manual_human_auditor",
        "verified_human_review": True,
        "is_negative_sample": False,
        "updated_at": now_iso
    }
    with open(meta_p, 'w', encoding='utf-8') as mf:
        json.dump(meta, mf, indent=2)

    print(f"Successfully added box for '{CLASSES[class_id]}' to {lbl_p}")
    print(f"  YOLO format: {yolo_line.strip()}")
    print(f"  Pixel dimensions: {w}x{h} -> [{int(xmin*w)}, {int(ymin*h)}, {int(xmax*w)}, {int(ymax*h)}]")

def mark_clean_floor(args):
    """Mark an image as a verified clean floor negative sample (empty label file)."""
    img_path, filename, w, h = get_image_info(args.filename)
    if not img_path or not os.path.exists(img_path):
        print(f"Error: Image '{args.filename}' not found in {IMAGES_DIR}")
        return

    stem = os.path.splitext(filename)[0]
    os.makedirs(LABELS_DIR, exist_ok=True)
    lbl_p = os.path.join(LABELS_DIR, stem + '.txt')
    meta_p = os.path.join(LABELS_DIR, stem + '.meta.json')

    # Overwrite label file as 0-byte empty file
    with open(lbl_p, 'w', encoding='utf-8') as f:
        pass  # 0 bytes

    now_iso = datetime.now(timezone.utc).isoformat()
    meta = {
        "image_file": filename,
        "label_file": stem + '.txt',
        "annotator": args.annotator or "manual_human_auditor",
        "verified_human_review": True,
        "is_negative_sample": True,
        "notes": "Verified dry clean floor surface without localized hazard bounding boxes.",
        "updated_at": now_iso
    }
    with open(meta_p, 'w', encoding='utf-8') as mf:
        json.dump(meta, mf, indent=2)

    print(f"Successfully marked '{filename}' as clean-floor negative sample (0-byte file: {lbl_p})")

def clear_annotations(args):
    """Clear all annotations for an image."""
    img_path, filename, w, h = get_image_info(args.filename)
    if not img_path:
        print(f"Error: Image '{args.filename}' not found")
        return

    stem = os.path.splitext(filename)[0]
    lbl_p = os.path.join(LABELS_DIR, stem + '.txt')
    meta_p = os.path.join(LABELS_DIR, stem + '.meta.json')

    if os.path.exists(lbl_p):
        os.remove(lbl_p)
    if os.path.exists(meta_p):
        os.remove(meta_p)
    print(f"Cleared all annotations for '{filename}'")

def main():
    parser = argparse.ArgumentParser(description="Floor Guard AI Dataset Annotation Tool")
    subparsers = parser.add_subparsers(dest="command")

    # list
    subparsers.add_parser("list", help="List all dataset images and their annotation status")

    # show
    p_show = subparsers.add_parser("show", help="Show annotations for a specific image")
    p_show.add_argument("filename", help="Image filename (e.g. sample_water_spill.jpg)")

    # add
    p_add = subparsers.add_parser("add", help="Add a bounding box to an image")
    p_add.add_argument("filename", help="Image filename")
    p_add.add_argument("class_name", help="Class name (water_spill, oil_spill, broken_glass, obstacle) or ID (0..3)")
    p_add.add_argument("coords", nargs=4, type=float, help="4 coordinates: xc yc w h (normalized) or x1 y1 x2 y2 (pixel)")
    p_add.add_argument("--format", choices=["normalized", "pixel"], default="normalized", help="Coordinate format")
    p_add.add_argument("--annotator", default="auditor", help="Annotator identifier")

    # mark-clean
    p_clean = subparsers.add_parser("mark-clean", help="Mark an image as clean floor negative sample")
    p_clean.add_argument("filename", help="Image filename")
    p_clean.add_argument("--annotator", default="auditor", help="Annotator identifier")

    # clear
    p_clear = subparsers.add_parser("clear", help="Clear annotations for an image")
    p_clear.add_argument("filename", help="Image filename")

    args = parser.parse_args()

    if args.command == "list":
        list_dataset(args)
    elif args.command == "show":
        show_image_annotations(args)
    elif args.command == "add":
        add_box(args)
    elif args.command == "mark-clean":
        mark_clean_floor(args)
    elif args.command == "clear":
        clear_annotations(args)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
