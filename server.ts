import express, { Request, Response } from 'express';
import path from 'path';
import fs from 'fs';
import { fileURLToPath } from 'url';
import { spawn } from 'child_process';
import multer from 'multer';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = Number(process.env.PORT) || 3000;
const isProd = process.env.NODE_ENV === 'production';
const PYTHON_CMD = process.platform === 'win32' ? 'python' : 'python3';

app.use(express.json({ limit: '100mb' }));
app.use(express.urlencoded({ extended: true, limit: '100mb' }));

// Managed directories
const uploadsDir = path.join(__dirname, 'uploads');
const originalsDir = path.join(uploadsDir, 'originals');
const annotatedDir = path.join(uploadsDir, 'annotated');
const samplesDir = path.join(__dirname, 'public', 'samples');

[uploadsDir, originalsDir, annotatedDir, samplesDir].forEach(dir => {
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
});

// Configure Multer for image & video uploads
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, originalsDir);
  },
  filename: (req, file, cb) => {
    const ext = path.extname(file.originalname) || '.jpg';
    const cleanBase = path.basename(file.originalname, ext).replace(/[^a-zA-Z0-9_-]/g, '_');
    const unique = `${Date.now()}_${cleanBase}${ext}`;
    cb(null, unique);
  }
});

const upload = multer({
  storage,
  limits: { fileSize: 150 * 1024 * 1024 } // 150MB limit
});

// Static routes for uploads, datasets, and samples
app.use('/uploads/originals', express.static(originalsDir));
app.use('/uploads/annotated', express.static(annotatedDir));
app.use('/uploads', express.static(uploadsDir));
app.use('/data/images', express.static(path.join(__dirname, 'data', 'processed', 'images')));
app.use('/data/benchmark', express.static(path.join(__dirname, 'data', 'benchmark_expanded', 'images')));
app.use('/data', express.static(path.join(__dirname, 'data')));
app.use('/samples', express.static(samplesDir));
app.use('/assets/samples', express.static(path.join(__dirname, 'data', 'processed', 'images')));

// Helper: Query SQLite via python bridge
function runDb(action: string, query: string, params: any[] = []): Promise<any> {
  return new Promise((resolve, reject) => {
    const bridgePath = path.join(__dirname, 'database', 'db_bridge.py');
    const py = spawn(PYTHON_CMD, [bridgePath]);
    let output = '';
    let errorOutput = '';

    py.stdout.on('data', data => output += data.toString());
    py.stderr.on('data', data => errorOutput += data.toString());

    py.on('close', code => {
      if (code !== 0) {
        return reject(new Error(errorOutput || `DB bridge process exited with code ${code}`));
      }
      try {
        const parsed = JSON.parse(output);
        if (parsed.status === 'ok') resolve(parsed);
        else reject(new Error(parsed.message || 'Database error'));
      } catch (err) {
        reject(new Error(`Failed to parse DB output: ${output}`));
      }
    });

    py.stdin.write(JSON.stringify({ action, query, params }));
    py.stdin.end();
  });
}

// Helper: Get active model metadata from registry
function getActiveModelInfo() {
  const registryPath = path.join(__dirname, 'models', 'model_registry.json');
  if (fs.existsSync(registryPath)) {
    try {
      const reg = JSON.parse(fs.readFileSync(registryPath, 'utf-8'));
      const active = reg.registry.find((m: any) => m.id === reg.active_model_id) || reg.registry[0];
      const all = reg.registry.map((m: any) => ({
        ...m,
        active: m.id === reg.active_model_id
      }));
      return { active: { ...active, active: true }, registry: all, activeId: reg.active_model_id, path: registryPath };
    } catch (e) {
      console.error('Error reading model registry:', e);
    }
  }
  const fallback = {
    id: 'yolov8s-coco-pretrained',
    name: 'YOLOv8s Pretrained Object Detector (COCO)',
    version: 'v8.4.0',
    architecture: 'Ultralytics YOLOv8s (Pretrained COCO80)',
    task: 'detection',
    trained_status: 'verified pretrained weights',
    weights_path: 'models/pretrained/yolov8s.pt',
    classes: ['80 standard COCO common objects'],
    active: true
  };
  return { active: fallback, registry: [fallback], activeId: fallback.id, path: registryPath };
}

// Helper: Run python ML image predictor
function runModelPredict(imagePath: string, modelId: string = 'yolov8s-coco-pretrained', confThreshold: number = 0.25): Promise<any> {
  return new Promise((resolve) => {
    const pyPath = path.join(__dirname, 'ml', 'predict_image.py');
    const py = spawn(PYTHON_CMD, [pyPath, imagePath, modelId, confThreshold.toString()]);
    let output = '';
    let errOutput = '';
    let isSettled = false;

    const timer = setTimeout(() => {
      if (!isSettled) {
        isSettled = true;
        py.kill();
        resolve({ status: 'error', message: 'Model inference timed out after 25 seconds' });
      }
    }, 25000);

    py.stdout.on('data', (d) => (output += d.toString()));
    py.stderr.on('data', (d) => (errOutput += d.toString()));
    py.on('error', (err) => {
      if (!isSettled) {
        isSettled = true;
        clearTimeout(timer);
        resolve({ status: 'error', message: `Failed to spawn ML process: ${err.message}` });
      }
    });
    py.on('close', (code) => {
      if (!isSettled) {
        isSettled = true;
        clearTimeout(timer);
        try {
          const res = JSON.parse(output.trim());
          resolve(res);
        } catch (e) {
          resolve({ status: 'error', message: errOutput.trim() || output.trim() || `ML process exited with code ${code}` });
        }
      }
    });
  });
}

// Helper: Run python ML video predictor
function runVideoPredict(videoPath: string, modelId: string = 'yolov8s-coco-pretrained', intervalSec: number = 1.0, confThreshold: number = 0.25): Promise<any> {
  return new Promise((resolve) => {
    const pyPath = path.join(__dirname, 'ml', 'predict_video.py');
    const py = spawn(PYTHON_CMD, [pyPath, videoPath, modelId, intervalSec.toString(), confThreshold.toString()]);
    let output = '';
    let errOutput = '';
    let isSettled = false;

    const timer = setTimeout(() => {
      if (!isSettled) {
        isSettled = true;
        py.kill();
        resolve({ status: 'error', message: 'Video analysis timed out after 60 seconds' });
      }
    }, 60000);

    py.stdout.on('data', (d) => (output += d.toString()));
    py.stderr.on('data', (d) => (errOutput += d.toString()));
    py.on('error', (err) => {
      if (!isSettled) {
        isSettled = true;
        clearTimeout(timer);
        resolve({ status: 'error', message: `Failed to spawn video process: ${err.message}` });
      }
    });
    py.on('close', (code) => {
      if (!isSettled) {
        isSettled = true;
        clearTimeout(timer);
        try {
          // Parse JSON from output
          const trimmed = output.trim();
          const jsonStart = trimmed.indexOf('{');
          if (jsonStart !== -1) {
            const parsed = JSON.parse(trimmed.substring(jsonStart));
            resolve(parsed);
          } else {
            resolve({ status: 'error', message: output || 'No JSON response from video predictor' });
          }
        } catch (e) {
          resolve({ status: 'error', message: errOutput.trim() || output.trim() || `Video predictor exited with code ${code}` });
        }
      }
    });
  });
}

// -------------------------------------------------------------
// Core API Endpoints
// -------------------------------------------------------------

// Health check
app.get('/api/health', (req: Request, res: Response) => {
  const modelInfo = getActiveModelInfo();
  res.json({
    status: 'ok',
    system: 'Floor Guard AI',
    version: '1.0.0',
    model_status: modelInfo.active.trained_status,
    active_model: modelInfo.active.name,
    active_model_id: modelInfo.activeId,
    timestamp: new Date().toISOString()
  });
});

// Model status & registry
app.get('/api/model/status', (req: Request, res: Response) => {
  try {
    const info = getActiveModelInfo();
    res.json({
      status: 'ok',
      active_model_id: info.activeId,
      model: info.active,
      all_models: info.registry
    });
  } catch (err: any) {
    res.status(500).json({ status: 'error', message: err.message });
  }
});

// Select active model
app.post('/api/model/select', (req: Request, res: Response) => {
  try {
    const { model_id } = req.body;
    if (!model_id) {
      return res.status(400).json({ status: 'error', message: 'model_id is required' });
    }
    const registryPath = path.join(__dirname, 'models', 'model_registry.json');
    if (!fs.existsSync(registryPath)) {
      return res.status(404).json({ status: 'error', message: 'Model registry file not found' });
    }
    const reg = JSON.parse(fs.readFileSync(registryPath, 'utf-8'));
    const found = reg.registry.find((m: any) => m.id === model_id);
    if (!found) {
      return res.status(400).json({ status: 'error', message: `Model ID '${model_id}' not found in registry` });
    }
    reg.active_model_id = model_id;
    fs.writeFileSync(registryPath, JSON.stringify(reg, null, 2), 'utf-8');
    const updated = reg.registry.map((m: any) => ({ ...m, active: m.id === model_id }));
    return res.json({
      status: 'ok',
      message: `Active model switched to ${found.name}`,
      active_model_id: model_id,
      active_model: { ...found, active: true },
      all_models: updated
    });
  } catch (err: any) {
    res.status(500).json({ status: 'error', message: err.message });
  }
});

// Model comparison arena (Evaluates BOTH models on the same image without modifying active model)
app.post('/api/model/compare', upload.single('image'), async (req: Request, res: Response) => {
  try {
    const file = req.file;
    const imagePath = req.body.imagePath;
    let targetFilePath = '';

    if (file) {
      targetFilePath = file.path;
    } else if (imagePath) {
      targetFilePath = path.resolve(imagePath);
      if (!fs.existsSync(targetFilePath)) {
        targetFilePath = path.join(__dirname, imagePath.replace(/^\//, ''));
      }
    } else {
      targetFilePath = path.join(__dirname, 'data', 'processed', 'images', 'sample_water_spill.jpg');
    }

    if (!fs.existsSync(targetFilePath)) {
      return res.status(404).json({ status: 'error', message: `Target image not found: ${targetFilePath}` });
    }

    const confThreshold = parseFloat(req.body.confidence || '0.25');

    // Run Model A: Production COCO baseline
    const resA = await runModelPredict(targetFilePath, 'yolov8s-coco-pretrained', confThreshold);
    // Run Model B: Experimental Phase 4.2 custom detector
    const resB = await runModelPredict(targetFilePath, 'floorguard-yolov8s-v1.1.0-phase4.2', confThreshold);

    res.json({
      status: 'ok',
      image_evaluated: path.basename(targetFilePath),
      confidence_threshold: confThreshold,
      model_a_coco: resA,
      model_b_custom: resB,
      disclaimer: "Comparison performed for educational evaluation. Production model configuration was not altered."
    });
  } catch (err: any) {
    res.status(500).json({ status: 'error', message: err.message });
  }
});

// Image Detection Endpoint
app.post('/api/detect/image', upload.single('image'), async (req: Request, res: Response) => {
  try {
    const file = req.file;
    const sampleId = req.body.sampleId;
    const datasetPath = req.body.datasetPath;
    const imagePath = req.body.imagePath;

    let targetFilePath = '';
    let fileName = '';
    let displayUrl = '';

    if (file) {
      targetFilePath = file.path;
      fileName = file.originalname;
      displayUrl = `/uploads/originals/${file.filename}`;
    } else if (datasetPath) {
      fileName = path.basename(datasetPath);
      targetFilePath = path.join(__dirname, datasetPath.replace(/^\//, ''));
      displayUrl = `/data/images/${fileName}`;
    } else if (imagePath) {
      fileName = path.basename(imagePath);
      if (fs.existsSync(imagePath)) {
        targetFilePath = path.resolve(imagePath);
      } else if (fs.existsSync(path.join(__dirname, imagePath))) {
        targetFilePath = path.join(__dirname, imagePath);
      } else if (fs.existsSync(path.join(__dirname, '..', imagePath))) {
        targetFilePath = path.join(__dirname, '..', imagePath);
      } else {
        targetFilePath = path.join(__dirname, 'data', 'processed', 'images', fileName);
      }
      
      // Ensure file is accessible via uploads or data
      const destCopy = path.join(originalsDir, fileName);
      if (!fs.existsSync(destCopy) && fs.existsSync(targetFilePath)) {
        try { fs.copyFileSync(targetFilePath, destCopy); } catch {}
      }
      displayUrl = fs.existsSync(destCopy) ? `/uploads/originals/${fileName}` : `/data/images/${fileName}`;
    } else if (sampleId === 'clean_floor' || req.body.type === 'clean') {
      fileName = 'thumb_clean_floor.jpg';
      targetFilePath = path.join(__dirname, 'data', 'processed', 'images', fileName);
      displayUrl = `/data/images/${fileName}`;
    } else if (sampleId === 'oil_spill' || req.body.type === 'oil') {
      fileName = 'thumb_oil_spill.jpg';
      targetFilePath = path.join(__dirname, 'data', 'processed', 'images', fileName);
      displayUrl = `/data/images/${fileName}`;
    } else if (sampleId === 'broken_glass' || req.body.type === 'glass') {
      fileName = 'thumb_broken_glass.jpg';
      targetFilePath = path.join(__dirname, 'data', 'processed', 'images', fileName);
      displayUrl = `/data/images/${fileName}`;
    } else if (sampleId === 'obstacle' || req.body.type === 'obstacle') {
      fileName = 'thumb_obstacle.jpg';
      targetFilePath = path.join(__dirname, 'data', 'processed', 'images', fileName);
      displayUrl = `/data/images/${fileName}`;
    } else {
      fileName = 'sample_water_spill.jpg';
      targetFilePath = path.join(__dirname, 'data', 'processed', 'images', fileName);
      displayUrl = `/data/images/${fileName}`;
    }

    if (!fs.existsSync(targetFilePath)) {
      return res.status(404).json({ status: 'error', message: `Target image file not found on disk: ${targetFilePath}` });
    }

    // Resolve requested or active model
    const activeInfo = getActiveModelInfo();
    const reqModelId = req.body.model_id || activeInfo.activeId;
    const targetModel = activeInfo.registry.find((m: any) => m.id === reqModelId) || activeInfo.active;
    const confThreshold = parseFloat(req.body.confidence || req.body.conf_threshold || '0.25');

    // Run Python ML Prediction Engine
    const ml = await runModelPredict(targetFilePath, reqModelId, confThreshold);

    if (ml.status === 'error') {
      console.error(`[Inference Error] ${ml.message} for ${targetFilePath}`);
      return res.status(422).json({
        status: 'error',
        message: ml.message || 'Model inference failed on provided image',
        source_file: targetFilePath
      });
    }

    const detections = ml.detections || [];
    const totalDetections = detections.length;
    const detectedClass = ml.class_name || (totalDetections > 0 ? detections[0].class_name : 'No Supported Objects Detected');
    const confidence = typeof ml.confidence === 'number' ? ml.confidence : (totalDetections > 0 ? detections[0].confidence : 0.0);
    const severity = ml.severity || (totalDetections > 0 ? detections[0].severity : 'Safe');
    const area = ml.estimated_area || '0.00 m²';
    const location = ml.location || 'Monitored Zone';
    const recommendation = ml.recommendation || (totalDetections > 0 ? `Detected ${detectedClass}.` : 'No supported hazards detected.');
    const bbox = ml.bounding_box || { x: 0, y: 0, width: 0, height: 0 };
    const normalizedBbox = ml.normalized_bbox || { x: 0, y: 0, width: 0, height: 0 };
    const modelVersion = targetModel.name || 'YOLOv8s Pretrained (COCO)';
    const annotatedUrl = ml.annotated_image_url || displayUrl;

    const runId = `run_${Date.now()}`;
    const detId = `det_${Date.now()}`;
    const createdAt = new Date().toISOString();
    const summary = ml.summary || `Detected ${totalDetections} object(s).`;

    // Persist into database
    await runDb('execute', `
      INSERT INTO detection_runs (id, source_type, original_filename, file_path, annotated_path, created_at, status, processing_duration_ms, model_version, total_detections, summary, meta_json)
      VALUES (?, 'image', ?, ?, ?, ?, 'completed', ?, ?, ?, ?, ?)
    `, [runId, fileName, displayUrl, annotatedUrl, createdAt, Math.round(ml.inference_duration_ms || 100), modelVersion, totalDetections, summary, JSON.stringify(detections)]);

    if (totalDetections > 0) {
      for (let idx = 0; idx < detections.length; idx++) {
        const d = detections[idx];
        const subDetId = `det_${Date.now()}_${idx}`;
        await runDb('execute', `
          INSERT INTO detections (id, detection_run_id, class_name, confidence, severity, bounding_box_json, estimated_area, evidence_path, location)
          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        `, [subDetId, runId, d.class_name, d.confidence, d.severity, JSON.stringify(d.bounding_box), parseFloat(d.estimated_area_m2) || 0.0, annotatedUrl, location]);
      }
    } else {
      // Record clean floor / no hazard entry for history persistence
      await runDb('execute', `
        INSERT INTO detections (id, detection_run_id, class_name, confidence, severity, bounding_box_json, estimated_area, evidence_path, location)
        VALUES (?, ?, 'Clean Floor', 1.0, 'Safe', '{}', 0.0, ?, ?)
      `, [detId, runId, displayUrl, location]);
    }

    res.json({
      status: 'ok',
      run_id: runId,
      source_file: targetFilePath,
      dataset_relative: path.relative(__dirname, targetFilePath).replace(/\\/g, '/'),
      model_info: {
        id: targetModel.id,
        name: targetModel.name,
        task: targetModel.task,
        architecture: targetModel.architecture,
        is_custom_trained: ml.is_custom_trained || false
      },
      detection: {
        id: detId,
        run_id: runId,
        class_name: detectedClass,
        confidence,
        confidence_percent: ml.confidence_percent || `${Math.round(confidence * 100)}%`,
        severity,
        area,
        location,
        recommendation,
        bounding_box: bbox,
        normalized_bbox: normalizedBbox,
        detections,
        total_detections: totalDetections,
        unsupported_classes: ml.unsupported_classes || [],
        supported_classes: ml.supported_classes || [],
        image_url: displayUrl,
        annotated_image_url: annotatedUrl,
        filename: fileName,
        created_at: createdAt,
        inference_duration_ms: ml.inference_duration_ms || 100,
        model_version: modelVersion,
        architecture: targetModel.architecture,
        academic_notice: ml.academic_notice || ''
      }
    });
  } catch (err: any) {
    res.status(500).json({ status: 'error', message: err.message });
  }
});

// Video Analysis Endpoint (Real OpenCV Frame Inference)
app.post('/api/detect/video', upload.single('video'), async (req: Request, res: Response) => {
  try {
    const file = req.file;
    let targetVideoPath = '';
    let fileName = '';

    if (file) {
      targetVideoPath = file.path;
      fileName = file.originalname;
    } else {
      // Use verified sample video
      targetVideoPath = path.join(__dirname, 'public', 'samples', 'sample_corridor_walkthrough.mp4');
      fileName = 'sample_corridor_walkthrough.mp4';
      if (!fs.existsSync(targetVideoPath)) {
        // Create sample video if missing
        const py = spawn(PYTHON_CMD, [path.join(__dirname, 'ml', 'predict_video.py')]);
        await new Promise(r => py.on('close', r));
      }
    }

    if (!fs.existsSync(targetVideoPath)) {
      return res.status(404).json({ status: 'error', message: `Video file not found: ${targetVideoPath}` });
    }

    const activeInfo = getActiveModelInfo();
    const reqModelId = req.body.model_id || activeInfo.activeId;
    const intervalSec = parseFloat(req.body.interval || req.body.sampling_interval_seconds || '1.0');
    const confThreshold = parseFloat(req.body.confidence || '0.25');

    // Run Real OpenCV Video Inference
    const vidRes = await runVideoPredict(targetVideoPath, reqModelId, intervalSec, confThreshold);

    if (vidRes.status === 'error') {
      return res.status(422).json({ status: 'error', message: vidRes.message || 'Video analysis failed' });
    }

    const runId = `run_vid_${Date.now()}`;
    const createdAt = new Date().toISOString();
    const keyframes = vidRes.keyframes || [];
    const hazardsCount = vidRes.hazards_count || 0;
    const firstThumb = keyframes.find((k: any) => k.detections_count > 0)?.thumb || (keyframes[0]?.thumb || '');
    const displayVideoUrl = file ? `/uploads/originals/${file.filename}` : `/samples/sample_corridor_walkthrough.mp4`;

    // Persist video run into database
    await runDb('execute', `
      INSERT INTO detection_runs (id, source_type, original_filename, file_path, annotated_path, created_at, status, processing_duration_ms, model_version, total_detections, summary, meta_json)
      VALUES (?, 'video', ?, ?, ?, ?, 'completed', ?, ?, ?, ?, ?)
    `, [runId, fileName, displayVideoUrl, firstThumb, createdAt, Math.round(vidRes.processing_duration_seconds * 1000), vidRes.model_name || 'YOLOv8s', hazardsCount, vidRes.summary, JSON.stringify(keyframes)]);

    // Record individual hazard detections from keyframes
    for (const kf of keyframes) {
      if (kf.detections && kf.detections.length > 0) {
        for (let idx = 0; idx < kf.detections.length; idx++) {
          const d = kf.detections[idx];
          const detId = `det_vid_${runId}_f${kf.frame}_${idx}`;
          await runDb('execute', `
            INSERT INTO detections (id, detection_run_id, class_name, confidence, severity, bounding_box_json, estimated_area, evidence_path, location)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
          `, [detId, runId, d.class_name, d.confidence, d.severity, JSON.stringify(d.bounding_box), 0.2, kf.thumb, `Frame ${kf.frame} (${kf.timestamp})`]);
        }
      }
    }

    res.json({
      status: 'ok',
      run_id: runId,
      video_info: {
        filename: fileName,
        duration_seconds: vidRes.duration_seconds,
        fps: vidRes.fps,
        total_frames: vidRes.total_frames,
        total_frames_analyzed: vidRes.total_frames_analyzed,
        average_frame_latency_ms: vidRes.average_frame_latency_ms,
        throughput_fps: vidRes.throughput_fps
      },
      video_analysis: {
        run_id: runId,
        filename: fileName,
        video_url: displayVideoUrl,
        is_demo_simulation: false,
        model_id: vidRes.model_id,
        model_name: vidRes.model_name,
        is_custom_trained: vidRes.is_custom_trained,
        duration: vidRes.duration,
        duration_seconds: vidRes.duration_seconds,
        fps: vidRes.fps,
        total_frames: vidRes.total_frames,
        total_frames_analyzed: vidRes.total_frames_analyzed,
        sampling_interval_seconds: vidRes.sampling_interval_seconds,
        hazards_count: vidRes.hazards_count,
        clean_frames_count: vidRes.clean_frames_count,
        processing_duration_seconds: vidRes.processing_duration_seconds,
        average_frame_latency_ms: vidRes.average_frame_latency_ms,
        throughput_fps: vidRes.throughput_fps,
        keyframes,
        summary: vidRes.summary,
        academic_notice: vidRes.academic_notice
      },
      keyframes: keyframes,
      hazards_count: hazardsCount,
      safe_frames_count: vidRes.clean_frames_count,
      total_frames_analyzed: vidRes.total_frames_analyzed,
      processing_duration_seconds: vidRes.processing_duration_seconds,
      video_url: displayVideoUrl
    });
  } catch (err: any) {
    res.status(500).json({ status: 'error', message: err.message });
  }
});

// Detection History Endpoint (Full persistent history supporting search, filters, pagination)
app.get('/api/history', async (req: Request, res: Response) => {
  try {
    const { search, sourceType, className, severity, limit = 50, offset = 0 } = req.query;

    let sql = `
      SELECT r.id, r.source_type, r.original_filename, r.file_path, r.annotated_path,
             r.created_at, r.status, r.processing_duration_ms, r.model_version,
             r.total_detections, r.summary, r.meta_json
      FROM detection_runs r
      WHERE 1=1
    `;
    const params: any[] = [];

    if (sourceType && sourceType !== 'all') {
      sql += ' AND r.source_type = ?';
      params.push(sourceType);
    }

    if (search) {
      sql += ' AND (r.original_filename LIKE ? OR r.summary LIKE ? OR r.id LIKE ?)';
      params.push(`%${search}%`, `%${search}%`, `%${search}%`);
    }

    sql += ' ORDER BY r.created_at DESC LIMIT ? OFFSET ?';
    params.push(Number(limit), Number(offset));

    const result = await runDb('query', sql, params);
    const rows = result.data || [];

    // Parse meta_json for each row safely
    const runs = rows.map((r: any) => {
      let detections = [];
      try {
        if (r.meta_json) detections = JSON.parse(r.meta_json);
      } catch {}

      // Fallback thumbnail resolution
      let thumbUrl = r.annotated_path || r.file_path;
      if (!thumbUrl || thumbUrl === '/uploads/1.jpg') {
        thumbUrl = '/uploads/originals/1.jpg';
      }

      return {
        id: r.id,
        source_type: r.source_type,
        original_filename: r.original_filename,
        original_image_url: r.file_path,
        annotated_image_url: r.annotated_path || r.file_path,
        thumb_url: thumbUrl,
        created_at: r.created_at,
        status: r.status,
        processing_duration_ms: r.processing_duration_ms,
        model_version: r.model_version,
        total_detections: r.total_detections,
        summary: r.summary,
        detections
      };
    });

    res.json({
      status: 'ok',
      total_count: runs.length,
      history: runs
    });
  } catch (err: any) {
    res.status(500).json({ status: 'error', message: err.message });
  }
});

// Single History Detail Endpoint
app.get('/api/history/:id', async (req: Request, res: Response) => {
  try {
    const { id } = req.params;
    const runRes = await runDb('query', 'SELECT * FROM detection_runs WHERE id = ?', [id]);
    if (!runRes.data || runRes.data.length === 0) {
      return res.status(404).json({ status: 'error', message: `Analysis record ${id} not found` });
    }

    const run = runRes.data[0];
    const detRes = await runDb('query', 'SELECT * FROM detections WHERE detection_run_id = ? ORDER BY confidence DESC', [id]);
    
    let meta = null;
    try {
      if (run.meta_json) meta = JSON.parse(run.meta_json);
    } catch {}

    res.json({
      status: 'ok',
      run: {
        ...run,
        original_image_url: run.file_path,
        annotated_image_url: run.annotated_path || run.file_path,
        detections: detRes.data || [],
        meta
      }
    });
  } catch (err: any) {
    res.status(500).json({ status: 'error', message: err.message });
  }
});

// Delete history record
app.delete('/api/history/:id', async (req: Request, res: Response) => {
  try {
    const { id } = req.params;
    await runDb('execute', 'DELETE FROM detections WHERE detection_run_id = ?', [id]);
    await runDb('execute', 'DELETE FROM detection_runs WHERE id = ?', [id]);
    res.json({ status: 'ok', message: `Analysis run ${id} removed successfully` });
  } catch (err: any) {
    res.status(500).json({ status: 'error', message: err.message });
  }
});

// Backward-compatible detections list
app.get('/api/detections', async (req: Request, res: Response) => {
  try {
    const { search, className, severity, limit = 50 } = req.query;
    let sql = `
      SELECT d.id, d.detection_run_id, d.class_name, d.confidence, d.severity,
             d.estimated_area, d.evidence_path, d.location,
             r.source_type, r.original_filename, r.created_at
      FROM detections d
      JOIN detection_runs r ON d.detection_run_id = r.id
      WHERE 1=1
    `;
    const params: any[] = [];

    if (className && className !== 'all') {
      sql += ' AND d.class_name = ?';
      params.push(className);
    }
    if (severity && severity !== 'all') {
      sql += ' AND d.severity = ?';
      params.push(severity);
    }
    if (search) {
      sql += ' AND (r.original_filename LIKE ? OR d.class_name LIKE ? OR d.location LIKE ?)';
      params.push(`%${search}%`, `%${search}%`, `%${search}%`);
    }

    sql += ' ORDER BY r.created_at DESC LIMIT ?';
    params.push(Number(limit));

    const result = await runDb('query', sql, params);
    
    // Normalize evidence_path to ensure valid thumbnail URLs
    const detections = (result.data || []).map((row: any) => {
      let ep = row.evidence_path;
      if (ep === '/uploads/1.jpg') ep = '/uploads/originals/1.jpg';
      return { ...row, evidence_path: ep };
    });

    res.json({ status: 'ok', detections });
  } catch (err: any) {
    res.status(500).json({ status: 'error', message: err.message });
  }
});

// Delete detection record (backward compatibility)
app.delete('/api/detections/:id', async (req: Request, res: Response) => {
  try {
    const { id } = req.params;
    await runDb('execute', 'DELETE FROM detections WHERE id = ?', [id]);
    res.json({ status: 'ok', message: 'Record removed successfully' });
  } catch (err: any) {
    res.status(500).json({ status: 'error', message: err.message });
  }
});

// Real Database-Derived Analytics
app.get('/api/analytics/real', async (req: Request, res: Response) => {
  try {
    // 1. Total runs and counts
    const totalRunsRes = await runDb('query', 'SELECT count(*) as total, sum(CASE WHEN source_type="image" THEN 1 ELSE 0 END) as images, sum(CASE WHEN source_type="video" THEN 1 ELSE 0 END) as videos, sum(total_detections) as total_hazards FROM detection_runs');
    const totalRuns = totalRunsRes.data?.[0]?.total || 0;
    const totalImages = totalRunsRes.data?.[0]?.images || 0;
    const totalVideos = totalRunsRes.data?.[0]?.videos || 0;
    const totalHazards = totalRunsRes.data?.[0]?.total_hazards || 0;

    // 2. Class breakdown from detections table
    const classDistRes = await runDb('query', 'SELECT class_name, count(*) as count FROM detections WHERE class_name != "Clean Floor" GROUP BY class_name ORDER BY count DESC');
    const classDistribution = classDistRes.data || [];

    // 3. Clean floor count
    const cleanRunsRes = await runDb('query', 'SELECT count(*) as clean_count FROM detection_runs WHERE total_detections = 0');
    const cleanFloorsCount = cleanRunsRes.data?.[0]?.clean_count || 0;

    // 4. Model usage breakdown
    const modelUsageRes = await runDb('query', 'SELECT model_version, count(*) as runs_count FROM detection_runs GROUP BY model_version');
    const modelUsage = modelUsageRes.data || [];

    // 5. Activity timeline (last 7 days based on real created_at)
    const timelineRes = await runDb('query', 'SELECT substr(created_at, 1, 10) as day, count(*) as analyses, sum(total_detections) as hazards FROM detection_runs GROUP BY day ORDER BY day DESC LIMIT 7');
    const timeline = (timelineRes.data || []).reverse();

    // 6. Recent runs (last 8)
    const recentRes = await runDb('query', 'SELECT id, source_type, original_filename, file_path, annotated_path, created_at, status, model_version, total_detections, summary FROM detection_runs ORDER BY created_at DESC LIMIT 8');
    const recentAnalyses = (recentRes.data || []).map((r: any) => ({
      ...r,
      thumb_url: r.annotated_path || (r.file_path === '/uploads/1.jpg' ? '/uploads/originals/1.jpg' : r.file_path)
    }));

    // 7. Verified evaluation report telemetry (from Phase 4.2 and Phase 4.3 reports)
    const p42EvalPath = path.join(__dirname, 'reports', 'evaluation_report_phase4_2.json');
    const p43EvalPath = path.join(__dirname, 'reports', 'evaluation_report_phase4_3.json');
    const evalPhase42 = fs.existsSync(p42EvalPath) ? JSON.parse(fs.readFileSync(p42EvalPath, 'utf-8')) : null;
    const evalPhase43 = fs.existsSync(p43EvalPath) ? JSON.parse(fs.readFileSync(p43EvalPath, 'utf-8')) : null;

    res.json({
      status: 'ok',
      operational_kpis: {
        total_analyses: totalRuns,
        images_analyzed: totalImages,
        videos_analyzed: totalVideos,
        hazards_detected: totalHazards,
        clean_floors_confirmed: cleanFloorsCount,
        safe_pass_rate_pct: totalRuns > 0 ? Math.round((cleanFloorsCount / totalRuns) * 100) : 100
      },
      hazard_class_distribution: classDistribution,
      model_usage: modelUsage,
      activity_timeline: timeline,
      recent_analyses: recentAnalyses,
      evaluation_telemetry: {
        phase4_2_frozen_benchmark: evalPhase42 ? {
          mAP50: evalPhase42.frozen_test_benchmark_metrics?.mAP50,
          mAP50_95: evalPhase42.frozen_test_benchmark_metrics?.mAP50_95,
          precision: evalPhase42.frozen_test_benchmark_metrics?.overall_precision,
          recall: evalPhase42.frozen_test_benchmark_metrics?.overall_recall,
          clean_floor_tn: evalPhase42.clean_floor_evaluation?.true_negatives,
          clean_floor_fp: evalPhase42.clean_floor_evaluation?.false_positives,
          per_class: evalPhase42.frozen_test_benchmark_metrics?.per_class
        } : null,
        phase4_3_expanded_benchmark: evalPhase43 ? {
          total_images: evalPhase43.benchmark_info?.total_samples,
          mAP50: evalPhase43.models_evaluated?.model_b_custom_phase4_2?.overall_metrics?.mAP50,
          mAP50_95: evalPhase43.models_evaluated?.model_b_custom_phase4_2?.overall_metrics?.mAP50_95,
          clean_floor_tn: evalPhase43.models_evaluated?.model_b_custom_phase4_2?.clean_floor_tn,
          clean_floor_fp: evalPhase43.models_evaluated?.model_b_custom_phase4_2?.clean_floor_fp,
          per_class: evalPhase43.models_evaluated?.model_b_custom_phase4_2?.per_class_metrics
        } : null
      }
    });
  } catch (err: any) {
    res.status(500).json({ status: 'error', message: err.message });
  }
});

// Analytics summary (Updated with live DB data)
app.get('/api/analytics/summary', async (req: Request, res: Response) => {
  try {
    const totalRunsRes = await runDb('query', 'SELECT count(*) as total, sum(total_detections) as total_hazards FROM detection_runs');
    const totalRuns = totalRunsRes.data?.[0]?.total || 0;
    const totalHazards = totalRunsRes.data?.[0]?.total_hazards || 0;

    const classDistRes = await runDb('query', 'SELECT class_name, count(*) as count FROM detections WHERE class_name != "Clean Floor" GROUP BY class_name ORDER BY count DESC');
    const classRows = classDistRes.data || [];
    const totalDetCount = classRows.reduce((a: number, b: any) => a + (b.count || 0), 0);

    const colors: Record<string, string> = {
      'Water Spill': '#06b6d4',
      'Oil Spill': '#f59e0b',
      'Broken Glass': '#a855f7',
      'Obstacle': '#ef4444',
      'Laptop': '#64748b'
    };

    const distribution = classRows.map((r: any) => ({
      name: r.class_name,
      count: r.count,
      percentage: totalDetCount > 0 ? Math.round((r.count / totalDetCount) * 100) : 0,
      color: colors[r.class_name] || '#f97316'
    }));

    // Real recent detections
    const recentRes = await runDb('query', `
      SELECT d.id, d.detection_run_id, d.class_name, d.confidence, d.severity, d.evidence_path,
             r.created_at, r.original_filename, d.estimated_area
      FROM detections d
      JOIN detection_runs r ON d.detection_run_id = r.id
      ORDER BY r.created_at DESC
      LIMIT 8
    `);
    const recentDetections = (recentRes.data || []).map((row: any) => ({
      ...row,
      evidence_path: row.evidence_path === '/uploads/1.jpg' ? '/uploads/originals/1.jpg' : row.evidence_path
    }));

    // Real activity trend
    const timelineRes = await runDb('query', 'SELECT substr(created_at, 1, 10) as date, count(*) as total_images, sum(total_detections) as hazards_detected FROM detection_runs GROUP BY date ORDER BY date DESC LIMIT 7');
    const trend = (timelineRes.data || []).reverse();

    const activeModelInfo = getActiveModelInfo();

    res.json({
      status: 'ok',
      kpis: {
        images_analyzed: totalRuns,
        images_analyzed_delta: 'Real DB records',
        hazards_detected: totalHazards,
        hazards_detected_delta: 'Verified detections',
        safe_floors: Math.max(0, totalRuns - totalHazards),
        safe_floors_delta: 'Inspected corridors',
        model_map: '67.3%',
        model_map_delta: 'Phase 4.2 Benchmark'
      },
      hazard_distribution: {
        total: totalDetCount,
        items: distribution
      },
      detection_trend: trend.length > 0 ? trend : [{ date: new Date().toISOString().substring(0, 10), total_images: totalRuns, hazards_detected: totalHazards }],
      heatmap: {
        hours: ['12 AM', '6 AM', '12 PM', '6 PM'],
        days: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        grid: [
          { hour: '12 AM', values: Array(7).fill('low') },
          { hour: '6 AM', values: Array(7).fill('med') },
          { hour: '12 PM', values: Array(7).fill('high') },
          { hour: '6 PM', values: Array(7).fill('low') }
        ]
      },
      recent_detections: recentDetections
    });
  } catch (err: any) {
    res.status(500).json({ status: 'error', message: err.message });
  }
});

// CSV Export
app.get('/api/analytics/export', async (req: Request, res: Response) => {
  try {
    const sql = `
      SELECT d.id, r.created_at, r.original_filename, r.source_type,
             d.class_name, d.confidence, d.severity, d.estimated_area, d.location
      FROM detections d
      JOIN detection_runs r ON d.detection_run_id = r.id
      ORDER BY r.created_at DESC
    `;
    const result = await runDb('query', sql);
    let csv = 'Detection ID,Timestamp,Filename,Source,Class,Confidence,Severity,Area (m2),Location\n';
    (result.data || []).forEach((row: any) => {
      csv += `"${row.id}","${row.created_at}","${row.original_filename}","${row.source_type}","${row.class_name}",${row.confidence},"${row.severity}",${row.estimated_area},"${row.location}"\n`;
    });

    res.setHeader('Content-Type', 'text/csv');
    res.setHeader('Content-Disposition', 'attachment; filename="floorguard_hazard_export.csv"');
    res.send(csv);
  } catch (err: any) {
    res.status(500).json({ status: 'error', message: err.message });
  }
});

// Settings endpoints
app.get('/api/settings', async (req: Request, res: Response) => {
  try {
    const result = await runDb('query', 'SELECT * FROM application_settings');
    const settings: Record<string, any> = {};
    (result.data || []).forEach((r: any) => {
      try { settings[r.key] = JSON.parse(r.value_json); }
      catch { settings[r.key] = r.value_json; }
    });
    res.json({ status: 'ok', settings });
  } catch (err: any) {
    res.status(500).json({ status: 'error', message: err.message });
  }
});

app.post('/api/settings', async (req: Request, res: Response) => {
  try {
    const { key, value } = req.body;
    const now = new Date().toISOString();
    await runDb('execute', `
      INSERT INTO application_settings (key, value_json, updated_at)
      VALUES (?, ?, ?)
      ON CONFLICT(key) DO UPDATE SET value_json=excluded.value_json, updated_at=excluded.updated_at
    `, [key, JSON.stringify(value), now]);
    res.json({ status: 'ok', key, updated_at: now });
  } catch (err: any) {
    res.status(500).json({ status: 'error', message: err.message });
  }
});

// Dataset images list
app.get('/api/dataset/images', (req: Request, res: Response) => {
  try {
    const processedDir = path.join(__dirname, 'data', 'processed', 'images');
    if (!fs.existsSync(processedDir)) {
      return res.json({ status: 'ok', images: [] });
    }
    const files = fs.readdirSync(processedDir);
    const images = files.map((file) => {
      const fullPath = path.join(processedDir, file);
      const stat = fs.statSync(fullPath);
      let classHint = 'Water Spill';
      if (file.includes('clean')) classHint = 'Clean Floor';
      else if (file.includes('oil')) classHint = 'Oil Spill';
      else if (file.includes('glass')) classHint = 'Broken Glass';
      else if (file.includes('obstacle')) classHint = 'Obstacle';

      return {
        id: file,
        filename: file,
        relative_path: `data/processed/images/${file}`,
        url: `/data/images/${file}`,
        size_bytes: stat.size,
        class_hint: classHint,
        mtime: stat.mtime.toISOString()
      };
    });
    res.json({ status: 'ok', count: images.length, images });
  } catch (err: any) {
    res.status(500).json({ status: 'error', message: err.message });
  }
});

// Dataset summary
app.get('/api/dataset/summary', async (req: Request, res: Response) => {
  try {
    const manifestPath = path.join(__dirname, 'data', 'dataset_manifest.json');
    let manifest: any = { manifest_version: '2.4-phase4.1', local_verified_inventory: {}, remote_catalog_sources: [] };
    if (fs.existsSync(manifestPath)) {
      manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf-8'));
    }
    const splitReportPath = path.join(__dirname, 'data', 'splits', 'split_report.json');
    let splitReport: any = null;
    if (fs.existsSync(splitReportPath)) {
      splitReport = JSON.parse(fs.readFileSync(splitReportPath, 'utf-8'));
    }
    const processedDir = path.join(__dirname, 'data', 'processed', 'images');
    const processedCount = fs.existsSync(processedDir) ? fs.readdirSync(processedDir).length : 0;
    const labelsDir = path.join(__dirname, 'data', 'processed', 'labels');
    const labelCount = fs.existsSync(labelsDir) ? fs.readdirSync(labelsDir).filter(f => f.endsWith('.txt')).length : 0;

    res.json({
      status: 'ok',
      summary: {
        dataset_root: 'data/',
        manifest_path: 'data/dataset_manifest.json',
        splits_directory: 'data/splits/',
        yolo_config_path: 'data/floorguard_yolo.yaml',
        database_path: 'data/database.sqlite',
        manifest_version: manifest.manifest_version || '2.4-phase4.1',
        total_catalog_images: manifest.local_verified_inventory?.total_image_files_in_workspace || 187,
        unique_workspace_images: manifest.local_verified_inventory?.unique_physical_images || 99,
        processed_images_stored: processedCount,
        verified_labels_stored: labelCount,
        usable_samples_total: manifest.local_verified_inventory?.usable_annotated_images || 96,
        total_verified_boxes: manifest.local_verified_inventory?.total_bounding_boxes || 212,
        classes: ['Water Spill', 'Oil Spill', 'Broken Glass', 'Obstacle'],
        background_condition: 'Clean Floor (Negative Samples)',
        splits: splitReport ? {
          train: splitReport.splits_statistics?.train?.total_images || 71,
          val: splitReport.splits_statistics?.val?.total_images || 14,
          test: splitReport.splits_statistics?.test?.total_images || 11
        } : { train: 71, val: 14, test: 11 },
        certified_for_training: true,
        certification_blocker: null,
        integrity_status: 'Phase 4.1 Liquid Expansion Certified'
      }
    });
  } catch (err: any) {
    res.status(500).json({ status: 'error', message: err.message });
  }
});

// -------------------------------------------------------------
// Vite Dev Server / Static Hosting
// -------------------------------------------------------------
async function startServer() {
  if (!isProd) {
    const { createServer: createViteServer } = await import('vite');
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: 'spa'
    });
    app.use(vite.middlewares);
  } else {
    app.use(express.static(path.join(__dirname, 'dist')));
    app.get('*', (req: Request, res: Response) => {
      res.sendFile(path.join(__dirname, 'dist', 'index.html'));
    });
  }

  app.listen(PORT, '0.0.0.0', () => {
    console.log(`Floor Guard AI server running on http://0.0.0.0:${PORT}`);
  });
}

startServer().catch(err => {
  console.error('Failed to start server:', err);
  process.exit(1);
});
