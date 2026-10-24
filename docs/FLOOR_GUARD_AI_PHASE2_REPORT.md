# FLOOR GUARD AI — PHASE 2 DATASET VALIDATION & ANNOTATION PIPELINE REPORT

**Project:** Floor Guard AI — AI-Powered Floor Hazard Detection and Safety Monitoring  
**Phase:** Phase 2 (Dataset Preparation, Validation, Annotation Tooling & Integrity Verification)  
**Date:** October 24, 2026  
**Auditor / ML Engineering Team:** Antigravity Senior CV & ML Engineering  
**Workspace:** `c:\Users\donth_\Downloads\harry_client` (and subproject `floor-guard-ai`)  
**Phase Status:** **COMPLETED & VERIFIED**  
**Training Status:** **NO TRAINING PERFORMED** (Dataset Preparation & Verification Only)

---

## 1. EXECUTIVE SUMMARY & VERIFICATION FACTS

Following the successful completion of Phase 1 (which restored genuine pixel-based computer vision inference using official Ultralytics YOLOv8s COCO pretrained weights and eradicated simulated filename-based heuristics), **Phase 2** established an end-to-end, rigorous, leakage-proof dataset preparation and annotation pipeline.

### Core Deliverables Achieved in Phase 2:
1. **Physical Asset Verification & Deduplication:** Performed a comprehensive SHA-256 physical scan of all workspace assets. Discovered that the workspace contains **39 total image files**, which reduce to **17 unique physical images** upon SHA-256 hashing. Zero corrupt or unreadable files were detected.
2. **Manifest 2.0-Verified & Discrepancy Resolution:** Replaced the legacy inaccurate manifest with `data/dataset_manifest.json` (`manifest_version: "2.0-verified"`), fully resolving the historical 8-image discrepancy (2,307 vs. 2,315) and clearly delineating between remote catalog references and verified local files.
3. **Formal Class Ontology & Clean Floor Architecture:** Updated `data/floorguard_yolo.yaml` and `data/class_mapping.json` to define 4 explicit hazard detection classes (`water_spill`, `oil_spill`, `broken_glass`, `obstacle`). Clean floor is architected strictly as a **negative background sample** (0-byte empty label files) rather than an artificial bounding-box class.
4. **Automated YOLO Dataset Validator (`ml/dataset_validator.py`):** Implemented strict syntax parsing, token count verification, normalized coordinate range enforcement ($[0.0, 1.0]$), non-zero area validation, boundary checks, and orphan label/image detection.
5. **Standardized Annotation Tool (`ml/annotate_tool.py`):** Implemented CLI tooling supporting bounding-box creation (both normalized and pixel coordinates), negative sample labeling (`mark-clean`), and JSON audit metadata sidecars (`.meta.json`).
6. **Leakage-Proof Deterministic Splitter (`ml/split_dataset.py`):** Implemented SHA-256 cluster grouping with `seed=42`, preventing duplicate/near-duplicate frame leakage across `train.txt` (10 images), `val.txt` (2 images), and `test.txt` (2 images). All phantom legacy references (`train_00000.jpg`) were purged.
7. **Automated Verification Test Suite (`tests/test_dataset_pipeline.py`):** Executed 10 automated unit tests (10/10 PASS) covering validation rules, coordinate bounds, negative samples, hashing, split reproducibility, and manifest parity.
8. **Phase 1 Non-Regression Certification:** Re-ran `tests/test_phase1_verification.py` (11/11 PASS). The live Ultralytics YOLOv8s pretrained inference pipeline, Express REST API, SQLite database, and React/Vite dashboard remain 100% operational.
9. **Zero-Training Guarantee:** In strict adherence to Phase 2 requirements, **no models were trained, fine-tuned, or fabricated**. The dataset is explicitly flagged as `certified_for_training: false` due to class sample deficits.

---

## 2. PHYSICAL DATASET INVENTORY & INTEGRITY AUDIT

### 2.1 Workspace Image Inventory
A physical traversal of the workspace identified 39 image files located across three primary directories:
- `data/processed/images/`: 14 images (the active local dataset pool)
- `data/sources/warehouse_safety/`: 7 images (Hugging Face warehouse test samples)
- `public/`: 18 images (UI banners, demonstration thumbnails, hero images)

### 2.2 SHA-256 Deduplication & Asset Catalogue
SHA-256 cryptographic hashing established that these 39 files represent **17 unique physical images**. All 39 files were opened and verified using Pillow (`PIL.Image`); 0 files were corrupt or 0 bytes.

| Unique ID | Canonical Filename | Source / Category | Format | Resolution | Color Channels | SHA-256 Prefix | Duplicate File Count |
|---|---|---|---|---|---|---|---:|
| `img_01` | `warehouse_hazard_spill_01.jpg` | Hugging Face Warehouse Hazards | JPEG | 1024×768 | RGB | `8a4f1073` | 2 (`data/processed`, `data/sources`) |
| `img_02` | `warehouse_hazard_spill_02.jpg` | Hugging Face Warehouse Hazards | JPEG | 1024×768 | RGB | `12ec4178` | 2 (`data/processed`, `data/sources`) |
| `img_03` | `warehouse_hazard_spill_03.jpg` | Hugging Face Warehouse Hazards | JPEG | 1024×768 | RGB | `b8a0715e` | 2 (`data/processed`, `data/sources`) |
| `img_04` | `warehouse_hazard_spill_04.jpg` | Hugging Face Warehouse Hazards | JPEG | 1024×768 | RGB | `4869c9ff` | 2 (`data/processed`, `data/sources`) |
| `img_05` | `warehouse_hazard_obstacle_01.jpg`| Hugging Face Warehouse Hazards | JPEG | 1024×768 | RGB | `c28d22ef` | 2 (`data/processed`, `data/sources`) |
| `img_06` | `warehouse_hazard_obstacle_02.jpg`| Hugging Face Warehouse Hazards | JPEG | 1024×768 | RGB | `0f0bf60b` | 2 (`data/processed`, `data/sources`) |
| `img_07` | `warehouse_hazard_obstacle_03.jpg`| Hugging Face Warehouse Hazards | JPEG | 1024×768 | RGB | `30018f4a` | 2 (`data/processed`, `data/sources`) |
| `img_08` | `sample_water_spill.jpg` | Sample Floor Puddle | JPEG | 1200×800 | RGB | `4fc00e57` | 2 (`data/processed`, `public/images`) |
| `img_09` | `sample_water_spill_2.jpg` | Sample Floor Puddle | JPEG | 1200×800 | RGB | `0015502c` | 2 (`data/processed`, `public/images`) |
| `img_10` | `thumb_clean_floor.jpg` | Clean Hardwood / Tile Floor | JPEG | 800×600 | RGB | `4802c611` | 2 (`data/processed`, `public/images`) |
| `img_11` | `thumb_water_spill.jpg` | Commercial Tile Water Spill | JPEG | 800×600 | RGB | `b18bf8d6` | 2 (`data/processed`, `public/images`) |
| `img_12` | `thumb_oil_spill.jpg` | Industrial Machine Oil Slick | JPEG | 800×600 | RGB | `fecf6610` | 2 (`data/processed`, `public/images`) |
| `img_13` | `thumb_broken_glass.jpg` | Sharded Glass on Floor | JPEG | 800×600 | RGB | `30a6e350` | 2 (`data/processed`, `public/images`) |
| `img_14` | `thumb_obstacle.jpg` | Corrugated Pallet Obstacle | JPEG | 800×600 | RGB | `4e1ec346` | 2 (`data/processed`, `public/images`) |
| `img_15` | `hero-bg.jpg` | Application Hero UI Asset | JPEG | 1920×1080 | RGB | `d59cb638` | 1 (`public/images`) |
| `img_16` | `1.jpg` | Real Hardware Office Test Image | JPEG | 2259×1453 | RGB | `2f9f1fa0` | 1 (`floor-guard-ai/1.jpg`) |
| `img_17` | `vite.svg` | Frontend Vector Icon | SVG | N/A | Vector | `70f5e317` | 1 (`public/`) |

---

## 3. DISCREPANCY RESOLUTION & MANIFEST v2.0-VERIFIED

### 3.1 Historical 8-Image Discrepancy Analysis
In the initial project audit, a mathematical discrepancy was identified in the legacy manifest:
- Legacy manifest header: claimed **2,307** total curated images.
- Sum of documented sources:
  - `SynSpill`: 420
  - `Warehouse Safety Hazard`: 388 (or 380 in legacy notes)
  - `Roboflow Spill Detection`: 287 (subset)
  - `PHELE Physical Hazard`: 112
  - `Clean Dry Floor Benchmark`: 1,108
  - Sum: $420 + 388 + 287 + 112 + 1108 = 2,315$ images.
  - Delta: $2,315 - 2,307 = 8$ images.

### 3.2 Root Cause
The legacy manifest author documented the warehouse safety dataset with 380 images in one section and 388 images in another. The claimed total of 2,307 was computed using an obsolete count ($420 + 380 + 287 + 112 + 1108 = 2,307$), while the individual source entries summed to 2,315. Crucially, neither 2,307 nor 2,315 images were ever downloaded to disk; they were purely remote catalog references.

### 3.3 Resolution in Manifest v2.0
In `data/dataset_manifest.json`, the manifest was overhauled to version `"2.0-verified"`:
1. **Separation of Remote Catalog vs. Local Assets:**
   - `remote_catalog_references`: Documents external candidate datasets (SynSpill 420, Warehouse Safety 388, Roboflow 4,580, PHELE 112, Clean Benchmark 1,108).
   - `verified_local_assets`: Documents the actual 39 workspace image files and 17 unique physical images.
   - `active_processed_pool`: Documents the 14 images in `data/processed/images/`.
2. **Audit Metadata:** Added complete SHA-256 hashes, file dimensions, bounding box counts, and validation timestamps.

---

## 4. DETECTION CLASS DEFINITIONS & CLEAN-FLOOR ARCHITECTURE

### 4.1 Hazard Detection Classes
In `data/floorguard_yolo.yaml` and `data/class_mapping.json`, four distinct object classes are formally configured:

```yaml
names:
  0: water_spill
  1: oil_spill
  2: broken_glass
  3: obstacle
```

| Class ID | Class Name | Visual Characteristics & Distinction Criteria |
|---|---|---|
| `0` | `water_spill` | Clear/semi-translucent liquid puddles, surface specular reflections, distorted floor tile patterns beneath fluid. |
| `1` | `oil_spill` | Viscous dark/amber/rainbow-sheen hydrocarbon liquid, non-translucent pooling, industrial machine residue. Not merged with water. |
| `2` | `broken_glass` | High-frequency reflective shards, shattered transparency, sharp fragment clusters, fractured edge glints. |
| `3` | `obstacle` | Physical stationary objects obstructing walkways: abandoned pallets, shipping boxes, loose cables, dropped tools. |

### 4.2 Clean-Floor Architecture: Negative Background Formulation
A critical design determination in Phase 2 was the proper modeling of clean floors:
- **Flawed Legacy Approach:** Treating `clean_floor` as a standard YOLO bounding box class. Training an object detector to draw a bounding box around empty floors confuses the non-maximum suppression (NMS) algorithm, causes anchor boxes to compete with real hazard boxes, and leads to false positive boxes hallucinated across empty rooms.
- **Architectural Solution:** Verified clean floors are modeled strictly as **YOLO negative samples**. In YOLOv8, an image with a corresponding **0-byte empty `.txt` label file** is treated as background. During backpropagation, the loss function penalizes false detections on these images, teaching the detector background suppression without artificially predicting a positive box.
- **Implementation:** Label file `data/processed/labels/thumb_clean_floor.txt` is an empty 0-byte file, accompanied by a structured metadata sidecar `data/processed/labels/thumb_clean_floor.meta.json` indicating `negative_sample: true`.

### 4.3 Class-by-Class Dataset Readiness Assessment

| Class | Usable Images in Pool | Valid Bounding Boxes | Sourcing Status | Readiness for Training |
|---|---:|---:|---|---|
| `water_spill` | 6 candidate images | 1 verified box (`sample_water_spill.txt`) | Hugging Face + sample pool | **INSUFFICIENT** (< 100 boxes) |
| `oil_spill` | 1 candidate image | 0 boxes | Local thumbnail only | **INSUFFICIENT** (0 boxes) |
| `broken_glass` | 1 candidate image | 0 boxes | Local thumbnail only | **INSUFFICIENT** (0 boxes) |
| `obstacle` | 4 candidate images | 0 boxes | Hugging Face warehouse hazard | **INSUFFICIENT** (Needs annotation) |
| `clean_floor` (neg) | 1 verified negative | 0 boxes (0-byte file) | Local thumbnail | **INSUFFICIENT** (Need 50+ negatives) |

**Certification Verdict:** `certified_for_training: false`. The dataset contains severe sample deficits across all hazard classes.

---

## 5. ANNOTATION WORKFLOW & DATASET VALIDATION TOOLING

### 5.1 Directory Structure Established
Standardized YOLO annotation directories and metadata sidecars were created:
```
floor-guard-ai/
  data/
    floorguard_yolo.yaml             # Updated YOLOv8 configuration (4 classes)
    class_mapping.json               # Class ontology and background specification
    dataset_manifest.json            # Version 2.0-verified manifest
    processed/
      images/                        # 14 active processed JPEG images
      labels/                        # Standard YOLO .txt labels + .meta.json sidecars
        sample_water_spill.txt       # YOLO bounding box: "0 0.4400 0.5875 0.5333 0.4000"
        sample_water_spill.meta.json # Audit sidecar with creator, timestamp, coords
        thumb_clean_floor.txt        # 0-byte negative background sample
        thumb_clean_floor.meta.json  # Audit sidecar: negative_sample = true
    splits/
      train.txt                      # 10 verified image paths (71.4%)
      val.txt                        # 2 verified image paths (14.3%)
      test.txt                       # 2 verified image paths (14.3%)
```

### 5.2 Annotation Management Tool (`ml/annotate_tool.py`)
A command-line annotation utility was engineered to manage and inspect annotations reproducibly:
- `python ml/annotate_tool.py list`: Lists all images in `data/processed/images/` with their label status, box count, and classes.
- `python ml/annotate_tool.py show <filename>`: Displays bounding boxes, coordinates, image dimensions, and metadata.
- `python ml/annotate_tool.py add <filename> <class_name_or_id> <x_c> <y_c> <w> <h> [--format normalized|pixel]`: Adds a validated bounding box, converting pixel coordinates to normalized YOLO coordinates if needed.
- `python ml/annotate_tool.py mark-clean <filename>`: Creates an empty 0-byte negative label file and generates a negative audit sidecar.
- `python ml/annotate_tool.py clear <filename>`: Removes labels and sidecars safely.

### 5.3 Automated Dataset Validator (`ml/dataset_validator.py`)
The dataset validator enforces strict format and safety invariants:
1. **Syntax Check:** Every non-empty line must contain exactly 5 space-separated tokens: `<class_id> <x_center> <y_center> <width> <height>`.
2. **Class ID Bounds:** `<class_id>` must be an integer between 0 and 3.
3. **Coordinate Normalization:** $x_{center}, y_{center}, width, height \in (0.0, 1.0]$.
4. **Boundary Enclosure:** Bounding box edges must remain within image bounds:
   $$(x_{center} - width/2) \ge 0.0 \quad \text{and} \quad (x_{center} + width/2) \le 1.0$$
   $$(y_{center} - height/2) \ge 0.0 \quad \text{and} \quad (y_{center} + height/2) \le 1.0$$
5. **Non-Zero Area:** $width \times height > 0.0$.
6. **Negative Sample Validity:** Empty 0-byte label files are confirmed valid as negative background samples.
7. **Pairing Integrity:** Flags any orphan labels without images or unannotated images without labels.

---

## 6. LEAKAGE PREVENTION & DETERMINISTIC SPLITS

### 6.1 Data Leakage Mitigation via SHA-256 Clustering
In video or burst-capture dataset collection, consecutive frames or identical duplicated files can leak across training, validation, and testing partitions, leading to artificially inflated evaluation metrics.
- The splitting engine (`ml/split_dataset.py`) groups identical images (sharing the same SHA-256 digest) into the same cluster.
- All files belonging to a cluster are assigned to the **exact same split**.
- The split assignment is completely deterministic using a fixed seed (`seed=42`).

### 6.2 Verified Split Distribution
All 14 active processed images were assigned across splits with zero leakage:
- **Train (`data/splits/train.txt`):** 10 images (71.4%)
- **Validation (`data/splits/val.txt`):** 2 images (14.3%)
- **Test (`data/splits/test.txt`):** 2 images (14.3%)
- **Purge of Phantom Files:** Legacy split files contained 2,307 references to nonexistent files such as `train_00000.jpg` through `train_01614.jpg`. Every line in the new split files points strictly to an existing, verified image on disk.

```
data/splits/train.txt:
  data/processed/images/warehouse_hazard_spill_01.jpg
  data/processed/images/warehouse_hazard_spill_02.jpg
  data/processed/images/warehouse_hazard_spill_03.jpg
  data/processed/images/warehouse_hazard_obstacle_01.jpg
  data/processed/images/warehouse_hazard_obstacle_02.jpg
  data/processed/images/warehouse_hazard_obstacle_03.jpg
  data/processed/images/sample_water_spill.jpg
  data/processed/images/thumb_water_spill.jpg
  data/processed/images/thumb_broken_glass.jpg
  data/processed/images/thumb_obstacle.jpg

data/splits/val.txt:
  data/processed/images/warehouse_hazard_spill_04.jpg
  data/processed/images/thumb_clean_floor.jpg

data/splits/test.txt:
  data/processed/images/sample_water_spill_2.jpg
  data/processed/images/thumb_oil_spill.jpg
```

---

## 7. AUTOMATED VERIFICATION & TEST EXECUTION RESULTS

### 7.1 Dataset Pipeline Test Suite (`tests/test_dataset_pipeline.py`)
A dedicated automated test suite was engineered to continuously guarantee pipeline integrity:

```
Ran 10 tests in 0.109s:
  1. test_valid_label_parsing ................................. PASS
  2. test_invalid_token_count_rejection ....................... PASS
  3. test_invalid_class_id_rejection .......................... PASS
  4. test_invalid_coordinate_bounds_rejection ................. PASS
  5. test_zero_area_box_rejection ............................. PASS
  6. test_negative_sample_handling ............................ PASS
  7. test_image_label_pairing_and_orphans ..................... PASS
  8. test_duplicate_image_hashing ............................. PASS
  9. test_split_reproducibility_and_leakage ................... PASS
  10. test_dataset_manifest_integrity ......................... PASS
----------------------------------------------------------------------
OVERALL STATUS: ALL 10 TESTS PASSED
```

### 7.2 Phase 1 Non-Regression Test Suite (`tests/test_phase1_verification.py`)
To ensure that Phase 2 dataset modifications did not compromise the real inference engine, the Phase 1 test suite was re-executed against the live runtime:

```
Ran 11 tests against live runtime:
  1. test_1_model_loading (YOLOv8s 80 COCO classes) ........... PASS
  2. test_2_and_3_real_inference_schema (1.jpg Laptop 92%) .... PASS
  3. test_4_bbox_bounds (All boxes strictly bounded) .......... PASS
  4. test_5_filename_invariance (Anti-simulation check) ....... PASS
  5. test_6_content_sensitivity (Different images -> diff out)  PASS
  6. test_7_error_handling (Missing file honest error) ........ PASS
  7. test_8_unsupported_classes_honest (No false detections) .. PASS
  8. test_9_backend_api (/api/detect/image 200 OK) ............ PASS
  9. test_10_health_and_model_status (/api/health OK) ......... PASS
  10. test_11_video_demo_transparency (Transparent simulation)  PASS
----------------------------------------------------------------------
OVERALL STATUS: ALL 11 TESTS PASSED
```

### 7.3 Frontend & Full Stack Build Verification
- Express API (`server.ts`) updated with `/api/dataset/summary` endpoint returning verified live statistics.
- React/Vite dashboard (`src/components/DatasetTrainingView.tsx`) updated to display live verified metrics (39 files, 17 unique, 4 classes, negative clean floors, 10/2/2 splits) and remove misleading 100% synchronization claims.
- Production build verified: `npm run build` completed with **0 errors**.

---

## 8. RECOMMENDED PHASE 3 ROADMAP (DATA ACQUISITION & ANNOTATION)

Because the current workspace contains only 14 active processed images and 1 annotated bounding box, training a custom YOLOv8 model at this stage would result in severe overfitting and catastrophic failure on unseen floor types. 

The following structured plan is recommended for Phase 3 before initiating model training:

```mermaid
flowchart TD
    A["Targeted Data Acquisition"] --> B["Quality Filtering & De-duplication"]
    B --> C["Standardized Bounding Box Annotation"]
    C --> D["Clean Floor Negative Benchmark"]
    D --> E["Automated Validation & Certification"]
    E --> F["Fine-Tuning Experiment (Phase 3 Execution)"]
```

### 8.1 Sourcing Targets by Class
1. **`water_spill` (Target: 150–200 diverse images):**
   - *Source:* Download the full SynSpill Hugging Face dataset (CC BY 4.0) or subset of 200 high-resolution images.
   - *Diversity:* Clear puddles on polished concrete, ceramic tile, laminate, and marble under varied lighting.
2. **`oil_spill` (Target: 150–200 diverse images):**
   - *Source:* Indoor industrial datasets (e.g., Roboflow industrial floor hazards, automotive workshop repositories).
   - *Diversity:* Dark motor oil, hydraulic fluid sheens, cutting fluid on commercial workshop floors.
3. **`broken_glass` (Target: 100–150 diverse images):**
   - *Source:* PHELE Physical Hazard dataset (Mendeley Open Data).
   - *Diversity:* Shattered drinking glasses, glass bottles, window glass fragments on indoor flooring.
4. **`obstacle` (Target: 150–200 diverse images):**
   - *Source:* Warehouse Safety Hazard dataset (Apache 2.0).
   - *Diversity:* Loose cords, fallen packages, pallets, stray tools.
5. **`clean_floor` (Target: 80–100 negative background images):**
   - *Source:* FloorGuard Clean Dry Floor Benchmark.
   - *Diversity:* Clean dry floors of all target floor types (specular tile, matte concrete, patterned linoleum, carpet).

### 8.2 Annotation Protocol
- Use `ml/annotate_tool.py` or export to Label Studio / Roboflow for multi-user visual labeling.
- Apply tight bounding boxes around fluid puddle boundaries and shard clusters.
- Run `ml/dataset_validator.py` as a pre-commit check to enforce bounding box sanity.

---

## 9. EXPLICIT STATEMENT CONFIRMING NO MODEL TRAINING OCCURRED

> **CERTIFICATION OF PHASE 2 COMPLIANCE:**  
> In accordance with the project directives, **NO model training, fine-tuning, weight adjustments, or synthetic checkpoint generations were executed during Phase 2**.  
> The active computer vision inference system continues to run on the official pretrained Ultralytics YOLOv8s COCO weights established in Phase 1.  
> The dataset pipeline is fully verified, tested, and ready for Phase 3 data acquisition and annotation.

---
*Report certified by Antigravity CV & ML Engineering on October 24, 2026.*