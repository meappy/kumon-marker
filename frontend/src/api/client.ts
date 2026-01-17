/**
 * API client for the Kumon Marker backend.
 */

const API_BASE = '/api';

export interface User {
  id: string;
  email: string;
  name: string | null;
  picture: string | null;
}

export interface AuthStatus {
  authenticated: boolean;
  user: User | null;
  google_drive_connected: boolean;
}

export interface WorksheetSummary {
  id: string;
  pdf_name: string;
  timestamp: string;
  pages: number;
  total_questions: number;
  total_errors: number;
  score_percentage: number;
  grade: string;
  has_marked_pdf: boolean;
  has_report: boolean;
  student_name: string | null;
  sheet_id: string | null;
}

export interface GDriveFile {
  id: string;
  name: string;
  created_time: string;
  size: number | null;
  is_kumon: boolean | null;  // null = not checked, true = Kumon worksheet, false = not Kumon
  sheet_id: string | null;   // e.g. "C26a", "D116"
  student_name: string | null;
}

export interface GDriveFilesResponse {
  scanned_at: string;
  files: GDriveFile[];
}

export interface UploadResponse {
  message: string;
  filename: string;
  id: string;
}

export interface ProcessResponse {
  message: string;
  id: string;
  job_id?: string;
  queued: boolean;
}

export interface Job {
  id: string;
  worksheet_id: string;
  user_id: string;
  status: 'queued' | 'processing' | 'completed' | 'failed' | 'cancelled';
  progress: number;
  error: string | null;
  created_at: string | null;
  started_at: string | null;
  completed_at: string | null;
}

export interface JobsResponse {
  jobs: Job[];
  queue_enabled: boolean;
}

export interface QueueStatusResponse {
  enabled: boolean;
  active_count: number;
  jobs: Job[];
}

export interface SettingValue {
  value: string;
  source: 'default' | 'env' | 'user';
  editable: boolean;
}

export interface VersionInfo {
  app_version: string;
  image_tag: string;
}

export interface AppSettings {
  anthropic_api_key: SettingValue;
  anthropic_model: SettingValue;
  gdrive_folder: SettingValue;
  timezone: SettingValue;
  google_configured: boolean;
  version: VersionInfo;
}

export interface GoogleAuthStatus {
  connected: boolean;
  email: string | null;
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }
  return response.json();
}

export const api = {
  // Auth
  async getAuthStatus(): Promise<AuthStatus> {
    const response = await fetch(`${API_BASE}/auth/status`);
    return handleResponse(response);
  },

  async getLoginUrl(): Promise<{ url: string }> {
    const response = await fetch(`${API_BASE}/auth/login`);
    return handleResponse(response);
  },

  async logout(): Promise<void> {
    const response = await fetch(`${API_BASE}/auth/logout`, {
      method: 'POST',
    });
    return handleResponse(response);
  },

  // Worksheets
  async listWorksheets(): Promise<WorksheetSummary[]> {
    const response = await fetch(`${API_BASE}/worksheets`);
    return handleResponse(response);
  },

  async getWorksheet(id: string): Promise<unknown> {
    const response = await fetch(`${API_BASE}/worksheets/${id}`);
    return handleResponse(response);
  },

  async uploadWorksheet(file: File): Promise<UploadResponse> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_BASE}/upload`, {
      method: 'POST',
      body: formData,
    });
    return handleResponse(response);
  },

  async processWorksheet(id: string, studentName?: string | null): Promise<ProcessResponse> {
    const params = studentName ? `?student_name=${encodeURIComponent(studentName)}` : '';
    const response = await fetch(`${API_BASE}/worksheets/${id}/process${params}`, {
      method: 'POST',
    });
    return handleResponse(response);
  },

  // Jobs API
  async getQueueStatus(): Promise<QueueStatusResponse> {
    const response = await fetch(`${API_BASE}/jobs/status`);
    return handleResponse(response);
  },

  async listJobs(activeOnly: boolean = false): Promise<JobsResponse> {
    const url = activeOnly ? `${API_BASE}/jobs?active_only=true` : `${API_BASE}/jobs`;
    const response = await fetch(url);
    return handleResponse(response);
  },

  async getJob(jobId: string): Promise<Job> {
    const response = await fetch(`${API_BASE}/jobs/${jobId}`);
    return handleResponse(response);
  },

  async cancelJob(jobId: string): Promise<Job> {
    const response = await fetch(`${API_BASE}/jobs/${jobId}`, {
      method: 'DELETE',
    });
    return handleResponse(response);
  },

  async listGDriveFiles(refresh: boolean = false): Promise<GDriveFilesResponse> {
    const url = refresh ? `${API_BASE}/gdrive/files?refresh=true` : `${API_BASE}/gdrive/files`;
    const response = await fetch(url);
    return handleResponse(response);
  },

  async syncFromGDrive(fileId: string, filename: string): Promise<UploadResponse> {
    const response = await fetch(`${API_BASE}/gdrive/sync/${fileId}?filename=${encodeURIComponent(filename)}`, {
      method: 'POST',
    });
    return handleResponse(response);
  },

  async regenerateReport(id: string): Promise<{ message: string; id: string }> {
    const response = await fetch(`${API_BASE}/worksheets/${id}/regenerate-report`, {
      method: 'POST',
    });
    return handleResponse(response);
  },

  getMarkedPdfUrl(id: string, download: boolean = false): string {
    return `${API_BASE}/worksheets/${id}/marked${download ? '?download=true' : ''}`;
  },

  getReportPdfUrl(id: string, download: boolean = false): string {
    return `${API_BASE}/worksheets/${id}/report${download ? '?download=true' : ''}`;
  },

  // Settings API
  async getSettings(): Promise<AppSettings> {
    const response = await fetch(`${API_BASE}/settings`);
    return handleResponse(response);
  },

  async updateSettings(settings: {
    anthropic_api_key?: string;
    anthropic_model?: string;
    gdrive_folder?: string;
    timezone?: string;
  }): Promise<AppSettings> {
    const response = await fetch(`${API_BASE}/settings`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(settings),
    });
    return handleResponse(response);
  },

  async resetSetting(key: string): Promise<void> {
    const response = await fetch(`${API_BASE}/settings/${key}`, {
      method: 'DELETE',
    });
    return handleResponse(response);
  },

  // Google Auth API
  async getGoogleAuthStatus(): Promise<GoogleAuthStatus> {
    const response = await fetch(`${API_BASE}/auth/google/status`);
    return handleResponse(response);
  },

  async getGoogleAuthUrl(): Promise<{ url: string }> {
    const response = await fetch(`${API_BASE}/auth/google/url`);
    return handleResponse(response);
  },

  async disconnectGoogle(): Promise<void> {
    const response = await fetch(`${API_BASE}/auth/google/disconnect`, {
      method: 'DELETE',
    });
    return handleResponse(response);
  },

  // Worksheet deletion
  async deleteWorksheet(id: string): Promise<{ message: string; id: string; files_deleted: number }> {
    const response = await fetch(`${API_BASE}/worksheets/${id}`, {
      method: 'DELETE',
    });
    return handleResponse(response);
  },

  async deleteAllWorksheets(): Promise<{ message: string; files_deleted: number }> {
    const response = await fetch(`${API_BASE}/worksheets`, {
      method: 'DELETE',
    });
    return handleResponse(response);
  },
};
