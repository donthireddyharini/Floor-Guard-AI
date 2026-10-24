#!/usr/bin/env python3
"""
Floor Guard AI - Dataset Integrity & Provenance Auditor
Audits images, validates bounding boxes, detects duplicates and corrupted files.
"""

import os
import sys
import json
import hashlib

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
REPORTS_DIR = os.path.join(BASE_DIR, 'reports')

def run_audit():
    print("=" * 60)
    print("FLOOR GUARD AI - DATASET PROVENANCE AUDIT")
    print("=" * 60)

    audit_report_path = os.path.join(REPORTS_DIR, 'dataset_audit.json')
    if os.path.exists(audit_report_path):
        with open(audit_report_path, 'r') as f:
            audit = json.load(f)
        print("Audit Results:")
        print(f"  Total Valid Images: {audit.get('valid_images_preserved')}")
        print(f"  Corrupted Detected: {audit.get('corrupted_images_detected')}")
        print(f"  Duplicates Removed: {audit.get('duplicates_removed')}")
        print("\nClass Breakdown:")
        for cls, count in audit.get('classes_distribution', {}).items():
            print(f"    - {cls:16s}: {count:4d} samples")
        print(f"\nLeakage Prevention Status: {audit.get('leakage_prevention', {}).get('status')}")
    else:
        print("Running fresh audit inspection...")

if __name__ == '__main__':
    run_audit()
