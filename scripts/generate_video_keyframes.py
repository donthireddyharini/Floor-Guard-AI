import cv2, os, json

out_dir = 'floor-guard-ai/public/assets/video_detections'
os.makedirs(out_dir, exist_ok=True)

keyframes_data = [
    {
        'id': 0,
        'timestamp': '00:01',
        'timeRange': '00:00 - 00:02',
        'seekTime': 1.0,
        'frame': 24,
        'frame_file': 'floor-guard-ai/public/assets/gemini_video_frames/sec_01_frame_24.jpg',
        'detected_class': 'Water Spill',
        'confidence': 0.94,
        'severity': 'High',
        'area': '0.38 m²',
        'note': 'Slip Hazard: Liquid water spill puddle spreading across warehouse walkway near caution cone.',
        'bbox': {'x': 18.5, 'y': 63.5, 'width': 64.0, 'height': 20.5}
    },
    {
        'id': 1,
        'timestamp': '00:02',
        'timeRange': '00:02 - 00:03',
        'seekTime': 2.0,
        'frame': 48,
        'frame_file': 'floor-guard-ai/public/assets/gemini_video_frames/sec_02_frame_48.jpg',
        'detected_class': 'Cable / Cord',
        'confidence': 0.96,
        'severity': 'High',
        'area': '0.45 m²',
        'note': 'Trip Hazard: Dense cluster of power and networking cables draped across office corridor floor.',
        'bbox': {'x': 8.0, 'y': 44.0, 'width': 84.0, 'height': 48.0}
    },
    {
        'id': 2,
        'timestamp': '00:03',
        'timeRange': '00:03 - 00:04',
        'seekTime': 3.5,
        'frame': 84,
        'frame_file': 'floor-guard-ai/public/assets/gemini_video_frames/sec_03_frame_72.jpg',
        'detected_class': 'Obstacle / Debris',
        'confidence': 0.93,
        'severity': 'Medium',
        'area': '0.52 m²',
        'note': 'Transit Obstacle: Overturned corrugated shipping cartons toppling and obstructing central aisle corridor.',
        'bbox': {'x': 28.0, 'y': 35.0, 'width': 44.0, 'height': 42.0}
    },
    {
        'id': 3,
        'timestamp': '00:05',
        'timeRange': '00:04 - 00:06',
        'seekTime': 5.0,
        'frame': 120,
        'frame_file': 'floor-guard-ai/public/assets/gemini_video_frames/sec_05_frame_120.jpg',
        'detected_class': 'Broken Glass',
        'confidence': 0.97,
        'severity': 'Critical',
        'area': '0.38 m²',
        'note': 'Laceration & Slip Hazard: Shattered glass jar with spilled viscous food sauce localized on retail tile floor.',
        'bbox': {'x': 26.0, 'y': 40.0, 'width': 54.0, 'height': 46.0}
    },
    {
        'id': 4,
        'timestamp': '00:07',
        'timeRange': '00:06 - 00:08',
        'seekTime': 7.0,
        'frame': 168,
        'frame_file': 'floor-guard-ai/public/assets/gemini_video_frames/sec_07_frame_168.jpg',
        'detected_class': 'Floor Damage',
        'confidence': 0.95,
        'severity': 'High',
        'area': '0.40 m²',
        'note': 'Structural Defect: Deep concrete floor crack and fissure creating severe trip and wheel-strike hazard.',
        'bbox': {'x': 15.0, 'y': 42.0, 'width': 64.0, 'height': 48.0}
    },
    {
        'id': 5,
        'timestamp': '00:09',
        'timeRange': '00:08 - 00:10',
        'seekTime': 9.0,
        'frame': 216,
        'frame_file': 'floor-guard-ai/public/assets/gemini_video_frames/sec_09_frame_216.jpg',
        'detected_class': 'Water Spill',
        'confidence': 0.96,
        'severity': 'Critical',
        'area': '0.42 m²',
        'note': 'Active Slip Incident: High-risk water puddle causing worker loss of footing in warehouse lane.',
        'bbox': {'x': 10.0, 'y': 66.0, 'width': 65.0, 'height': 24.0}
    }
]

for kf in keyframes_data:
    img = cv2.imread(kf['frame_file'])
    if img is not None:
        h, w = img.shape[:2]
        b = kf['bbox']
        x1 = int((b['x'] / 100.0) * w)
        y1 = int((b['y'] / 100.0) * h)
        bw = int((b['width'] / 100.0) * w)
        bh = int((b['height'] / 100.0) * h)
        
        # Save clean thumbnail
        thumb_name = f'thumb_gemini_kf_{kf["id"]}.jpg'
        thumb_path = os.path.join(out_dir, thumb_name)
        cv2.imwrite(thumb_path, img)
        kf['thumb'] = f'/assets/video_detections/{thumb_name}'
        
        # Draw annotated box for preview
        annotated = img.copy()
        cv2.rectangle(annotated, (x1, y1), (x1 + bw, y1 + bh), (0, 0, 255), 3)
        cv2.putText(annotated, f"{kf['detected_class']} {int(kf['confidence']*100)}%", (x1, max(30, y1 - 10)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
        cv2.imwrite(os.path.join(out_dir, f'annotated_gemini_kf_{kf["id"]}.jpg'), annotated)
        print(f"Processed KF {kf['id']}: {kf['detected_class']} at {b}")

with open(os.path.join(out_dir, 'keyframes_meta.json'), 'w') as f:
    json.dump(keyframes_data, f, indent=2)
print("Done saving keyframes!")
