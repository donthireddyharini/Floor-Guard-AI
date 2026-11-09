#!/usr/bin/env python3
"""
Floor Guard AI - 30-Second Clean Multi-Hazard Raw Footage Generator
Generates clean, authentic industrial inspection CCTV footage across 5 floor hazard zones
without pre-baked annotations or burned-in boxes, allowing Floor Guard AI to perform
genuine dynamic hazard detection during playback.
"""

import os
import sys
import cv2
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_PATH = os.path.join(BASE_DIR, 'public', 'assets', 'samples', 'corridor_hazard_tour_30s.mp4')
os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

FPS = 30
DURATION_SEC = 30
WIDTH = 1280
HEIGHT = 720

SCENARIOS = [
    {
        "name": "Clean Corridor Walkway",
        "hazard": "Clean Floor",
        "severity": "Safe",
        "image": os.path.join(BASE_DIR, "dataset", "images", "test", "hf_bal_clean_floor_0133.jpg"),
        "duration_sec": 6.0
    },
    {
        "name": "Entrance Corridor Liquid Pooling",
        "hazard": "Water Spill",
        "severity": "High",
        "image": os.path.join(BASE_DIR, "dataset", "images", "test", "floor_hazard_water_spill_marble_aug4_contrast.jpg"),
        "duration_sec": 6.0
    },
    {
        "name": "Machinery Maintenance Zone - Petroleum Leak",
        "hazard": "Oil Spill",
        "severity": "Critical",
        "image": os.path.join(BASE_DIR, "dataset", "images", "test", "floor_hazard_oil_spill_warehouse_aug4_contrast.jpg"),
        "duration_sec": 6.0
    },
    {
        "name": "Assembly Floor - Shattered Glass Shards",
        "hazard": "Broken Glass",
        "severity": "Critical",
        "image": os.path.join(BASE_DIR, "dataset", "images", "test", "floor_hazard_broken_glass_store_aug4_contrast.jpg"),
        "duration_sec": 6.0
    },
    {
        "name": "Transit Aisle - Pallet & Box Obstruction",
        "hazard": "Obstacle",
        "severity": "Medium",
        "image": os.path.join(BASE_DIR, "dataset", "images", "test", "aug_boxes_sec03_contrast.jpg"),
        "duration_sec": 6.0
    }
]

def render_scene_frame(img, progress, frame_idx):
    """Render authentic CCTV frame with slow camera push-in and subtle timestamp."""
    h, w, _ = img.shape
    # Smooth camera push-in from 1.0 to 1.06
    scale = 1.0 + (progress * 0.06)
    crop_w = int(w / scale)
    crop_h = int(h / scale)
    x1 = (w - crop_w) // 2
    y1 = (h - crop_h) // 2
    cropped = img[y1:y1 + crop_h, x1:x1 + crop_w]
    frame = cv2.resize(cropped, (WIDTH, HEIGHT), interpolation=cv2.INTER_LINEAR)

    # Minimal clean timestamp in top-left (authentic CCTV style)
    sec = frame_idx / FPS
    time_str = f"CAM-04 | 2026-10-26 {int(sec//60):02d}:{int(sec%60):02d}:{int((sec*100)%100):02d}"
    cv2.putText(frame, time_str, (18, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (230, 230, 230), 1, cv2.LINE_AA)

    return frame

def generate_video():
    print(f"Generating clean un-annotated 30s video at {OUTPUT_PATH}...")
    loaded_images = []
    for sc in SCENARIOS:
        img = cv2.imread(sc["image"])
        if img is None:
            img = np.full((720, 1280, 3), 40, dtype=np.uint8)
        else:
            img = cv2.resize(img, (WIDTH, HEIGHT))
        loaded_images.append(img)

    fourcc = cv2.VideoWriter_fourcc(*'avc1')
    writer = cv2.VideoWriter(OUTPUT_PATH, fourcc, FPS, (WIDTH, HEIGHT))

    frames_per_scene = FPS * 6  # 180 frames per scene * 5 = 900 frames = 30s
    total_written = 0

    for s_idx, scenario in enumerate(SCENARIOS):
        img = loaded_images[s_idx]
        for f in range(frames_per_scene):
            progress = f / float(frames_per_scene)
            frame = render_scene_frame(img, progress, total_written)
            writer.write(frame)
            total_written += 1

    writer.release()
    print(f"Successfully generated {total_written} clean frames ({round(total_written/FPS, 1)}s) to {OUTPUT_PATH}")

    # Generate matching clean thumbnails for timeline
    thumbs = [
        (90, 'thumb_clean_floor.jpg'),
        (270, 'thumb_water_spill.jpg'),
        (450, 'thumb_oil_spill.jpg'),
        (630, 'thumb_broken_glass.jpg'),
        (810, 'thumb_obstacle.jpg')
    ]
    cap = cv2.VideoCapture(OUTPUT_PATH)
    thumb_dir = os.path.join(BASE_DIR, 'public', 'assets', 'samples')
    for f_idx, name in thumbs:
        cap.set(cv2.CAP_PROP_POS_FRAMES, f_idx)
        ret, frame = cap.read()
        if ret:
            cv2.imwrite(os.path.join(thumb_dir, name), cv2.resize(frame, (480, 270)))
    cap.release()
    print("Clean keyframe thumbnails generated.")

if __name__ == '__main__':
    generate_video()
