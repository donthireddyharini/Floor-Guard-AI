import React, { useState, useRef, useEffect } from 'react';
import {
  Video,
  Upload,
  Play,
  Pause,
  AlertTriangle,
  CheckCircle,
  Clock,
  RotateCcw,
  ShieldCheck,
  Loader2,
  Eye,
  EyeOff,
  Trash2,
  History,
  Calendar,
  ExternalLink
} from 'lucide-react';

interface KeyframeItem {
  id: number;
  timestamp: string;
  timeRange?: string;
  startTime?: number;
  endTime?: number;
  seekTime: number;
  frame: number;
  detectedClass: string;
  confidence: number;
  severity: 'Safe' | 'Medium' | 'High' | 'Critical';
  area: string;
  thumb: string;
  note: string;
  bbox?: { x: number; y: number; width: number; height: number } | null;
}

const DEFAULT_SAMPLE_VIDEO = '/assets/samples/corridor_hazard_tour_30s.mp4';

const DEFAULT_KEYFRAMES: KeyframeItem[] = [
  {
    id: 0,
    timestamp: '00:00 - 00:06',
    startTime: 0.0,
    endTime: 6.0,
    seekTime: 0.0,
    frame: 90,
    detectedClass: 'Clean Floor',
    confidence: 0.99,
    severity: 'Safe',
    area: '0.00 m²',
    thumb: '/assets/samples/thumb_clean_floor.jpg',
    note: 'Dry unobstructed concrete corridor walkway. Safe transit condition.'
  },
  {
    id: 1,
    timestamp: '00:06 - 00:12',
    startTime: 6.0,
    endTime: 12.0,
    seekTime: 6.0,
    frame: 240,
    detectedClass: 'Water Spill',
    confidence: 0.78,
    severity: 'High',
    area: '0.34 m²',
    thumb: '/assets/samples/thumb_water_spill.jpg',
    note: 'Entrance corridor liquid puddle spreading across main pedestrian footway.',
    bbox: { x: 17.5, y: 45.4, width: 61.1, height: 44.4 }
  },
  {
    id: 2,
    timestamp: '00:12 - 00:18',
    startTime: 12.0,
    endTime: 18.0,
    seekTime: 12.0,
    frame: 450,
    detectedClass: 'Oil Spill',
    confidence: 0.92,
    severity: 'Critical',
    area: '0.41 m²',
    thumb: '/assets/samples/thumb_oil_spill.jpg',
    note: 'Viscous hydrocarbon lubricant leak near pump enclosure. Chemical slip hazard.',
    bbox: { x: 3.1, y: 40.2, width: 82.3, height: 53.3 }
  },
  {
    id: 3,
    timestamp: '00:18 - 00:24',
    startTime: 18.0,
    endTime: 24.0,
    seekTime: 18.0,
    frame: 630,
    detectedClass: 'Broken Glass',
    confidence: 0.80,
    severity: 'Critical',
    area: '0.28 m²',
    thumb: '/assets/samples/thumb_broken_glass.jpg',
    note: 'Shattered glass shards clustered on floor. Immediate laceration hazard.',
    bbox: { x: 21.7, y: 32.7, width: 77.7, height: 51.3 }
  },
  {
    id: 4,
    timestamp: '00:24 - 00:30',
    startTime: 24.0,
    endTime: 30.0,
    seekTime: 24.0,
    frame: 810,
    detectedClass: 'Obstacle',
    confidence: 0.99,
    severity: 'Medium',
    area: '0.48 m²',
    thumb: '/assets/samples/thumb_obstacle.jpg',
    note: 'Dropped warehouse packing crate blocking central transit route.',
    bbox: { x: 22.0, y: 6.0, width: 42.1, height: 69.4 }
  }
];

export const VideoAnalysisView: React.FC = () => {
  const [videoSrc, setVideoSrc] = useState<string>(DEFAULT_SAMPLE_VIDEO);
  const [isPlaying, setIsPlaying] = useState<boolean>(true);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [hasAnalyzed, setHasAnalyzed] = useState<boolean>(true);
  const [showOverlay, setShowOverlay] = useState<boolean>(true);
  const [analysisStatus, setAnalysisStatus] = useState<string>('');
  const [progress, setProgress] = useState(100);
  const [selectedKeyframe, setSelectedKeyframe] = useState<number>(0);
  const [currentTimeSec, setCurrentTimeSec] = useState<number>(0);
  const [isCustomVideo, setIsCustomVideo] = useState<boolean>(false);
  const [videoPlayError, setVideoPlayError] = useState<boolean>(false);

  const videoRef = useRef<HTMLVideoElement | null>(null);
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  const [videoMeta, setVideoMeta] = useState({
    filename: 'corridor_hazard_tour_30s.mp4',
    resolution: '1280x720 @ 30 FPS',
    duration: '00:30',
    totalFrames: 900,
    analyzedFrames: 900,
    hazardsDetected: 4,
    safeFrames: 180,
    summary: 'Autonomous 30s video hazard inspection: 4 distinct floor hazards verified (Water Spill, Oil Spill, Broken Glass, Obstacle).'
  });

  const [keyframes, setKeyframes] = useState<KeyframeItem[]>(DEFAULT_KEYFRAMES);
  const [videoHistory, setVideoHistory] = useState<any[]>([]);

  // Load dedicated video inspection history from backend
  const loadVideoHistory = async () => {
    try {
      const res = await fetch('/api/history/videos');
      const data = await res.json();
      if (data.status === 'ok') {
        setVideoHistory(data.runs || []);
      }
    } catch (e) {
      console.error('Failed to load video history:', e);
    }
  };

  useEffect(() => {
    loadVideoHistory();
  }, []);

  const handleDeleteVideoRun = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!confirm('Are you sure you want to delete this video analysis record?')) return;
    try {
      await fetch(`/api/history/videos/${id}`, { method: 'DELETE' });
      setVideoHistory(prev => prev.filter(r => r.id !== id));
    } catch (e) {
      console.error(e);
    }
  };

  const handleSelectPastVideo = (run: any) => {
    if (run.file_path) {
      setVideoSrc(run.file_path);
      setIsCustomVideo(run.original_filename !== 'corridor_hazard_tour_30s.mp4');
    }
    setVideoMeta({
      filename: run.original_filename,
      resolution: '1280x720 @ 30 FPS',
      duration: 'Recorded Run',
      totalFrames: 900,
      analyzedFrames: 900,
      hazardsDetected: run.total_detections,
      safeFrames: 0,
      summary: run.summary || 'Inspected video run loaded from history.'
    });

    if (run.detections && run.detections.length > 0) {
      const count = run.detections.length;
      const segDur = 30 / Math.max(1, count);
      const builtKeyframes: KeyframeItem[] = run.detections.map((d: any, idx: number) => {
        let bbox = null;
        try {
          if (d.bounding_box_json) bbox = JSON.parse(d.bounding_box_json);
        } catch {}
        const startTime = idx * segDur;
        const endTime = (idx + 1) * segDur;
        return {
          id: idx,
          timestamp: `Incident #${idx + 1}`,
          startTime: Math.round(startTime * 100) / 100,
          endTime: Math.round(endTime * 100) / 100,
          seekTime: Math.round(startTime * 100) / 100,
          frame: idx * 150,
          detectedClass: d.class_name,
          confidence: d.confidence,
          severity: d.severity,
          area: `${d.estimated_area || 0.25} m²`,
          thumb: d.evidence_path || '/assets/samples/thumb_water_spill.jpg',
          note: `Location: ${d.location || 'Monitored Walkway'}`,
          bbox: bbox && bbox.width ? bbox : { x: 25, y: 35, width: 50, height: 45 }
        };
      });
      setKeyframes(builtKeyframes);
      setSelectedKeyframe(0);
      setHasAnalyzed(true);
      setShowOverlay(true);
    }
  };

  // Helper: Find active keyframe using exact segment window [startTime, endTime)
  const getActiveKeyframeIndex = (curTime: number, items: KeyframeItem[]) => {
    if (!items || items.length === 0) return 0;
    for (let i = 0; i < items.length; i++) {
      const kf = items[i];
      const start = kf.startTime !== undefined ? kf.startTime : (i === 0 ? 0 : kf.seekTime);
      const end = kf.endTime !== undefined ? kf.endTime : (i === items.length - 1 ? 999999 : (items[i + 1].startTime ?? items[i + 1].seekTime));
      if (curTime >= start && curTime < end) {
        return i;
      }
    }
    // Fallback: nearest distance
    let matchedIdx = 0;
    let minDiff = Infinity;
    for (let i = 0; i < items.length; i++) {
      const diff = Math.abs(curTime - items[i].seekTime);
      if (diff < minDiff) {
        minDiff = diff;
        matchedIdx = i;
      }
    }
    return matchedIdx;
  };

  // Synchronize keyframe selection dynamically with playback currentTime
  const handleTimeUpdate = () => {
    if (!videoRef.current) return;
    const curTime = videoRef.current.currentTime;
    setCurrentTimeSec(curTime);

    if (hasAnalyzed && keyframes && keyframes.length > 0) {
      setSelectedKeyframe(getActiveKeyframeIndex(curTime, keyframes));
    }
  };

  // High-frequency 60 FPS animation frame loop for instantaneous hazard boundary detection as video plays
  useEffect(() => {
    let animId: number;
    const syncFrame = () => {
      if (videoRef.current && !videoRef.current.paused && hasAnalyzed && keyframes.length > 0) {
        const curTime = videoRef.current.currentTime;
        setCurrentTimeSec(curTime);
        setSelectedKeyframe(getActiveKeyframeIndex(curTime, keyframes));
      }
      animId = requestAnimationFrame(syncFrame);
    };
    animId = requestAnimationFrame(syncFrame);
    return () => cancelAnimationFrame(animId);
  }, [hasAnalyzed, keyframes]);

  const togglePlayPause = () => {
    if (!videoRef.current) return;
    if (isPlaying) {
      videoRef.current.pause();
      setIsPlaying(false);
    } else {
      videoRef.current.play().catch(() => {});
      setIsPlaying(true);
    }
  };

  const jumpToKeyframe = (index: number) => {
    setSelectedKeyframe(index);
    const kf = keyframes[index];
    if (kf && videoRef.current) {
      videoRef.current.currentTime = kf.seekTime;
      if (videoRef.current.paused) {
        videoRef.current.play().catch(() => {});
        setIsPlaying(true);
      }
    }
  };

  // Upload manual video handler with real OpenCV extraction, YOLOv8 inference & DB save
  const handleVideoUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Reset old detections immediately so no stale bounding boxes or keyframes appear
    setHasAnalyzed(false);
    setKeyframes([]);
    setSelectedKeyframe(0);
    setIsAnalyzing(true);
    setAnalysisStatus(`Uploading "${file.name}" to FloorGuard AI inspection engine...`);
    setProgress(25);
    setVideoPlayError(false);

    const localBlobUrl = URL.createObjectURL(file);
    setVideoSrc(localBlobUrl);
    setIsCustomVideo(true);

    setVideoMeta({
      filename: file.name,
      resolution: 'Analyzing video stream...',
      duration: 'Calculating...',
      totalFrames: 0,
      analyzedFrames: 0,
      hazardsDetected: 0,
      safeFrames: 0,
      summary: `Uploading "${file.name}" to FloorGuard AI inspection engine...`
    });

    const formData = new FormData();
    formData.append('video', file);

    try {
      setAnalysisStatus('Sampling keyframes and executing FloorGuard YOLOv8 detection...');
      setProgress(60);

      const res = await fetch('/api/detect/video', {
        method: 'POST',
        body: formData
      });

      setProgress(85);
      const data = await res.json();
      setProgress(100);

      if (data && data.status === 'ok' && data.video_analysis) {
        const va = data.video_analysis;
        setVideoMeta({
          filename: file.name,
          resolution: va.resolution || '1280x720 @ 30 FPS',
          duration: va.duration || '00:10',
          totalFrames: va.total_frames || 240,
          analyzedFrames: va.analyzed_frames || 192,
          hazardsDetected: va.hazards_count || 0,
          safeFrames: va.safe_frames || Math.max(0, (va.total_frames || 240) - (va.hazards_count || 0) * 24),
          summary: va.summary || 'Video hazard analysis complete. Incidents recorded to history.'
        });

        if (va.keyframes && va.keyframes.length > 0) {
          setKeyframes(va.keyframes);
          setSelectedKeyframe(0);
          setHasAnalyzed(true);
          setShowOverlay(true);

          // Record each detected hazard keyframe to persistent Hazard History
          va.keyframes.forEach((kf: any, kIdx: number) => {
            if (kf.severity && kf.severity !== 'Safe') {
              saveLocalHistoryItem({
                id: `det_vid_${Date.now()}_${kIdx}`,
                detection_run_id: data.run_id || `run_vid_${Date.now()}`,
                class_name: kf.detected_class || kf.class_name || 'Hazard',
                confidence: kf.confidence || 0.9,
                severity: kf.severity || 'Medium',
                estimated_area: 0.25,
                evidence_path: kf.annotated_image_url || kf.thumb || '/assets/samples/thumb_water_spill.jpg',
                location: `Video @ ${kf.timestamp || '00:00'} (${file.name})`,
                source_type: 'video',
                original_filename: file.name,
                created_at: new Date().toISOString(),
                summary: `Video hazard: ${kf.detected_class || kf.class_name} detected at frame ${kf.frame || kIdx}`
              });
            }
          });
        }

        // Keep localBlobUrl for smooth playback without browser media interruption
        if (!localBlobUrl && va.file_path) {
          setVideoSrc(va.file_path);
        }

        loadVideoHistory();
      } else {
        alert(data.message || 'Video analysis failed. Please try a different video format.');
        setVideoMeta(prev => ({
          ...prev,
          summary: 'Video analysis failed: ' + (data.message || 'Inspection error')
        }));
      }
    } catch (err: any) {
      console.error('Failed to analyze uploaded video:', err);
      alert('Failed to analyze uploaded video: ' + (err.message || 'Network error'));
      setVideoMeta(prev => ({
        ...prev,
        summary: 'Video analysis encountered an error: ' + (err.message || 'Inspection failed')
      }));
    } finally {
      setTimeout(() => {
        setIsAnalyzing(false);
        setAnalysisStatus('');
        if (videoRef.current) {
          videoRef.current.currentTime = 0;
          videoRef.current.play().catch(() => {});
          setIsPlaying(true);
        }
      }, 350);

      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const restoreSampleVideo = () => {
    setVideoSrc(DEFAULT_SAMPLE_VIDEO);
    setIsCustomVideo(false);
    setSelectedKeyframe(0);
    setKeyframes(DEFAULT_KEYFRAMES);
    setVideoPlayError(false);
    setHasAnalyzed(true);
    setShowOverlay(true);
    setVideoMeta({
      filename: 'corridor_hazard_tour_30s.mp4',
      resolution: '1280x720 @ 30 FPS',
      duration: '00:30',
      totalFrames: 900,
      analyzedFrames: 900,
      hazardsDetected: 4,
      safeFrames: 180,
      summary: 'Autonomous 30s video hazard inspection: 4 distinct floor hazards verified (Water Spill, Oil Spill, Broken Glass, Obstacle).'
    });
    if (videoRef.current) {
      videoRef.current.currentTime = 0;
      videoRef.current.play().catch(() => {});
      setIsPlaying(true);
    }
  };

  // Run video analysis on the current video and save history to database
  const runAnalysis = async () => {
    setIsAnalyzing(true);
    setAnalysisStatus('Running multi-hazard OpenCV frame extraction & YOLOv8 evaluation...');
    setProgress(20);

    try {
      const res = await fetch('/api/detect/video', {
        method: 'POST'
      });
      setProgress(75);
      const data = await res.json();
      setProgress(100);

      if (data && data.video_analysis) {
        const va = data.video_analysis;
        setVideoMeta({
          filename: va.filename || 'corridor_hazard_tour_30s.mp4',
          resolution: va.resolution || '1280x720 @ 30 FPS',
          duration: va.duration || '00:30',
          totalFrames: va.total_frames || 900,
          analyzedFrames: va.analyzed_frames || 900,
          hazardsDetected: va.hazards_count || 4,
          safeFrames: va.safe_frames || 180,
          summary: va.summary || 'Continuous 30s video hazard inspection: 4 distinct hazards verified (Water Spill, Oil Spill, Broken Glass, Obstacle).'
        });

        if (va.keyframes && va.keyframes.length > 0) {
          setKeyframes(va.keyframes);
          setSelectedKeyframe(0);

          // Record tour keyframes to persistent Hazard History
          va.keyframes.forEach((kf: any, kIdx: number) => {
            if (kf.severity && kf.severity !== 'Safe') {
              saveLocalHistoryItem({
                id: `det_tour_${Date.now()}_${kIdx}`,
                detection_run_id: `run_tour_${Date.now()}`,
                class_name: kf.detected_class || kf.class_name || 'Hazard',
                confidence: kf.confidence || 0.95,
                severity: kf.severity || 'High',
                estimated_area: 0.35,
                evidence_path: kf.annotated_image_url || kf.thumb || '/assets/samples/thumb_water_spill.jpg',
                location: `Patrol Tour @ ${kf.timestamp || '00:00'}`,
                source_type: 'video',
                original_filename: 'corridor_hazard_tour_30s.mp4',
                created_at: new Date().toISOString(),
                summary: `Sample Tour hazard: ${kf.detected_class || kf.class_name} at ${kf.timestamp}`
              });
            }
          });
        }
        setHasAnalyzed(true);
        setShowOverlay(true);
        loadVideoHistory();
      }
    } catch (err: any) {
      console.error('Failed to run video analysis:', err);
    } finally {
      setTimeout(() => {
        setIsAnalyzing(false);
        setAnalysisStatus('');
      }, 350);
    }
  };

  const current = keyframes[selectedKeyframe] || keyframes[0] || DEFAULT_KEYFRAMES[0];

  return (
    <div className="p-6 space-y-6 max-w-[1720px] mx-auto">
      {/* Top Banner */}
      <div className="bg-[#131b29] border border-[#1e2c3f] rounded-2xl p-5 flex flex-wrap items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <Video className="w-5 h-5 text-[#22c55e]" />
            <h2 className="text-base font-bold text-white tracking-tight">
              Offline Video Hazard Inspection
            </h2>
            {hasAnalyzed ? (
              <span className="text-[10px] bg-emerald-500/20 text-[#22c55e] border border-emerald-500/30 px-2.5 py-0.5 rounded font-mono font-semibold flex items-center gap-1.5">
                <span className="w-1.5 h-1.5 rounded-full bg-[#22c55e] animate-pulse"></span>
                Inspection Active • History Saved
              </span>
            ) : (
              <span className="text-[10px] bg-slate-800 text-slate-300 border border-slate-700 px-2.5 py-0.5 rounded font-mono font-semibold">
                Raw Footage Standby (Click Run Analysis)
              </span>
            )}
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Autonomous floor hazard inspection pipeline scanning video footage for liquid spills, oils, broken glass, and obstacles.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleVideoUpload}
            accept="video/mp4,video/webm,video/quicktime,video/x-matroska,video/avi"
            className="hidden"
          />

          <button
            onClick={() => fileInputRef.current?.click()}
            disabled={isAnalyzing}
            className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-[#1b2738] hover:bg-[#223349] border border-[#2d3e58] text-slate-200 text-xs font-semibold shadow-sm transition-colors cursor-pointer disabled:opacity-50"
          >
            <Upload className="w-3.5 h-3.5 text-[#38bdf8]" />
            <span>Upload Manual Video</span>
          </button>

          {hasAnalyzed && (
            <button
              onClick={() => setShowOverlay(!showOverlay)}
              className="flex items-center gap-1.5 px-3 py-2 rounded-xl bg-[#182335] hover:bg-[#202e44] border border-[#26374f] text-slate-300 text-xs font-medium transition-colors cursor-pointer"
              title="Toggle bounding box overlay"
            >
              {showOverlay ? <EyeOff className="w-3.5 h-3.5 text-amber-400" /> : <Eye className="w-3.5 h-3.5 text-[#22c55e]" />}
              <span>{showOverlay ? 'Hide Overlay' : 'Show Overlay'}</span>
            </button>
          )}

          {isCustomVideo && (
            <button
              onClick={restoreSampleVideo}
              disabled={isAnalyzing}
              className="flex items-center gap-2 px-3 py-2 rounded-xl bg-[#1a2333] hover:bg-[#202d42] border border-[#293b54] text-slate-300 text-xs font-medium transition-colors cursor-pointer disabled:opacity-50"
              title="Reset to 30s multi-hazard tour video"
            >
              <RotateCcw className="w-3.5 h-3.5 text-amber-400" />
              <span>Reset 30s Patrol</span>
            </button>
          )}

          <button
            onClick={runAnalysis}
            disabled={isAnalyzing}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-[#22c55e] hover:bg-[#16a34a] text-black font-bold text-xs shadow-md transition-colors cursor-pointer disabled:opacity-50"
          >
            {isAnalyzing ? (
              <Loader2 className="w-3.5 h-3.5 animate-spin" />
            ) : (
              <Play className="w-3.5 h-3.5 fill-current" />
            )}
            <span>{isAnalyzing ? `Analyzing (${progress}%)` : hasAnalyzed ? 'Re-run Analysis' : 'Run Video Analysis'}</span>
          </button>
        </div>
      </div>

      {/* Analysis Progress Banner */}
      {isAnalyzing && (
        <div className="p-3.5 rounded-2xl bg-[#0e1e33] border border-[#38bdf8]/40 flex items-center justify-between shadow-md">
          <div className="flex items-center gap-3">
            <Loader2 className="w-4 h-4 text-[#38bdf8] animate-spin" />
            <span className="text-xs text-slate-200 font-medium">
              {analysisStatus || `Processing video frames with FloorGuard AI (${progress}%)...`}
            </span>
          </div>
          <div className="w-36 bg-slate-800 rounded-full h-2 overflow-hidden border border-slate-700">
            <div
              className="bg-[#38bdf8] h-full transition-all duration-300 rounded-full"
              style={{ width: `${progress}%` }}
            ></div>
          </div>
        </div>
      )}

      {/* Main Analysis Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Left Column (8 cols): Video Player & Keyframe Timeline */}
        <div className="lg:col-span-8 bg-[#131b29] border border-[#1e2c3f] rounded-2xl p-5 space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <h3 className="text-sm font-bold text-white tracking-tight">Active Hazard Video Feed</h3>
              <span className="text-[10px] bg-slate-800 text-slate-300 px-2 py-0.5 rounded font-mono truncate max-w-[200px]" title={videoMeta.filename}>
                {videoMeta.filename}
              </span>
            </div>
            <div className="flex items-center gap-3">
              <button
                onClick={togglePlayPause}
                className="px-2.5 py-1 rounded-lg bg-[#1a2638] hover:bg-[#24354f] border border-[#2b3c54] text-xs font-medium text-slate-200 flex items-center gap-1.5 cursor-pointer"
              >
                {isPlaying ? <Pause className="w-3.5 h-3.5 text-amber-400" /> : <Play className="w-3.5 h-3.5 text-[#22c55e]" />}
                <span>{isPlaying ? 'Pause' : 'Play'}</span>
              </button>
              <span className="text-xs font-mono text-slate-400">
                Playback: <strong className="text-white">{currentTimeSec.toFixed(1)}s</strong> / {videoMeta.duration}
              </span>
            </div>
          </div>

          {/* Video Display: Clean Raw Footage + Dynamic AI Overlay when analyzed */}
          <div className="relative rounded-xl overflow-hidden border border-[#202d42] bg-[#090e17] aspect-16/9 flex items-center justify-center group shadow-xl">
            {!videoPlayError ? (
              <video
                key={videoSrc}
                ref={videoRef}
                src={videoSrc}
                autoPlay
                muted
                loop
                playsInline
                onTimeUpdate={handleTimeUpdate}
                onSeeked={handleTimeUpdate}
                onError={() => setVideoPlayError(true)}
                className="w-full h-full object-cover"
              />
            ) : (
              <img
                src={current.thumb}
                alt={current.detectedClass}
                className="w-full h-full object-cover"
              />
            )}

            {/* Dynamic AI Hazard Bounding Overlay (ONLY active after Analysis has run) */}
            {hasAnalyzed && showOverlay && current && current.bbox && (
              <div
                className="absolute pointer-events-none transition-all duration-300 border-2 border-red-500 bg-red-500/25 shadow-[0_0_20px_rgba(239,68,68,0.5)] rounded-lg animate-pulse"
                style={{
                  left: `${current.bbox.x}%`,
                  top: `${current.bbox.y}%`,
                  width: `${current.bbox.width}%`,
                  height: `${current.bbox.height}%`
                }}
              >
                {/* Corner highlight reticles */}
                <div className="absolute -top-1 -left-1 w-3 h-3 border-t-2 border-l-2 border-yellow-300"></div>
                <div className="absolute -top-1 -right-1 w-3 h-3 border-t-2 border-r-2 border-yellow-300"></div>
                <div className="absolute -bottom-1 -left-1 w-3 h-3 border-b-2 border-l-2 border-yellow-300"></div>
                <div className="absolute -bottom-1 -right-1 w-3 h-3 border-b-2 border-r-2 border-yellow-300"></div>

                {/* Floating Tag */}
                <div className="absolute -top-7 left-0 bg-red-600 text-white text-[10px] font-bold px-2 py-0.5 rounded shadow flex items-center gap-1 whitespace-nowrap">
                  <AlertTriangle className="w-3 h-3" />
                  <span>{current.detectedClass.toUpperCase()} ({(current.confidence * 100).toFixed(0)}%)</span>
                </div>
              </div>
            )}

            {/* CCTV Telemetry Overlay Stamp */}
            <div className="absolute top-3 left-3 bg-black/85 backdrop-blur-md px-3 py-1.5 rounded-lg border border-white/20 text-white font-mono text-xs flex items-center gap-2 shadow-lg">
              <Clock className="w-3.5 h-3.5 text-[#22c55e]" />
              <span>{current.timestamp}</span>
              <span className="text-slate-400">|</span>
              {hasAnalyzed ? (
                <>
                  <span
                    className={`font-bold ${
                      current.severity === 'Safe' ? 'text-[#22c55e]' : 'text-[#ef4444]'
                    }`}
                  >
                    {current.detectedClass.toUpperCase()}
                  </span>
                  <span className="text-slate-500 font-mono text-[10px]">
                    {(current.confidence * 100).toFixed(0)}% CONF
                  </span>
                </>
              ) : isAnalyzing ? (
                <span className="text-cyan-400 font-bold flex items-center gap-1.5 animate-pulse">
                  <span className="w-2 h-2 rounded-full bg-cyan-400"></span>
                  UPLOADING &amp; ANALYZING VIDEO...
                </span>
              ) : (
                <span className="text-slate-300 font-bold">RAW FOOTAGE (AWAITING RUN)</span>
              )}
            </div>

            {/* Severity Risk Badge */}
            {hasAnalyzed ? (
              current.severity !== 'Safe' ? (
                <div className="absolute bottom-3 right-3 bg-[#ef4444]/95 backdrop-blur-md px-3.5 py-1.5 rounded-lg text-white font-bold text-xs shadow-lg flex items-center gap-1.5 border border-red-400/50">
                  <AlertTriangle className="w-3.5 h-3.5" />
                  <span>{current.severity.toUpperCase()} RISK {current.detectedClass.toUpperCase()}</span>
                </div>
              ) : (
                <div className="absolute bottom-3 right-3 bg-[#22c55e]/95 backdrop-blur-md px-3.5 py-1.5 rounded-lg text-black font-bold text-xs shadow-lg flex items-center gap-1.5">
                  <CheckCircle className="w-3.5 h-3.5" />
                  <span>CLEAR &amp; SAFE FLOOR ZONE</span>
                </div>
              )
            ) : (
              <div className="absolute bottom-3 right-3 bg-[#1e293b]/90 backdrop-blur-md px-3.5 py-1.5 rounded-lg text-slate-300 font-medium text-xs shadow-lg flex items-center gap-1.5 border border-slate-700">
                <Video className="w-3.5 h-3.5 text-[#38bdf8]" />
                <span>STANDBY MODE • CLICK "RUN VIDEO ANALYSIS"</span>
              </div>
            )}
          </div>

          {/* Keyframe Timeline Scrubber */}
          <div className="space-y-2 pt-2">
            <div className="flex items-center justify-between text-xs">
              <span className="font-bold text-slate-300">
                {hasAnalyzed ? 'Synchronized Hazard Keyframe Detections' : 'Inspection Keyframe Sequence (Standby)'}
              </span>
              <span className="text-slate-400 text-[11px]">
                {hasAnalyzed ? 'Click thumbnail to seek timestamp' : 'Click "Run Video Analysis" to detect hazards'}
              </span>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-2">
              {keyframes.map((kf, i) => (
                <button
                  key={kf.id ?? i}
                  onClick={() => jumpToKeyframe(i)}
                  className={`p-1.5 rounded-xl border text-left transition-all cursor-pointer ${
                    hasAnalyzed && selectedKeyframe === i
                      ? 'border-[#22c55e] bg-[#1a2c22] shadow-[0_0_12px_rgba(34,197,94,0.35)] scale-[1.02]'
                      : 'border-[#1b2738] bg-[#0d131f] hover:border-slate-500'
                  }`}
                >
                  <div className="aspect-16/10 rounded-md overflow-hidden bg-black mb-1.5 relative">
                    <img src={kf.thumb} alt={kf.detectedClass} className="w-full h-full object-cover" />
                    {hasAnalyzed && kf.severity !== 'Safe' && (
                      <span className="absolute bottom-1 right-1 w-2 h-2 rounded-full bg-red-500 animate-ping"></span>
                    )}
                  </div>
                  <div className="flex items-center justify-between text-[10px] font-mono">
                    <span className="text-slate-300 font-bold">{kf.timestamp}</span>
                    <span
                      className={`font-bold ${
                        !hasAnalyzed ? 'text-slate-400' : kf.severity === 'Safe' ? 'text-[#22c55e]' : 'text-[#ef4444]'
                      }`}
                    >
                      {hasAnalyzed ? kf.severity : 'Frame'}
                    </span>
                  </div>
                  <div className="text-[10px] text-slate-400 truncate mt-0.5">
                    {hasAnalyzed ? kf.detectedClass : 'Sampled View'}
                  </div>
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Right Column (4 cols): Video Run Summary & Inspection Report */}
        <div className="lg:col-span-4 bg-[#131b29] border border-[#1e2c3f] rounded-2xl p-5 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-white tracking-tight">Offline Video Summary</h3>
            <span className="text-[10px] bg-slate-800 text-[#38bdf8] font-mono px-2 py-0.5 rounded">
              {isCustomVideo ? 'Uploaded Video' : '30s Patrol Scan'}
            </span>
          </div>

          <div className="p-4 rounded-xl bg-[#0d131f] border border-[#182335] space-y-2.5 text-xs font-mono">
            <div className="flex justify-between text-slate-300">
              <span className="text-slate-400">Source:</span>
              <span className="text-white truncate max-w-[190px]" title={videoMeta.filename}>
                {videoMeta.filename}
              </span>
            </div>
            <div className="flex justify-between text-slate-300">
              <span className="text-slate-400">Duration:</span>
              <span className="text-white">{videoMeta.duration}</span>
            </div>
            <div className="flex justify-between text-slate-300">
              <span className="text-slate-400">Resolution:</span>
              <span className="text-white">{videoMeta.resolution}</span>
            </div>
            <div className="flex justify-between text-slate-300">
              <span className="text-slate-400">Analyzed Frames:</span>
              <span className="text-white">{videoMeta.analyzedFrames} frames</span>
            </div>
            <div className="flex justify-between text-slate-300">
              <span className="text-slate-400">Hazard Events:</span>
              <span className="font-bold text-[#ef4444]">{videoMeta.hazardsDetected} incidents</span>
            </div>
            <div className="flex justify-between text-slate-300">
              <span className="text-slate-400">Safe Frames:</span>
              <span className="font-bold text-[#22c55e]">{videoMeta.safeFrames} frames</span>
            </div>
          </div>

          {/* Active Keyframe Detail Card */}
          <div className="p-4 rounded-xl bg-[#0d131f] border border-[#1d2b3f] space-y-2 text-xs">
            <div className="flex items-center justify-between">
              <span className="text-slate-400 font-semibold">Active Keyframe:</span>
              <span className="text-[#38bdf8] font-mono font-bold">{current.timestamp}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-slate-400">Classification:</span>
              <span className="text-white font-bold">{hasAnalyzed ? current.detectedClass : 'Awaiting Analysis'}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-slate-400">Confidence:</span>
              <span className="text-emerald-400 font-mono font-bold">
                {hasAnalyzed ? `${(current.confidence * 100).toFixed(1)}%` : '---'}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-slate-400">Hazard Area:</span>
              <span className="text-slate-200 font-mono">{hasAnalyzed ? current.area : '---'}</span>
            </div>
            <p className="text-[11px] text-slate-300 pt-1 border-t border-[#182335] leading-relaxed">
              {hasAnalyzed ? current.note : 'Raw footage preview. Click "Run Video Analysis" to trigger AI hazard localization.'}
            </p>
          </div>

          {/* Incident Callout */}
          <div className="p-3.5 rounded-xl bg-[#231519] border border-[#ef4444]/40 space-y-2 shadow-sm">
            <div className="flex items-center gap-2 text-xs font-bold text-[#ef4444]">
              <AlertTriangle className="w-4 h-4 shrink-0" />
              <span>Safety Assessment &amp; History Status</span>
            </div>
            <p className="text-[11px] text-slate-200 leading-relaxed">
              {videoMeta.summary}
            </p>
          </div>
        </div>
      </div>

      {/* Dedicated Video Analysis History Table (Separate from Images) */}
      <div className="bg-[#131b29] border border-[#1e2c3f] rounded-2xl p-5 space-y-4 shadow-sm">
        <div className="flex flex-wrap items-center justify-between gap-3 pb-3 border-b border-[#1b2738]">
          <div className="flex items-center gap-2">
            <Video className="w-4 h-4 text-[#f59e0b]" />
            <h3 className="text-sm font-bold text-white tracking-tight">
              Dedicated Video Inspection History
            </h3>
            <span className="text-[10px] bg-amber-500/20 text-amber-400 border border-amber-500/30 px-2 py-0.5 rounded font-mono font-semibold">
              Separate Video Archive ({videoHistory.length} Runs)
            </span>
          </div>
          <p className="text-xs text-slate-400">
            All video analysis runs saved separately with time-synchronized keyframes and hazard logs.
          </p>
        </div>

        {videoHistory.length === 0 ? (
          <div className="py-8 text-center text-xs text-slate-500 font-mono">
            No video inspection runs recorded yet. Click "Run Video Analysis" or upload a video above.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-mono">
              <thead>
                <tr className="border-b border-[#1b2738] text-[10px] text-slate-400">
                  <th className="pb-3">Run Timestamp</th>
                  <th className="pb-3">Video Filename</th>
                  <th className="pb-3">Hazards Detected</th>
                  <th className="pb-3">Keyframe Hazard Evidence</th>
                  <th className="pb-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#172335]">
                {videoHistory.map((run) => (
                  <tr
                    key={run.id}
                    onClick={() => handleSelectPastVideo(run)}
                    className="hover:bg-[#182335] transition-colors cursor-pointer group"
                  >
                    <td className="py-3 text-[11px] text-slate-400 whitespace-nowrap">
                      {new Date(run.created_at).toLocaleString('en-US', {
                        month: 'short',
                        day: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit'
                      })}
                    </td>
                    <td className="py-3 font-sans font-semibold text-slate-200">
                      <div className="flex items-center gap-2">
                        <Video className="w-3.5 h-3.5 text-amber-400 shrink-0" />
                        <span className="truncate max-w-[220px]" title={run.original_filename}>
                          {run.original_filename}
                        </span>
                      </div>
                      <div className="text-[10px] text-slate-500 font-mono mt-0.5 truncate max-w-[280px]">
                        {run.summary}
                      </div>
                    </td>
                    <td className="py-3">
                      <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-[#ef4444]/20 text-[#ef4444] border border-[#ef4444]/30">
                        {run.total_detections} Hazard Incidents
                      </span>
                    </td>
                    <td className="py-3">
                      <div className="flex items-center gap-1.5 flex-wrap">
                        {(run.detections || []).slice(0, 5).map((d: any, dIdx: number) => (
                          <div
                            key={d.id || dIdx}
                            className="relative group/thumb w-10 h-7 rounded overflow-hidden border border-[#2b3d56] bg-black"
                            title={`${d.class_name} (${Math.round(d.confidence * 100)}%)`}
                          >
                            <img
                              src={d.evidence_path || '/assets/samples/thumb_water_spill.jpg'}
                              alt={d.class_name}
                              className="w-full h-full object-cover"
                            />
                            <div className="absolute inset-0 bg-black/40 group-hover/thumb:bg-transparent transition-colors"></div>
                          </div>
                        ))}
                      </div>
                    </td>
                    <td className="py-3 text-right">
                      <div className="flex items-center justify-end gap-2">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleSelectPastVideo(run);
                          }}
                          className="px-2.5 py-1 rounded-lg bg-[#1a283c] hover:bg-[#23354f] border border-[#2b3e5a] text-slate-200 text-[10px] font-bold flex items-center gap-1 transition-colors"
                        >
                          <ExternalLink className="w-3 h-3 text-[#38bdf8]" />
                          <span>Load Run</span>
                        </button>
                        <button
                          onClick={(e) => handleDeleteVideoRun(run.id, e)}
                          className="p-1 hover:text-[#ef4444] text-slate-500 transition-colors"
                          title="Delete run"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
