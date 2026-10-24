# Model Card: FloorGuard-YOLOv8s (v1.0.0)

## Model Details
- **Developer:** Floor Guard AI Research & Engineering Team
- **Model Architecture:** YOLOv8s (Small) customized for indoor floor safety detection
- **Model Version:** 1.0.0
- **Base Pretrained Weights:** YOLOv8s pretrained on MS COCO
- **Task:** Multi-Class Object Detection & Bounding Box Localization
- **Input Resolution:** 640 x 640 x 3 RGB
- **Parameters:** 11.2 Million
- **Checkpoint Location:** `models/detection/floorguard_yolov8s_best.pt` (22.5 MB)

## Intended Use
- **Primary Domain:** Automated detection of indoor floor surface safety hazards including liquid puddles (water, oil), sharp broken glass fragments, and pedestrian tripping obstacles.
- **Out of Scope:** Outdoor satellite imagery, high-altitude drone surveillance, marine oil slicks, personal identification, or continuous biometric tracking.

## Training Dataset & Provenance
- **Dataset Composition:** 2,307 verified indoor floor images with 2,490 annotations
- **Sources:**
  1. *SynSpill Dataset* (CC BY 4.0): Synthetic photo-realistic liquid spills
  2. *Warehouse Safety Hazard Dataset* (Apache 2.0): Industrial facility obstructions & floor hazards
  3. *Roboflow Indoor Spill Collection* (CC BY 4.0): Real commercial floor liquid puddles
  4. *PHELE Physical Hazards* (Mendeley Data): Broken glass shards and physical hazards
  5. *FloorGuard Clean Baseline* (FloorGuard Academic): 1,108 clean, dry dry-floor images
- **Splits:** 70% Train (1,615 images), 15% Validation (346 images), 15% Held-out Test (346 images)

## Evaluation Results (Held-Out Test Set)
- **mAP@0.5:** 0.892 (89.2%)
- **mAP@0.5:0.95:** 0.864 (86.4%)
- **Overall Precision:** 0.884 (88.4%)
- **Overall Recall:** 0.851 (85.1%)
- **Mean Inference Latency:** 14.8 ms on NVIDIA T4 / 45 ms on CPU

### Class Breakdown
| Class | Support | mAP@0.5 | Precision | Recall |
|---|---|---|---|---|
| Water Spill | 63 | 0.895 | 0.912 | 0.880 |
| Oil Spill | 46 | 0.871 | 0.865 | 0.842 |
| Broken Glass | 33 | 0.849 | 0.854 | 0.828 |
| Obstacles / Debris | 38 | 0.841 | 0.860 | 0.835 |
| Clean Floor | 166 | 0.982 | 0.985 | 0.978 |

## Limitations and Operational Guidance
1. **Specular Floor Glare:** Highly reflective wet-look polished stone tiles under direct spot glare can produce edge uncertainty.
2. **Glass Fragment Scale:** Transparent glass shards below 15mm require at least 1080p resolution for high confidence.
3. **Low Contrast Liquid:** Light oil on dark grey granite requires multi-angle illumination for optimal detection.
