import { useEffect, useState, useRef, useCallback } from 'react';
import { api } from '../api/client';
import type { GDriveFile, WorksheetSummary, Job } from '../api/client';
import { formatSheetName } from '../utils/kumon';

interface QueueItem {
  fileId: string;
  filename: string;
  sheetId: string | null;
  studentName: string | null;
}

interface GDriveModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSync: (fileId: string, filename: string, studentName: string | null) => Promise<void>;
  worksheets: WorksheetSummary[];
  timezone?: string;
  activeJobs?: Job[];
  queueEnabled?: boolean;
}

function getTimezoneAbbr(date: Date, timezone?: string): string {
  if (!timezone) return '';
  // Get timezone abbreviation (e.g., ACDT, AEST) by formatting with only timeZoneName
  const formatted = date.toLocaleString('en-AU', {
    timeZone: timezone,
    timeZoneName: 'short',
  });
  // Extract just the timezone part (last word)
  const match = formatted.match(/[A-Z]{3,5}$/);
  return match ? match[0] : '';
}

function formatDateTime(isoString: string, timezone?: string): string {
  const date = new Date(isoString);
  const options: Intl.DateTimeFormatOptions = {
    weekday: 'short',
    day: 'numeric',
    month: 'short',
    year: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
    hour12: true,
    timeZone: timezone || undefined,
  };
  const formatted = date.toLocaleString('en-AU', options);
  const tzAbbr = getTimezoneAbbr(date, timezone);
  return tzAbbr ? `${formatted} ${tzAbbr}` : formatted;
}

function formatScanTime(isoString: string, timezone?: string): string {
  const date = new Date(isoString);
  const formatted = date.toLocaleString('en-AU', {
    day: 'numeric',
    month: 'short',
    hour: 'numeric',
    minute: '2-digit',
    hour12: true,
    timeZone: timezone || undefined,
  });
  const tzAbbr = getTimezoneAbbr(date, timezone);
  return tzAbbr ? `${formatted} ${tzAbbr}` : formatted;
}

function formatMarkedTime(isoString: string, timezone?: string): string {
  const date = new Date(isoString);
  const formatted = date.toLocaleString('en-AU', {
    day: 'numeric',
    month: 'short',
    hour: 'numeric',
    minute: '2-digit',
    hour12: true,
    timeZone: timezone || undefined,
  });
  return formatted;
}

export function GDriveModal({ isOpen, onClose, onSync, worksheets, timezone, activeJobs = [], queueEnabled = false }: GDriveModalProps) {
  const [files, setFiles] = useState<GDriveFile[]>([]);
  const [scannedAt, setScannedAt] = useState<string | null>(null);

  // Check if a Drive file has already been marked
  // Note: GDrive sheet_id is single (e.g., "C26a"), worksheet sheet_id is a range (e.g., "C26a-C28b")
  const isAlreadyMarked = useCallback((file: GDriveFile): WorksheetSummary | undefined => {
    if (!file.sheet_id) return undefined;
    return worksheets.find(
      (ws) =>
        ws.sheet_id?.startsWith(file.sheet_id!) &&
        ((!ws.student_name && !file.student_name) ||
          ws.student_name?.toLowerCase() === file.student_name?.toLowerCase())
    );
  }, [worksheets]);

  // Find active job for a file (by matching filename to worksheet_id)
  const getJobForFile = useCallback((file: GDriveFile): Job | undefined => {
    const worksheetId = file.name.replace(/\.pdf$/i, '');
    return activeJobs.find((job) => job.worksheet_id === worksheetId);
  }, [activeJobs]);

  // Cancel a job
  const handleCancelJob = useCallback(async (jobId: string) => {
    try {
      await api.cancelJob(jobId);
    } catch (error) {
      console.error('Failed to cancel job:', error);
    }
  }, []);
  const [loading, setLoading] = useState(false);
  const [scanning, setScanning] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Queue management
  const [queue, setQueue] = useState<QueueItem[]>([]);
  const [processing, setProcessing] = useState<string | null>(null);
  const [completed, setCompleted] = useState<Set<string>>(new Set());
  const processingRef = useRef(false);

  const fetchFiles = async (refresh: boolean = false) => {
    if (refresh) {
      setScanning(true);
    } else {
      setLoading(true);
    }
    setError(null);
    try {
      const response = await api.listGDriveFiles(refresh);
      setFiles(response.files);
      setScannedAt(response.scanned_at);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch files');
    } finally {
      setLoading(false);
      setScanning(false);
    }
  };

  // Process queue one at a time
  const processQueue = useCallback(async () => {
    if (processingRef.current) return;

    setQueue((currentQueue) => {
      if (currentQueue.length === 0) return currentQueue;

      const [next, ...rest] = currentQueue;
      processingRef.current = true;
      setProcessing(next.fileId);

      // Process async
      (async () => {
        try {
          await onSync(next.fileId, next.filename, next.studentName);
          setCompleted((prev) => new Set([...prev, next.fileId]));
        } catch (err) {
          setError(err instanceof Error ? err.message : 'Marking failed');
        } finally {
          processingRef.current = false;
          setProcessing(null);
          // Process next item
          setTimeout(() => processQueue(), 100);
        }
      })();

      return rest;
    });
  }, [onSync]);

  // Start processing when queue changes
  useEffect(() => {
    if (queue.length > 0 && !processingRef.current) {
      processQueue();
    }
  }, [queue, processQueue]);

  useEffect(() => {
    if (isOpen) {
      fetchFiles(false);
      // Reset state when opening
      setCompleted(new Set());
      setQueue([]);
      setProcessing(null);
      processingRef.current = false;
    }
  }, [isOpen]);

  // Handle ESC key to close modal
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };
    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  const handleAddToQueue = (file: GDriveFile) => {
    // Don't add if already in queue, processing, or completed
    if (
      queue.some((q) => q.fileId === file.id) ||
      processing === file.id ||
      completed.has(file.id)
    ) {
      return;
    }

    setQueue((prev) => [
      ...prev,
      {
        fileId: file.id,
        filename: file.name,
        sheetId: file.sheet_id,
        studentName: file.student_name,
      },
    ]);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white rounded-xl shadow-xl w-full max-w-lg mx-4 max-h-[80vh] flex flex-col">
        <div className="flex items-center justify-between p-4 border-b">
          <div>
            <h2 className="text-lg font-semibold">Google Drive Files</h2>
            {scannedAt && (
              <p className="text-xs text-gray-500">
                Last scan: {formatScanTime(scannedAt, timezone)}
              </p>
            )}
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => fetchFiles(true)}
              disabled={scanning || loading || activeJobs.length > 0 || processing !== null}
              className="px-3 py-1 text-sm bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              title={activeJobs.length > 0 || processing !== null ? 'Cannot refresh while marking is in progress' : undefined}
            >
              {scanning ? 'Scanning...' : 'Refresh'}
            </button>
            <button onClick={onClose} className="text-gray-500 hover:text-gray-700 text-xl">
              ×
            </button>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto p-4">
          {loading && <p className="text-center text-gray-500">Loading...</p>}
          {scanning && <p className="text-center text-gray-500">Scanning Drive files...</p>}
          {error && <p className="text-center text-red-600">{error}</p>}
          {!loading && !scanning && !error && files.length === 0 && (
            <p className="text-center text-gray-500">No PDF files found</p>
          )}
          {!loading && !scanning && !error && files.length > 0 && files.filter(f => f.is_kumon).length === 0 && (
            <p className="text-center text-gray-500">No Kumon worksheets found</p>
          )}
          {files.filter(f => f.is_kumon === true).map((file) => {
            const isInQueue = queue.some((q) => q.fileId === file.id);
            const isProcessing = processing === file.id;
            const isCompleted = completed.has(file.id);
            const queuePosition = queue.findIndex((q) => q.fileId === file.id) + 1;
            const existingWorksheet = isAlreadyMarked(file);
            const activeJob = getJobForFile(file);

            // Determine status based on queue mode
            const jobQueued = activeJob?.status === 'queued';
            const jobProcessing = activeJob?.status === 'processing';
            const jobCompleted = activeJob?.status === 'completed';
            const jobFailed = activeJob?.status === 'failed';

            return (
              <div
                key={file.id}
                className="flex items-center justify-between py-3 border-b last:border-b-0"
              >
                <div>
                  <p className="font-medium text-gray-900">
                    {formatSheetName(file.sheet_id)}
                    {file.student_name && (
                      <span className="ml-2 text-gray-500 font-normal">({file.student_name})</span>
                    )}
                    {existingWorksheet && !activeJob && (
                      <span className="ml-2 px-2 py-0.5 bg-green-100 text-green-700 text-xs rounded">
                        Grade {existingWorksheet.grade} ({existingWorksheet.score_percentage.toFixed(0)}%)
                      </span>
                    )}
                  </p>
                  <p className="text-sm text-gray-500">
                    Scanned: {formatDateTime(file.created_time, timezone)}
                  </p>
                  {existingWorksheet && !activeJob && (
                    <p className="text-sm text-gray-500">
                      Marked: {formatMarkedTime(existingWorksheet.timestamp, timezone)}
                    </p>
                  )}
                  {jobFailed && activeJob?.error && (
                    <p className="text-sm text-red-600 mt-1">{activeJob.error}</p>
                  )}
                </div>
                {/* Download original (only if synced/marked) */}
                {existingWorksheet && (
                  <a
                    href={`/api/uploads/${file.name.replace(/\.pdf$/i, '')}?download=true`}
                    className="p-1.5 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded transition-colors"
                    title="Download original"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                    </svg>
                  </a>
                )}

                {/* Queue-based status (when RabbitMQ is enabled) */}
                {queueEnabled && activeJob ? (
                  jobCompleted ? (
                    <span className="px-4 py-2 bg-green-100 text-green-700 rounded-lg flex items-center gap-2">
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                      Done
                    </span>
                  ) : jobFailed ? (
                    <button
                      onClick={() => handleAddToQueue(file)}
                      className="px-4 py-2 bg-red-100 text-red-700 rounded-lg hover:bg-red-200 transition-colors"
                    >
                      Retry
                    </button>
                  ) : jobProcessing ? (
                    <div className="flex items-center gap-2 px-4 py-2 bg-orange-100 text-orange-700 rounded-lg">
                      <div className="w-16 h-2 bg-orange-200 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-orange-500 transition-all duration-300"
                          style={{ width: `${activeJob.progress}%` }}
                        />
                      </div>
                      <span className="text-sm">{activeJob.progress}%</span>
                      <button
                        onClick={() => handleCancelJob(activeJob.id)}
                        className="ml-1 text-orange-600 hover:text-orange-800"
                        title="Cancel"
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                      </button>
                    </div>
                  ) : jobQueued ? (
                    <div className="flex items-center gap-2 px-4 py-2 bg-gray-100 text-gray-600 rounded-lg">
                      <span className="animate-pulse">Queued</span>
                      <button
                        onClick={() => handleCancelJob(activeJob.id)}
                        className="text-gray-500 hover:text-gray-700"
                        title="Cancel"
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                      </button>
                    </div>
                  ) : null
                ) : (
                  /* Local queue fallback (no RabbitMQ) */
                  isCompleted ? (
                    <span className="px-4 py-2 bg-green-100 text-green-700 rounded-lg">
                      Done
                    </span>
                  ) : isProcessing ? (
                    <span className="px-4 py-2 bg-yellow-100 text-yellow-700 rounded-lg animate-pulse">
                      Marking...
                    </span>
                  ) : isInQueue ? (
                    <span className="px-4 py-2 bg-gray-100 text-gray-600 rounded-lg">
                      Queued #{queuePosition}
                    </span>
                  ) : existingWorksheet ? (
                    <button
                      onClick={() => handleAddToQueue(file)}
                      className="px-4 py-2 bg-gray-100 text-gray-600 rounded-lg hover:bg-gray-200 transition-colors"
                    >
                      Re-mark
                    </button>
                  ) : (
                    <button
                      onClick={() => handleAddToQueue(file)}
                      className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                    >
                      Mark
                    </button>
                  )
                )}
              </div>
            );
          })}
        </div>

        <div className="p-4 border-t">
          <button
            onClick={onClose}
            className="w-full py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
