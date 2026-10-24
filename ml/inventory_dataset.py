#!/usr/bin/env python3
"""
Floor Guard AI — Phase 2 Dataset & Image Forensic Inventory
Scans workspace image assets, detects duplicates, verifies integrity, and outputs structured metadata.
"""

import os
import sys
import json
import hashlib
from PIL import Image

def scan_images(workspace_dir):
    valid_exts = {'.jpg', '.jpeg', '.png', '.webp', '.bmp'}
    ignore_dirs = {'node_modules', '.git', 'backups', 'dist', '.system_generated'}

    records = []
    for root, dirs, files in os.walk(workspace_dir):
        # Filter out ignored directories
        dirs[:] = [d for d in dirs if d not in ignore_dirs and not d.startswith('.')]
        for f in files:
            ext = os.path.splitext(f)[1].lower()
            if ext in valid_exts:
                full_path = os.path.join(root, f)
                rel_path = os.path.relpath(full_path, workspace_dir).replace('\\', '/')
                size = os.path.getsize(full_path)

                with open(full_path, 'rb') as fp:
                    sha256 = hashlib.sha256(fp.read()).hexdigest()

                readable = False
                dims = [0, 0]
                img_format = None
                mode = None
                error_msg = None

                try:
                    with Image.open(full_path) as im:
                        im.verify()
                    with Image.open(full_path) as im:
                        dims = list(im.size)
                        img_format = im.format
                        mode = im.mode
                    readable = True
                except Exception as e:
                    error_msg = str(e)

                records.append({
                    "relative_path": rel_path,
                    "filename": f,
                    "size_bytes": size,
                    "sha256": sha256,
                    "readable": readable,
                    "dimensions": {"width": dims[0], "height": dims[1]},
                    "format": img_format,
                    "color_mode": mode,
                    "error": error_msg
                })

    # Group by SHA-256 for duplicate detection
    by_hash = {}
    for r in records:
        by_hash.setdefault(r["sha256"], []).append(r)

    unique_assets = []
    for h, copies in by_hash.items():
        primary = copies[0]
        all_paths = [c["relative_path"] for c in copies]
        unique_assets.append({
            "sha256": h,
            "primary_path": primary["relative_path"],
            "copy_count": len(copies),
            "copies": all_paths,
            "dimensions": primary["dimensions"],
            "format": primary["format"],
            "size_bytes": primary["size_bytes"],
            "readable": primary["readable"]
        })

    summary = {
        "total_image_files": len(records),
        "total_unique_images": len(unique_assets),
        "total_readable_images": sum(1 for r in records if r["readable"]),
        "total_corrupted_images": sum(1 for r in records if not r["readable"]),
        "total_zero_byte_images": sum(1 for r in records if r["size_bytes"] == 0),
        "duplicate_groups": sum(1 for u in unique_assets if u["copy_count"] > 1),
        "unique_assets": unique_assets,
        "all_files": records
    }
    return summary

if __name__ == '__main__':
    target_dir = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    report = scan_images(target_dir)
    print(json.dumps(summary := {k: v for k, v in report.items() if k != 'all_files'}, indent=2))
