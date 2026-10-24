#!/usr/bin/env python3
"""
Floor Guard AI — Phase 2 Dataset Validator
Performs strict, verifiable validation of YOLO format bounding box annotations,
image-label integrity, coordinate normalization, negative sample validity, and duplicate detection.

Validation Standards:
  - Format: Standard YOLO detection: <class_id> <x_center> <y_center> <width> <height>
  - Classes: 0: water_spill, 1: oil_spill, 2: broken_glass, 3: obstacle
  - Coordinates: Normalized floats in range [0.0, 1.0]
  - Negative samples: Validated clean floor images have empty (0-byte) label files
  - Parity: 1-to-1 pairing between image files and label text files
"""

import os
import sys
import json
import hashlib
from PIL import Image

CLASSES = {
    0: "water_spill",
    1: "oil_spill",
    2: "broken_glass",
    3: "obstacle"
}

EPSILON = 0.01  # Tolerance for floating-point boundary clipping

def validate_box_line(line, line_num, filename):
    """
    Validate a single line of a YOLO annotation file.
    Returns (is_valid, parsed_data_or_error_message).
    """
    tokens = line.strip().split()
    if not tokens:
        return True, None  # Empty lines ignored

    if len(tokens) != 5:
        return False, f"Line {line_num} in '{filename}': Expected 5 tokens, found {len(tokens)}: '{line.strip()}'"

    # 1. Parse class ID
    try:
        class_id = int(tokens[0])
    except ValueError:
        return False, f"Line {line_num} in '{filename}': Invalid non-integer class ID '{tokens[0]}'"

    if class_id not in CLASSES:
        return False, f"Line {line_num} in '{filename}': Class ID {class_id} outside valid range [0..{len(CLASSES)-1}] ({list(CLASSES.values())})"

    # 2. Parse coordinates
    try:
        xc = float(tokens[1])
        yc = float(tokens[2])
        w = float(tokens[3])
        h = float(tokens[4])
    except ValueError:
        return False, f"Line {line_num} in '{filename}': Coordinates contain non-float values"

    # 3. Check ranges
    if not (0.0 <= xc <= 1.0):
        return False, f"Line {line_num} in '{filename}': x_center {xc} out of range [0.0, 1.0]"
    if not (0.0 <= yc <= 1.0):
        return False, f"Line {line_num} in '{filename}': y_center {yc} out of range [0.0, 1.0]"
    if not (0.0 < w <= 1.0 + EPSILON):
        return False, f"Line {line_num} in '{filename}': width {w} must be in (0.0, 1.0]"
    if not (0.0 < h <= 1.0 + EPSILON):
        return False, f"Line {line_num} in '{filename}': height {h} must be in (0.0, 1.0]"

    # 4. Check boundaries
    xmin = xc - (w / 2.0)
    xmax = xc + (w / 2.0)
    ymin = yc - (h / 2.0)
    ymax = yc + (h / 2.0)

    if xmin < -EPSILON or xmax > 1.0 + EPSILON:
        return False, f"Line {line_num} in '{filename}': Box x-span [{xmin:.3f}, {xmax:.3f}] extends beyond image bounds"
    if ymin < -EPSILON or ymax > 1.0 + EPSILON:
        return False, f"Line {line_num} in '{filename}': Box y-span [{ymin:.3f}, {ymax:.3f}] extends beyond image bounds"

    return True, {
        "class_id": class_id,
        "class_name": CLASSES[class_id],
        "x_center": xc,
        "y_center": yc,
        "width": w,
        "height": h,
        "bbox_normalized": [round(xmin, 4), round(ymin, 4), round(xmax, 4), round(ymax, 4)]
    }

def validate_label_file(label_path):
    """
    Validate a YOLO label file.
    Returns {
        "valid": bool,
        "is_negative_sample": bool,
        "boxes": list,
        "errors": list
    }
    """
    if not os.path.exists(label_path):
        return {
            "valid": False,
            "is_negative_sample": False,
            "boxes": [],
            "errors": [f"Label file not found: {label_path}"]
        }

    with open(label_path, 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.strip().splitlines()
    if not lines or len(content.strip()) == 0:
        return {
            "valid": True,
            "is_negative_sample": True,
            "boxes": [],
            "errors": []
        }

    boxes = []
    errors = []
    fname = os.path.basename(label_path)

    for i, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        valid, result = validate_box_line(line, i, fname)
        if valid:
            if result:
                boxes.append(result)
        else:
            errors.append(result)

    return {
        "valid": len(errors) == 0,
        "is_negative_sample": len(boxes) == 0 and len(errors) == 0,
        "boxes": boxes,
        "errors": errors
    }

def validate_dataset_directory(images_dir, labels_dir):
    """
    Perform complete dataset validation over images and labels directories.
    """
    report = {
        "images_dir": images_dir,
        "labels_dir": labels_dir,
        "total_images": 0,
        "total_labels": 0,
        "paired_samples": 0,
        "missing_labels": [],
        "orphaned_labels": [],
        "corrupted_images": [],
        "invalid_label_files": [],
        "negative_background_samples": 0,
        "annotated_hazard_samples": 0,
        "total_bounding_boxes": 0,
        "class_box_counts": {name: 0 for name in CLASSES.values()},
        "duplicate_image_groups": [],
        "overall_status": "PENDING"
    }

    if not os.path.exists(images_dir):
        report["overall_status"] = f"ERROR: images_dir not found ({images_dir})"
        return report

    os.makedirs(labels_dir, exist_ok=True)

    valid_exts = {'.jpg', '.jpeg', '.png', '.webp', '.bmp'}
    image_files = {}
    image_hashes = {}

    for f in os.listdir(images_dir):
        ext = os.path.splitext(f)[1].lower()
        if ext in valid_exts:
            full_path = os.path.join(images_dir, f)
            stem = os.path.splitext(f)[0]
            image_files[stem] = full_path

            # Hash check
            with open(full_path, 'rb') as fp:
                h = hashlib.sha256(fp.read()).hexdigest()
            image_hashes.setdefault(h, []).append(f)

            # Check image readability
            try:
                with Image.open(full_path) as im:
                    im.verify()
            except Exception as e:
                report["corrupted_images"].append({"file": f, "error": str(e)})

    report["total_images"] = len(image_files)

    # Record duplicates
    for h, copies in image_hashes.items():
        if len(copies) > 1:
            report["duplicate_image_groups"].append({"sha256": h, "files": copies})

    # Read label files
    label_files = {}
    for f in os.listdir(labels_dir):
        if f.endswith('.txt'):
            full_path = os.path.join(labels_dir, f)
            stem = os.path.splitext(f)[0]
            label_files[stem] = full_path

    report["total_labels"] = len(label_files)

    # Check image -> label pairing
    for stem, img_path in image_files.items():
        if stem in label_files:
            report["paired_samples"] += 1
            lbl_res = validate_label_file(label_files[stem])
            if not lbl_res["valid"]:
                report["invalid_label_files"].append({
                    "file": os.path.basename(label_files[stem]),
                    "errors": lbl_res["errors"]
                })
            elif lbl_res["is_negative_sample"]:
                report["negative_background_samples"] += 1
            else:
                report["annotated_hazard_samples"] += 1
                report["total_bounding_boxes"] += len(lbl_res["boxes"])
                for b in lbl_res["boxes"]:
                    report["class_box_counts"][b["class_name"]] += 1
        else:
            report["missing_labels"].append(os.path.basename(img_path))

    # Check orphaned labels (label exists but no matching image)
    for stem, lbl_path in label_files.items():
        if stem not in image_files:
            report["orphaned_labels"].append(os.path.basename(lbl_path))

    has_errors = (
        len(report["missing_labels"]) > 0 or
        len(report["orphaned_labels"]) > 0 or
        len(report["corrupted_images"]) > 0 or
        len(report["invalid_label_files"]) > 0
    )

    report["overall_status"] = "PASSED" if not has_errors and report["total_images"] > 0 else (
        "WARNING: Incomplete or Discrepant" if report["total_images"] > 0 else "EMPTY"
    )
    return report

if __name__ == '__main__':
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    img_dir = os.path.join(base, 'data', 'processed', 'images')
    lbl_dir = os.path.join(base, 'data', 'processed', 'labels')

    res = validate_dataset_directory(img_dir, lbl_dir)
    print(json.dumps(res, indent=2))
