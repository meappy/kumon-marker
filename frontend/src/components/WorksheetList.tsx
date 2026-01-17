import { useState } from 'react';
import { api } from '../api/client';
import type { WorksheetSummary } from '../api/client';
import { formatSheetNameConsistent } from '../utils/kumon';
import { PdfPreviewModal } from './PdfPreviewModal';

interface WorksheetListProps {
  worksheets: WorksheetSummary[];
  onProcess: (id: string) => void;
  onDelete: (id: string) => void;
  onDeleteAll: () => void;
  processing: string | null;
  deleting: string | null;
  timezone?: string;
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

function gradeColour(grade: string): string {
  switch (grade) {
    case 'A':
      return 'bg-green-100 text-green-800';
    case 'B':
      return 'bg-blue-100 text-blue-800';
    case 'C':
      return 'bg-yellow-100 text-yellow-800';
    default:
      return 'bg-red-100 text-red-800';
  }
}

export function WorksheetList({ worksheets, onProcess, onDelete, onDeleteAll, processing, deleting, timezone }: WorksheetListProps) {
  const [previewModal, setPreviewModal] = useState<{
    isOpen: boolean;
    pdfUrl: string;
    downloadUrl: string;
    title: string;
    filename: string;
  }>({ isOpen: false, pdfUrl: '', downloadUrl: '', title: '', filename: '' });

  const openMarkedPreview = (ws: WorksheetSummary) => {
    const displayName = formatSheetNameConsistent(ws.sheet_id);
    setPreviewModal({
      isOpen: true,
      pdfUrl: api.getMarkedPdfUrl(ws.id),
      downloadUrl: api.getMarkedPdfUrl(ws.id, true),
      title: `Marked: ${displayName}${ws.student_name ? ` (${ws.student_name})` : ''}`,
      filename: `${displayName}-marked.pdf`,
    });
  };

  const openReportPreview = (ws: WorksheetSummary) => {
    const displayName = formatSheetNameConsistent(ws.sheet_id);
    setPreviewModal({
      isOpen: true,
      pdfUrl: api.getReportPdfUrl(ws.id),
      downloadUrl: api.getReportPdfUrl(ws.id, true),
      title: `Report: ${displayName}${ws.student_name ? ` (${ws.student_name})` : ''}`,
      filename: `${displayName}-report.pdf`,
    });
  };

  if (worksheets.length === 0) {
    return (
      <div className="text-center py-12 text-gray-500">
        <p>No worksheets processed yet.</p>
        <p className="text-sm mt-1">Upload a PDF or sync from Google Drive to get started.</p>
      </div>
    );
  }

  return (
    <>
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold text-gray-900">Marked Worksheets</h2>
          <button
            onClick={onDeleteAll}
            disabled={deleting === 'all'}
            className="px-3 py-1.5 bg-red-100 text-red-700 text-sm rounded hover:bg-red-200 disabled:opacity-50"
          >
            {deleting === 'all' ? 'Deleting...' : 'Delete All'}
          </button>
        </div>
        {worksheets.map((ws) => (
        <div
          key={ws.id}
          className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 flex items-center justify-between"
        >
          <div className="flex-1">
            <div className="flex items-center gap-3">
              <span className="font-medium text-gray-900">
                {formatSheetNameConsistent(ws.sheet_id)}
                {ws.student_name && (
                  <span className="ml-2 text-gray-500 font-normal">({ws.student_name})</span>
                )}
              </span>
              <span className={`px-2 py-0.5 rounded text-sm font-medium ${gradeColour(ws.grade)}`}>
                Grade {ws.grade}
              </span>
            </div>
            <div className="text-sm text-gray-500 mt-1">
              {formatDateTime(ws.timestamp, timezone)} · {ws.total_questions - ws.total_errors}/{ws.total_questions} correct
              ({ws.score_percentage.toFixed(0)}%) · {ws.pages} pages
            </div>
          </div>
          <div className="flex items-center gap-2">
            {!ws.has_marked_pdf && (
              <button
                onClick={() => onProcess(ws.id)}
                disabled={processing === ws.id}
                className="px-3 py-1.5 bg-green-600 text-white text-sm rounded hover:bg-green-700 disabled:opacity-50"
              >
                {processing === ws.id ? 'Processing...' : 'Process'}
              </button>
            )}
            {ws.has_marked_pdf && (
              <button
                onClick={() => openMarkedPreview(ws)}
                className="px-3 py-1.5 bg-gray-100 text-gray-700 text-sm rounded hover:bg-gray-200"
              >
                Marked Worksheet
              </button>
            )}
            {ws.has_report && (
              <button
                onClick={() => openReportPreview(ws)}
                className="px-3 py-1.5 bg-blue-100 text-blue-700 text-sm rounded hover:bg-blue-200"
              >
                Report Card
              </button>
            )}
            <button
              onClick={() => onDelete(ws.id)}
              disabled={deleting === ws.id}
              className="p-1.5 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded disabled:opacity-50"
              title="Delete worksheet"
            >
              {deleting === ws.id ? (
                <svg className="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
              ) : (
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              )}
            </button>
          </div>
        </div>
        ))}
      </div>

      <PdfPreviewModal
        isOpen={previewModal.isOpen}
        onClose={() => setPreviewModal({ ...previewModal, isOpen: false })}
        pdfUrl={previewModal.pdfUrl}
        downloadUrl={previewModal.downloadUrl}
        title={previewModal.title}
        filename={previewModal.filename}
      />
    </>
  );
}
