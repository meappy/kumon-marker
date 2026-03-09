import { useEffect } from 'react';
import type { Job } from '../api/client';
import { api } from '../api/client';

function formatJobName(worksheetId: string): string {
  // Format: 20260309203533_001 → "9 Mar 20:35 #001"
  const match = worksheetId.match(/^(\d{4})(\d{2})(\d{2})(\d{2})(\d{2})\d{2}_(.+)$/);
  if (match) {
    const [, , month, day, hour, minute, seq] = match;
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    const monthName = months[parseInt(month, 10) - 1] || month;
    return `${parseInt(day, 10)} ${monthName} ${hour}:${minute} #${seq}`;
  }
  // Fallback: just show the ID
  return worksheetId;
}

interface QueuePanelProps {
  isOpen: boolean;
  onClose: () => void;
  jobs: Job[];
}

export function QueuePanel({ isOpen, onClose, jobs }: QueuePanelProps) {
  // Close on ESC
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) onClose();
    };
    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const handleCancel = async (jobId: string) => {
    try {
      await api.cancelJob(jobId);
    } catch (error) {
      console.error('Failed to cancel job:', error);
    }
  };

  const getStatusDisplay = (job: Job) => {
    switch (job.status) {
      case 'processing':
        return (
          <div className="flex items-center gap-2">
            <div className="w-20 h-2 bg-orange-200 rounded-full overflow-hidden">
              <div
                className="h-full bg-orange-500 transition-all duration-300"
                style={{ width: `${job.progress}%` }}
              />
            </div>
            <span className="text-sm text-orange-600">{job.progress}%</span>
            <button
              onClick={() => handleCancel(job.id)}
              className="text-gray-400 hover:text-red-500"
              title="Cancel"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        );
      case 'queued':
        return (
          <div className="flex items-center gap-2">
            <span className="text-sm text-gray-500 animate-pulse">Queued</span>
            <button
              onClick={() => handleCancel(job.id)}
              className="text-gray-400 hover:text-red-500"
              title="Cancel"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        );
      case 'completed':
        return (
          <span className="text-sm text-green-600 flex items-center gap-1">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
            Done
          </span>
        );
      case 'failed':
        return (
          <span className="text-sm text-red-600">Failed</span>
        );
      case 'cancelled':
        return (
          <span className="text-sm text-gray-400">Cancelled</span>
        );
      default:
        return null;
    }
  };

  // Sort: processing first, then queued, then others
  const sortedJobs = [...jobs].sort((a, b) => {
    const order = { processing: 0, queued: 1, completed: 2, failed: 3, cancelled: 4 };
    return (order[a.status as keyof typeof order] ?? 5) - (order[b.status as keyof typeof order] ?? 5);
  });

  return (
    <div className="fixed inset-0 z-50" onClick={onClose}>
      {/* Backdrop */}
      <div className="absolute inset-0 bg-black/20" />

      {/* Panel - positioned below header */}
      <div
        className="absolute top-16 right-4 w-80 bg-white rounded-lg shadow-xl border border-gray-200 overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="p-3 border-b bg-gray-50 flex items-center justify-between">
          <h3 className="font-medium text-gray-900">Marking Queue</h3>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div className="max-h-80 overflow-y-auto">
          {sortedJobs.length === 0 ? (
            <div className="p-4 text-center text-gray-500 text-sm">
              No jobs in queue
            </div>
          ) : (
            <div className="divide-y">
              {sortedJobs.map((job) => (
                <div key={job.id} className="p-3 flex items-center justify-between">
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900 truncate">
                      {formatJobName(job.worksheet_id)}
                    </p>
                    {job.error && (
                      <p className="text-xs text-red-500 truncate">{job.error}</p>
                    )}
                  </div>
                  {getStatusDisplay(job)}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
