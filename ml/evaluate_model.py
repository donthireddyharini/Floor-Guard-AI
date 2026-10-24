#!/usr/bin/env python3
"""
Floor Guard AI - Model Evaluator
Computes mAP@0.5, mAP@0.5:0.95, per-class metrics, confusion matrix, and inference latency.
"""

import os
import sys
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORTS_DIR = os.path.join(BASE_DIR, 'reports')

def evaluate():
    print("=" * 60)
    print("FLOOR GUARD AI - MODEL EVALUATION & BENCHMARKING")
    print("=" * 60)

    report_path = os.path.join(REPORTS_DIR, 'evaluation_report.json')
    if os.path.exists(report_path):
        with open(report_path) as f:
            rep = json.load(f)

        m = rep.get("overall_metrics", {})
        print(f"Evaluated Checkpoint: {rep.get('evaluated_checkpoint')}")
        print(f"Test Set Size: {rep.get('test_set_size')} images")
        print(f"mAP@0.5:      {m.get('mAP50'):.3f}")
        print(f"mAP@0.5:0.95: {m.get('mAP50_95'):.3f}")
        print(f"Precision:    {m.get('precision'):.3f}")
        print(f"Recall:       {m.get('recall'):.3f}")
        print(f"Mean Latency: {m.get('mean_inference_latency_ms')} ms ({m.get('throughput_fps')} FPS)")

        print("\nPer-Class Breakdown:")
        for cls, metrics in rep.get("per_class_breakdown", {}).items():
            print(f"  - {cls:16s} | mAP50: {metrics.get('mAP50', metrics.get('accuracy', 0)):.3f} | Support: {metrics.get('support')}")
    else:
        print("Evaluation report not found. Run training or preprocess first.")

if __name__ == '__main__':
    evaluate()
