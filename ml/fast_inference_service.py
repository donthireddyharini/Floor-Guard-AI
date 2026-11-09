#!/usr/bin/env python3
"""
Floor Guard AI - High Speed In-Memory Inference Service
Keeps YOLOv8s floor hazard detector warm in RAM, reducing detection latency
from ~6.0s (cold process spawn + torch load) down to ~50ms (direct warm inference).
"""

import sys
import os
import json
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
import time

# Ensure ml directory is on sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from ml.predict_image import get_model, detect

PORT = 5005

class FastInferenceHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Quiet standard logging to avoid terminal spam
        pass

    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            model, model_path, is_custom = get_model()
            payload = {
                "status": "ok",
                "service": "FloorGuard Fast Inference Daemon",
                "active_model": model_path,
                "is_custom": is_custom,
                "uptime": time.time()
            }
            self.wfile.write(json.dumps(payload).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == '/predict':
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            try:
                data = json.loads(body.decode('utf-8'))
                image_path = data.get('image_path')
                model_type = data.get('model_type', 'detector')
                conf_thresh = float(data.get('conf_threshold', 0.18))
                imgsz = int(data.get('imgsz', 512))
                run_tiling = bool(data.get('run_tiling', False))
                original_filename = data.get('original_filename')

                if not image_path:
                    self.send_response(400)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({"status": "error", "message": "Missing image_path"}).encode('utf-8'))
                    return

                t0 = time.time()
                result = detect(image_path, model_type, conf_thresh, imgsz=imgsz, run_tiling=run_tiling, original_filename=original_filename)
                elapsed_ms = round((time.time() - t0) * 1000, 1)
                result['latency_ms'] = elapsed_ms

                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(result).encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "error", "message": str(e)}).encode('utf-8'))
        elif self.path == '/predict_video':
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            try:
                data = json.loads(body.decode('utf-8'))
                video_path = data.get('video_path')
                num_keyframes = int(data.get('num_keyframes', 8))

                if not video_path:
                    self.send_response(400)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({"status": "error", "message": "Missing video_path"}).encode('utf-8'))
                    return

                from ml.predict_video import analyze_video
                result = analyze_video(video_path, num_keyframes)

                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(result).encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "error", "message": str(e)}).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

def run_service():
    print(f"[FastInferenceService] Pre-warming YOLOv8s Floor Guard model in RAM...")
    t0 = time.time()
    get_model()
    # Warmup with dummy test
    sample_img = os.path.join(BASE_DIR, 'dataset', 'images', 'test', 'hf_pilot_water_spill_0013.jpg')
    if os.path.exists(sample_img):
        detect(sample_img)
    print(f"[FastInferenceService] Model warmed up successfully in {round(time.time() - t0, 2)}s.")
    print(f"[FastInferenceService] Fast Inference Service listening on http://127.0.0.1:{PORT}")

    server = ThreadingHTTPServer(('127.0.0.1', PORT), FastInferenceHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("[FastInferenceService] Shutting down...")
        server.server_close()

if __name__ == '__main__':
    run_service()
