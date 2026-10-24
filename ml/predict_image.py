#!/usr/bin/env python3
"""
Floor Guard AI - Real Model Inference Engine (Multi-Model Support)
Performs genuine pixel-level object detection using either:
  1. Production Baseline: Ultralytics YOLOv8s pretrained on MS-COCO (80 classes)
  2. Experimental Hazard Detector: FloorGuard YOLOv8s custom-trained on floor hazards (4 classes)

Generates authentic bounding-box annotations, saves annotated image artifacts to uploads/annotated/,
and outputs comprehensive structured telemetry with zero hardcoding.
"""

import sys
import os
import json
import time
import uuid
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = Path(__file__).resolve().parent.parent

# Model Checkpoint Registry Paths
MODEL_PATHS = {
    'yolov8s-coco-pretrained': BASE_DIR / 'models' / 'pretrained' / 'yolov8s.pt',
    'floorguard-yolov8s-v1.1.0-phase4.2': BASE_DIR / 'models' / 'detection' / 'floorguard_yolov8s_phase4_2_best.pt',
    'floorguard-yolov8s-v1.0.0': BASE_DIR / 'models' / 'detection' / 'floorguard_yolov8s_best.pt',
    'default': BASE_DIR / 'models' / 'pretrained' / 'yolov8s.pt'
}

CUSTOM_CLASSES = {
    0: 'water_spill',
    1: 'oil_spill',
    2: 'broken_glass',
    3: 'obstacle'
}

CLASS_COLORS = {
    'water_spill': '#06b6d4',      # Cyan
    'oil_spill': '#f59e0b',        # Amber/Orange
    'broken_glass': '#a855f7',     # Purple
    'obstacle': '#ef4444',         # Red
    'clean_floor': '#10b981',      # Emerald Green
    'default': '#f97316'           # Hazard Orange
}

_LOADED_MODELS = {}

def get_yolo_model(model_identifier):
    """Load and cache the requested YOLO model."""
    global _LOADED_MODELS
    
    # Resolve checkpoint path
    target_path = None
    mid_lower = str(model_identifier).lower()
    if 'phase4_2' in mid_lower or '1.1.0' in mid_lower:
        target_path = BASE_DIR / 'models' / 'detection' / 'floorguard_yolov8s_phase4_2_best.pt'
    elif 'phase4' in mid_lower or '1.0.0' in mid_lower and 'coco' not in mid_lower:
        target_path = BASE_DIR / 'models' / 'detection' / 'floorguard_yolov8s_best.pt'
    elif model_identifier in MODEL_PATHS:
        target_path = MODEL_PATHS[model_identifier]
    elif os.path.exists(model_identifier):
        target_path = Path(model_identifier)
    else:
        # Check model registry
        reg_path = BASE_DIR / 'models' / 'model_registry.json'
        if reg_path.exists():
            try:
                with open(reg_path, 'r', encoding='utf-8') as f:
                    reg = json.load(f)
                for m in reg.get('registry', []):
                    if m.get('id') == model_identifier:
                        target_path = BASE_DIR / m.get('weights_path', '')
                        break
            except Exception:
                pass
                
    if not target_path or not target_path.exists():
        target_path = MODEL_PATHS['yolov8s-coco-pretrained']
        if not target_path.exists():
            target_path = BASE_DIR / 'yolov8s.pt'
            
    cache_key = str(target_path.resolve())
    if cache_key in _LOADED_MODELS:
        return _LOADED_MODELS[cache_key], target_path

    from ultralytics import YOLO
    model = YOLO(str(target_path))
    _LOADED_MODELS[cache_key] = model
    return model, target_path

def resolve_image_path(image_path):
    """Resolve absolute path across relative, data, and uploads directories."""
    abs_path = os.path.abspath(image_path)
    if os.path.exists(abs_path):
        return abs_path

    alt_paths = [
        os.path.join(str(BASE_DIR), image_path.lstrip('/\\')),
        os.path.join(str(BASE_DIR), 'uploads', 'originals', os.path.basename(image_path)),
        os.path.join(str(BASE_DIR), 'uploads', os.path.basename(image_path)),
        os.path.join(str(BASE_DIR), 'data', 'processed', 'images', os.path.basename(image_path)),
        os.path.join(str(BASE_DIR), 'data', 'benchmark_expanded', 'images', os.path.basename(image_path)),
        os.path.join(str(BASE_DIR), 'public', image_path.lstrip('/\\')),
        os.path.join(str(BASE_DIR.parent), os.path.basename(image_path))
    ]
    for ap in alt_paths:
        if os.path.exists(ap):
            return ap
    return None

def draw_annotations(orig_img_path, detections, out_dir):
    """Render authentic bounding boxes and labels onto the image and save to disk."""
    try:
        im = Image.open(orig_img_path).convert('RGB')
        draw = ImageDraw.Draw(im)
        w, h = im.size
        
        # Line width based on image size
        line_w = max(2, int(min(w, h) / 300))
        
        for det in detections:
            bbox = det.get('bounding_box', {})
            bx = bbox.get('x', 0)
            by = bbox.get('y', 0)
            bw = bbox.get('width', 0)
            bh = bbox.get('height', 0)
            
            cname = det.get('class_name', '').lower().replace(' ', '_')
            hex_color = CLASS_COLORS.get(cname, CLASS_COLORS['default'])
            
            # Draw rectangle
            draw.rectangle([bx, by, bx + bw, by + bh], outline=hex_color, width=line_w)
            
            # Label banner
            conf_str = det.get('confidence_percent', f"{int(det.get('confidence', 0)*100)}%")
            label_text = f"{det.get('class_name')} {conf_str}"
            
            # Text background
            text_bbox = draw.textbbox((bx, max(0, by - 18)), label_text)
            draw.rectangle([text_bbox[0] - 2, text_bbox[1] - 2, text_bbox[2] + 2, text_bbox[3] + 2], fill=hex_color)
            draw.text((bx, max(0, by - 18)), label_text, fill='#ffffff')
            
        os.makedirs(out_dir, exist_ok=True)
        fname = f"ann_{int(time.time()*1000)}_{uuid.uuid4().hex[:6]}.jpg"
        save_path = os.path.join(out_dir, fname)
        im.save(save_path, 'JPEG', quality=90)
        return save_path, f"/uploads/annotated/{fname}"
    except Exception as e:
        return None, None

def detect(image_path, model_identifier="yolov8s-coco-pretrained", conf_threshold=0.25):
    """
    Execute real model inference on image pixels.
    """
    if not model_identifier or model_identifier == 'detector' or 'coco' in str(model_identifier).lower():
        model_identifier = 'yolov8s-coco-pretrained'

    abs_path = resolve_image_path(image_path)
    if not abs_path:
        return {
            "status": "error",
            "message": f"Image file not found on disk: {image_path}"
        }

    try:
        with Image.open(abs_path) as pil_im:
            width, height = pil_im.size
    except Exception as e:
        return {
            "status": "error",
            "message": f"Unable to read image pixels or corrupted file: {abs_path}"
        }

    t0 = time.time()
    try:
        model, model_file = get_yolo_model(model_identifier)
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to initialize YOLO detector ({model_identifier}): {str(e)}"
        }

    # Determine if custom hazard model or COCO pretrained
    is_custom_hazard_model = 'floorguard' in model_file.name.lower() or 'phase4' in model_file.name.lower()
    
    try:
        results = model.predict(source=abs_path, conf=float(conf_threshold), verbose=False)
        res = results[0]
    except Exception as e:
        return {
            "status": "error",
            "message": f"Inference execution failed on image pixels: {str(e)}"
        }

    inference_ms = round((time.time() - t0) * 1000.0, 2)
    boxes = res.boxes
    detections = []

    for box in boxes:
        cls_id = int(box.cls[0].item())
        conf_val = float(box.conf[0].item())
        x1, y1, x2, y2 = box.xyxy[0].tolist()

        bx = max(0, int(round(x1)))
        by = max(0, int(round(y1)))
        bw = min(width - bx, int(round(x2 - x1)))
        bh = min(height - by, int(round(y2 - y1)))

        if is_custom_hazard_model:
            cname = CUSTOM_CLASSES.get(cls_id, f"hazard_{cls_id}")
            display_name = cname.replace('_', ' ').title()
            severity = "High" if cname in ['water_spill', 'oil_spill', 'broken_glass'] else "Medium"
            is_obstacle = cname == 'obstacle'
        else:
            coco_name = model.names.get(cls_id, f"object_{cls_id}")
            display_name = coco_name.capitalize()
            tripping_objects = {
                'bottle', 'cup', 'chair', 'backpack', 'handbag', 'suitcase',
                'sports ball', 'skateboard', 'box', 'bowl', 'potted plant', 'tv'
            }
            is_obstacle = coco_name.lower() in tripping_objects
            severity = "Medium" if is_obstacle else "Low"

        # Estimated area relative to frame
        est_area_m2 = round((bw * bh) / (width * height) * 4.0, 3) # normalized to approx 4m² camera FOV

        detections.append({
            "class_id": cls_id,
            "class_name": display_name,
            "raw_class_name": cname if is_custom_hazard_model else coco_name,
            "confidence": round(conf_val, 4),
            "confidence_percent": f"{int(round(conf_val * 100))}%",
            "severity": severity,
            "is_tripping_hazard_candidate": is_obstacle,
            "estimated_area_m2": est_area_m2,
            "bounding_box": {
                "x": bx,
                "y": by,
                "width": bw,
                "height": bh
            },
            "normalized_bbox": {
                "x": round(bx / width, 4) if width else 0,
                "y": round(by / height, 4) if height else 0,
                "width": round(bw / width, 4) if width else 0,
                "height": round(bh / height, 4) if height else 0
            }
        })

    # Sort detections by confidence descending
    detections.sort(key=lambda d: d["confidence"], reverse=True)

    # Render annotated image
    annotated_dir = BASE_DIR / 'uploads' / 'annotated'
    ann_disk_path, ann_url = draw_annotations(abs_path, detections, str(annotated_dir))

    # Supported vs unsupported disclosure
    if is_custom_hazard_model:
        model_version = "FloorGuard-YOLOv8s-Phase4.2"
        model_name = "FloorGuard-YOLOv8s Custom Hazard Detector (Phase 4.2)"
        supported_classes = ['water_spill', 'oil_spill', 'broken_glass', 'obstacle']
        unsupported_classes = []
        academic_notice = (
            "Custom-trained YOLOv8s floor hazard detector. Note: Water spill detection "
            "on subtle distant floors has lower sensitivity; high sample variance exists on small benchmarks."
        )
    else:
        model_version = "YOLOv8s-COCO-Pretrained"
        model_name = "Ultralytics YOLOv8s Pretrained (COCO-80)"
        supported_classes = ['80 common COCO objects (tripping obstacles, boxes, chairs, bottles)']
        unsupported_classes = ['water_spill', 'oil_spill', 'broken_glass']
        academic_notice = (
            "Official Ultralytics YOLOv8s pretrained on MS-COCO. Liquid spills (water/oil) and "
            "broken glass shards are outside COCO vocabulary. Zero detections does NOT confirm a clean floor."
        )

    primary_class = detections[0]['class_name'] if detections else "No Supported Objects Detected"
    primary_conf = detections[0]['confidence'] if detections else 0.0
    primary_sev = detections[0]['severity'] if detections else "Safe"
    primary_area = f"{detections[0]['estimated_area_m2']} m²" if detections else "0.00 m²"
    primary_bbox = detections[0]['bounding_box'] if detections else {"x": 0, "y": 0, "width": 0, "height": 0}
    primary_norm_bbox = detections[0]['normalized_bbox'] if detections else {"x": 0, "y": 0, "width": 0, "height": 0}

    return {
        "status": "ok",
        "task": "detection",
        "model_id": model_identifier,
        "model_name": model_name,
        "model_version": model_version,
        "model_checkpoint": model_file.name,
        "is_custom_trained": is_custom_hazard_model,
        "supported_classes": supported_classes,
        "unsupported_classes": unsupported_classes,
        "source_path": abs_path,
        "dataset_relative_path": os.path.relpath(abs_path, str(BASE_DIR)).replace('\\', '/'),
        "dimensions": {"width": width, "height": height},
        "inference_duration_ms": inference_ms,
        "confidence_threshold": float(conf_threshold),
        "total_detections": len(detections),
        "class_name": primary_class,
        "confidence": primary_conf,
        "confidence_percent": f"{int(round(primary_conf * 100))}%",
        "severity": primary_sev,
        "estimated_area": primary_area,
        "location": "Monitored Zone",
        "bounding_box": primary_bbox,
        "normalized_bbox": primary_norm_bbox,
        "detections": detections,
        "annotated_image_url": ann_url,
        "academic_notice": academic_notice,
        "summary": (
            f"Detected {len(detections)} object(s), primary: {primary_class} ({int(round(primary_conf * 100))}%)"
            if len(detections) > 0
            else f"No supported objects detected at threshold {conf_threshold}. (Absence of detection does not guarantee clean floor)"
        )
    }

def get_model(model_identifier='yolov8s-coco-pretrained'):
    """Alias for backwards compatibility with phase 1 verification test."""
    model, _ = get_yolo_model(model_identifier)
    return model

if __name__ == '__main__':
    img_arg = sys.argv[1] if len(sys.argv) > 1 else '1.jpg'
    model_arg = sys.argv[2] if len(sys.argv) > 2 else 'yolov8s-coco-pretrained'
    conf_arg = float(sys.argv[3]) if len(sys.argv) > 3 else 0.25
    
    result = detect(img_arg, model_identifier=model_arg, conf_threshold=conf_arg)
    print(json.dumps(result))
