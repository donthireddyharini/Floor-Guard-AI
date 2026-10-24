#!/usr/bin/env python3
"""
Floor Guard AI — Phase 2 Dataset & Split Pipeline Test Suite
Tests validation logic, coordinate verification, empty label handling,
leakage prevention, and manifest accuracy using isolated synthetic fixtures.
"""

import os
import sys
import json
import tempfile
import unittest
from PIL import Image

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from ml.dataset_validator import validate_box_line, validate_label_file, validate_dataset_directory
from ml.split_dataset import generate_splits

class TestDatasetPipeline(unittest.TestCase):

    def test_01_valid_yolo_syntax(self):
        """Test standard valid YOLO bounding box line."""
        valid, res = validate_box_line("0 0.500000 0.500000 0.200000 0.300000", 1, "test.txt")
        self.assertTrue(valid)
        self.assertEqual(res["class_id"], 0)
        self.assertEqual(res["class_name"], "water_spill")
        self.assertEqual(res["x_center"], 0.5)
        self.assertEqual(res["width"], 0.2)

    def test_02_invalid_token_count_rejection(self):
        """Reject lines with fewer or more than 5 tokens."""
        # 4 tokens
        valid, err = validate_box_line("0 0.5 0.5 0.2", 1, "test.txt")
        self.assertFalse(valid)
        self.assertIn("Expected 5 tokens", err)

        # 6 tokens
        valid, err = validate_box_line("0 0.5 0.5 0.2 0.3 0.99", 1, "test.txt")
        self.assertFalse(valid)
        self.assertIn("Expected 5 tokens", err)

        # Non-numeric
        valid, err = validate_box_line("water 0.5 0.5 0.2 0.3", 1, "test.txt")
        self.assertFalse(valid)
        self.assertIn("Invalid non-integer class ID", err)

    def test_03_invalid_class_id_rejection(self):
        """Reject class IDs outside the 4 supported hazard categories (0..3)."""
        valid, err = validate_box_line("99 0.5 0.5 0.2 0.3", 1, "test.txt")
        self.assertFalse(valid)
        self.assertIn("Class ID 99 outside valid range", err)

        valid, err = validate_box_line("-1 0.5 0.5 0.2 0.3", 1, "test.txt")
        self.assertFalse(valid)
        self.assertIn("Class ID -1 outside valid range", err)

    def test_04_coordinate_bounds_and_zero_area(self):
        """Reject out-of-bounds coordinates, zero-area, and negative-sized boxes."""
        # x_center > 1.0
        valid, err = validate_box_line("0 1.5 0.5 0.2 0.3", 1, "test.txt")
        self.assertFalse(valid)
        self.assertIn("out of range", err)

        # zero width
        valid, err = validate_box_line("0 0.5 0.5 0.0 0.3", 1, "test.txt")
        self.assertFalse(valid)
        self.assertIn("width 0.0 must be in", err)

        # negative height
        valid, err = validate_box_line("0 0.5 0.5 0.2 -0.1", 1, "test.txt")
        self.assertFalse(valid)
        self.assertIn("height -0.1 must be in", err)

        # box boundary extends outside image (x_center=0.1, width=0.5 -> xmin = -0.15)
        valid, err = validate_box_line("0 0.1 0.5 0.5 0.3", 1, "test.txt")
        self.assertFalse(valid)
        self.assertIn("extends beyond image bounds", err)

    def test_05_clean_floor_negative_sample_handling(self):
        """Empty label file must be validated as a legitimate background negative sample."""
        with tempfile.TemporaryDirectory() as td:
            lbl_file = os.path.join(td, "clean_floor_001.txt")
            with open(lbl_file, 'w', encoding='utf-8') as f:
                pass  # 0 bytes

            res = validate_label_file(lbl_file)
            self.assertTrue(res["valid"])
            self.assertTrue(res["is_negative_sample"])
            self.assertEqual(len(res["boxes"]), 0)
            self.assertEqual(len(res["errors"]), 0)

    def test_06_image_label_pairing_and_orphaning(self):
        """Detect missing labels and orphaned labels in dataset directory."""
        with tempfile.TemporaryDirectory() as td:
            img_dir = os.path.join(td, "images")
            lbl_dir = os.path.join(td, "labels")
            os.makedirs(img_dir)
            os.makedirs(lbl_dir)

            # Create synthetic test images (fixtures only)
            im1 = Image.new("RGB", (100, 100), color="blue")
            im1.save(os.path.join(img_dir, "sample_a.jpg"))

            im2 = Image.new("RGB", (100, 100), color="red")
            im2.save(os.path.join(img_dir, "sample_b.jpg"))

            # Label only for sample_a
            with open(os.path.join(lbl_dir, "sample_a.txt"), "w") as f:
                f.write("0 0.5 0.5 0.2 0.2\n")

            # Orphaned label without image
            with open(os.path.join(lbl_dir, "orphan_x.txt"), "w") as f:
                f.write("3 0.4 0.4 0.1 0.1\n")

            rep = validate_dataset_directory(img_dir, lbl_dir)
            self.assertIn("sample_b.jpg", rep["missing_labels"])
            self.assertIn("orphan_x.txt", rep["orphaned_labels"])
            self.assertEqual(rep["paired_samples"], 1)
            self.assertEqual(rep["class_box_counts"]["water_spill"], 1)

    def test_07_duplicate_image_detection(self):
        """Identify duplicate images using SHA-256 hash matching."""
        with tempfile.TemporaryDirectory() as td:
            img_dir = os.path.join(td, "images")
            lbl_dir = os.path.join(td, "labels")
            os.makedirs(img_dir)
            os.makedirs(lbl_dir)

            im = Image.new("RGB", (80, 80), color="green")
            im.save(os.path.join(img_dir, "original.jpg"))
            im.save(os.path.join(img_dir, "copy1.jpg"))
            im.save(os.path.join(img_dir, "copy2.jpg"))

            rep = validate_dataset_directory(img_dir, lbl_dir)
            self.assertEqual(len(rep["duplicate_image_groups"]), 1)
            self.assertEqual(len(rep["duplicate_image_groups"][0]["files"]), 3)

    def test_08_split_reproducibility(self):
        """Fixed random seed must yield identical train/val/test splits."""
        rep1 = generate_splits(seed=42, dry_run=True)
        rep2 = generate_splits(seed=42, dry_run=True)
        self.assertEqual(rep1["total_images"], rep2["total_images"])
        self.assertEqual(rep1["splits_statistics"], rep2["splits_statistics"])
        self.assertEqual(rep1["data_leakage_detected"], rep2["data_leakage_detected"])

    def test_09_split_leakage_prevention(self):
        """Ensure duplicate image clusters never cross-contaminate across train/val/test splits."""
        rep = generate_splits(seed=42, dry_run=True)
        self.assertFalse(rep["data_leakage_detected"])
        self.assertEqual(rep["leakage_details"]["train_val_overlap"], 0)
        self.assertEqual(rep["leakage_details"]["train_test_overlap"], 0)
        self.assertEqual(rep["leakage_details"]["val_test_overlap"], 0)

    def test_10_manifest_accuracy(self):
        """Manifest counts must match physical reality on disk."""
        manifest_path = os.path.join(BASE_DIR, "data", "dataset_manifest.json")
        self.assertTrue(os.path.exists(manifest_path))
        with open(manifest_path, "r", encoding="utf-8") as f:
            m = json.load(f)

        self.assertIn(m["manifest_version"], ["2.0-verified", "2.1-phase3a", "2.2-phase3b", "2.3-phase3c", "2.4-phase4.1"])
        processed_dir = os.path.join(BASE_DIR, "data", "processed", "images")
        actual_processed = len([f for f in os.listdir(processed_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))]) if os.path.exists(processed_dir) else 0
        self.assertEqual(m["local_verified_inventory"]["processed_pool_images"], actual_processed)

if __name__ == '__main__':
    unittest.main()
