#!/usr/bin/env python3
"""
Floor Guard AI - Pipeline and Data Integrity Tests
Validates dataset manifest, schema, splits, and reports.
"""

import os
import sys
import json
import sqlite3

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def test_manifest_integrity():
    manifest_path = os.path.join(BASE_DIR, 'data', 'dataset_manifest.json')
    assert os.path.exists(manifest_path), "Dataset manifest must exist"
    with open(manifest_path) as f:
        m = json.load(f)
    assert len(m.get('sources', [])) >= 4, "Must have at least 4 candidate sources"
    assert "exclusions" in m, "Manifest must list excluded datasets"
    print("PASS: test_manifest_integrity")

def test_database_schema():
    db_path = os.path.join(BASE_DIR, 'data', 'database.sqlite')
    assert os.path.exists(db_path), "Database file must exist"
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [r[0] for r in cur.fetchall()]
    expected_tables = ['detection_runs', 'detections', 'dataset_sources', 'training_runs', 'model_registry', 'application_settings']
    for t in expected_tables:
        assert t in tables, f"Missing table {t}"
    conn.close()
    print("PASS: test_database_schema")

def test_reports_consistency():
    eval_rep = os.path.join(BASE_DIR, 'reports', 'evaluation_report.json')
    assert os.path.exists(eval_rep), "Evaluation report must exist"
    with open(eval_rep) as f:
        data = json.load(f)
    assert "overall_metrics" in data
    assert data["overall_metrics"]["mAP50_95"] > 0.80
    print("PASS: test_reports_consistency")

if __name__ == '__main__':
    test_manifest_integrity()
    test_database_schema()
    test_reports_consistency()
    print("ALL ML PIPELINE TESTS PASSED.")
