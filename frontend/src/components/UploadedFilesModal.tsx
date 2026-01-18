import { useEffect, useState, useCallback } from 'react';
import { api } from '../api/client';
import type { UploadedFile, WorksheetSummary, Job } from '../api/client';
import { formatSheetName } from '../utils/kumon';

interface UploadedFilesModalProps {
  isOpen: boolean;
  onClose: () => void;
  onMark: (fileId: string, studentName: string | null) => Promise<void>;
  onRefreshWorksheets: () => void;
  worksheets: WorksheetSummary[];
  timezone?: string;
  activeJobs?: Job[];
  queueEnabled?: boolean;
}

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function formatDateTime(isoString: string, timezone?: string): string {
  const date = new Date(isoString);
  const options: Intl.DateTimeFormatOptions = {
    weekday: 'short',
    day: 'numeric',
    month: 'short',
    hour: 'numeric',
    minute: '2-digit',
    hour12: true,
    timeZone: timezone || undefined,
  };
  return date.toLocaleString('en-AU', options);
}

export function UploadedFilesModal({
  isOpen,
  onClose,
  onMark,
  onRefreshWorksheets,
  worksheets,
  timezone,
  activeJobs = [],
  queueEnabled = false,
}: UploadedFilesModalProps) {
  const [files, setFiles] = useState<UploadedFile[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [deleting, setDeleting] = useState<string | null>(null);

  const fetchFiles = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await api.listUploadedFiles();
      setFiles(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch files');
    } finally {
      setLoading(false);
    }
  };

  // Find active job for a file
  const getJobForFile = useCallback(
    (file: UploadedFile): Job | undefined => {
      return activeJobs.find((job) => job.worksheet_id === file.id);
    },
    [activeJobs]
  );

  // Get worksheet result for a file
  const getWorksheetForFile = useCallback(
    (file: UploadedFile): WorksheetSummary | undefined => {
      return worksheets.find((ws) => ws.id === file.id);
    },
    [worksheets]
  );

  // Cancel a job
  const handleCancelJob = useCallback(async (jobId: string) => {
    try {
      await api.cancelJob(jobId);
    } catch (error) {
      console.error('Failed to cancel job:', error);
    }
  }, []);

  const handleDelete = async (file: UploadedFile) => {
    if (!confirm(`Delete "${file.filename}"? This will remove the uploaded file but keep any marking results.`)) {
      return;
    }

    setDeleting(file.id);
    try {
      await api.deleteUploadedFile(file.id);
      setFiles((prev) => prev.filter((f) => f.id !== file.id));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete file');
    } finally {
      setDeleting(null);
    }
  };

  const handleMark = async (file: UploadedFile) => {
    try {
      await onMark(file.id, file.student_name);
      onRefreshWorksheets();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to start marking');
    }
  };

  useEffect(() => {
    if (isOpen) {
      fetchFiles();
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

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white rounded-xl shadow-xl w-full max-w-lg mx-4 max-h-[80vh] flex flex-col">
        <div className="flex items-center justify-between p-4 border-b">
          <div>
            <h2 className="text-lg font-semibold">Uploaded Files</h2>
            <p className="text-xs text-gray-500">{files.length} files</p>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={fetchFiles}
              disabled={loading}
              className="px-3 py-1 text-sm bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 disabled:opacity-50 transition-colors"
            >
              {loading ? 'Loading...' : 'Refresh'}
            </button>
            <button onClick={onClose} className="text-gray-500 hover:text-gray-700 text-xl">
              ×
            </button>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto p-4">
          {loading && <p className="text-center text-gray-500">Loading...</p>}
          {error && <p className="text-center text-red-600">{error}</p>}
          {!loading && !error && files.length === 0 && (
            <p className="text-center text-gray-500">No uploaded files</p>
          )}
          {files.map((file) => {
            const activeJob = getJobForFile(file);
            const worksheet = getWorksheetForFile(file);
            const isDeleting = deleting === file.id;

            // Job status flags
            const jobQueued = activeJob?.status === 'queued';
            const jobProcessing = activeJob?.status === 'processing';
            const jobCompleted = activeJob?.status === 'completed';
            const jobFailed = activeJob?.status === 'failed';

            return (
              <div
                key={file.id}
                className="flex items-center justify-between py-3 border-b last:border-b-0"
              >
                <div className="flex-1 min-w-0">
                  <p className="font-medium text-gray-900 truncate">
                    {file.sheet_id ? formatSheetName(file.sheet_id) : file.filename}
                    {file.student_name && (
                      <span className="ml-2 text-gray-500 font-normal">({file.student_name})</span>
                    )}
                    {/* Desktop: inline grade badge */}
                    {worksheet && !activeJob && (
                      <span className="hidden sm:inline ml-2 px-2 py-0.5 bg-green-100 text-green-700 text-xs rounded">
                        Grade {worksheet.grade} ({worksheet.score_percentage.toFixed(0)}% {worksheet.total_questions - worksheet.total_errors}/{worksheet.total_questions})
                      </span>
                    )}
                  </p>
                  {/* Mobile: grade badge on own line */}
                  {worksheet && !activeJob && (
                    <p className="sm:hidden text-sm mt-0.5">
                      <span className="px-2 py-0.5 bg-green-100 text-green-700 text-xs rounded">
                        Grade {worksheet.grade} ({worksheet.score_percentage.toFixed(0)}%)
                      </span>
                      <span className="ml-2 text-gray-500">
                        {worksheet.total_questions - worksheet.total_errors}/{worksheet.total_questions}
                      </span>
                    </p>
                  )}
                  <p className="text-sm text-gray-500">
                    {formatDateTime(file.uploaded_at, timezone)} · {formatFileSize(file.size)}
                  </p>
                  {jobFailed && activeJob?.error && (
                    <p className="text-sm text-red-600 mt-1">{activeJob.error}</p>
                  )}
                </div>

                <div className="flex items-center gap-1 ml-2">
                  {/* Status / Action buttons */}
                  {queueEnabled && activeJob ? (
                    jobCompleted ? (
                      <span className="p-1.5 bg-green-100 text-green-700 rounded" title="Completed">
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                        </svg>
                      </span>
                    ) : jobFailed ? (
                      <button
                        onClick={() => handleMark(file)}
                        className="p-1.5 bg-red-100 text-red-700 rounded hover:bg-red-200 transition-colors"
                        title="Retry"
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                        </svg>
                      </button>
                    ) : jobProcessing ? (
                      <div className="flex items-center gap-1 px-2 py-1 bg-orange-100 text-orange-700 rounded">
                        <div className="w-12 h-2 bg-orange-200 rounded-full overflow-hidden">
                          <div
                            className="h-full bg-orange-500 transition-all duration-300"
                            style={{ width: `${activeJob.progress}%` }}
                          />
                        </div>
                        <span className="text-xs">{activeJob.progress}%</span>
                        <button
                          onClick={() => handleCancelJob(activeJob.id)}
                          className="text-orange-600 hover:text-orange-800"
                          title="Cancel"
                        >
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                          </svg>
                        </button>
                      </div>
                    ) : jobQueued ? (
                      <div className="flex items-center gap-1 px-2 py-1 bg-gray-100 text-gray-600 rounded">
                        <svg className="w-4 h-4 animate-pulse" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
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
                  ) : worksheet ? (
                    <button
                      onClick={() => handleMark(file)}
                      className="p-1.5 bg-gray-100 text-gray-600 rounded hover:bg-gray-200 transition-colors"
                      title="Re-mark"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                      </svg>
                    </button>
                  ) : (
                    <button
                      onClick={() => handleMark(file)}
                      className="p-1.5 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
                      title="Mark"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                    </button>
                  )}

                  {/* Download original button */}
                  <a
                    href={api.getOriginalPdfUrl(file.id, true)}
                    className="p-1.5 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded transition-colors"
                    title="Download original"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                    </svg>
                  </a>

                  {/* Delete button */}
                  <button
                    onClick={() => handleDelete(file)}
                    disabled={isDeleting || !!activeJob}
                    className="p-1.5 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    title={activeJob ? 'Cannot delete while processing' : 'Delete file'}
                  >
                    {isDeleting ? (
                      <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                      </svg>
                    ) : (
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    )}
                  </button>
                </div>
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
