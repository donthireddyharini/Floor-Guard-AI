/**
 * Persistent Hazard Detection History Store
 * Provides persistent storage and synchronization for both image detections and video analyses.
 */

export interface HistoryRecord {
  id: string;
  detection_run_id: string;
  class_name: string;
  confidence: number;
  severity: string;
  estimated_area?: number;
  evidence_path: string;
  location: string;
  source_type: 'image' | 'video';
  original_filename: string;
  created_at: string;
  bounding_box_json?: string;
  summary?: string;
}

const STORAGE_KEY = 'floorguard_hazard_history_v2';

export function getLocalHistory(): HistoryRecord[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed : [];
  } catch (e) {
    console.warn('Failed to parse local history:', e);
    return [];
  }
}

export function saveLocalHistoryItem(item: HistoryRecord): void {
  try {
    const existing = getLocalHistory();
    // Deduplicate by ID or (detection_run_id + class_name)
    const filtered = existing.filter(
      (x) => x.id !== item.id && !(x.detection_run_id === item.detection_run_id && x.class_name === item.class_name)
    );
    const updated = [item, ...filtered].slice(0, 150);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
    window.dispatchEvent(new CustomEvent('floorguard:history_updated', { detail: item }));
  } catch (err) {
    console.error('Failed to save to local history:', err);
  }
}

export function removeLocalHistoryItem(id: string): void {
  try {
    const existing = getLocalHistory();
    const updated = existing.filter((x) => x.id !== id);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
    window.dispatchEvent(new CustomEvent('floorguard:history_updated'));
  } catch (err) {
    console.error('Failed to remove from local history:', err);
  }
}

export function clearAllLocalHistory(): void {
  try {
    localStorage.removeItem(STORAGE_KEY);
    window.dispatchEvent(new CustomEvent('floorguard:history_updated'));
  } catch (err) {
    console.error('Failed to clear local history:', err);
  }
}
