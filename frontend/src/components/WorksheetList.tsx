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

type SortOption = 'date-desc' | 'date-asc' | 'student' | 'grade' | 'score-desc' | 'score-asc';

const ITEMS_PER_PAGE = 10;

export function WorksheetList({ worksheets, onProcess, onDelete, onDeleteAll, processing, deleting, timezone }: WorksheetListProps) {
  const [sortBy, setSortBy] = useState<SortOption>('date-desc');
  const [currentPage, setCurrentPage] = useState(1);
  const [previewModal, setPreviewModal] = useState<{
    isOpen: boolean;
    pdfUrl: string;
    downloadUrl: string;
    title: string;
    filename: string;
  }>({ isOpen: false, pdfUrl: '', downloadUrl: '', title: '', filename: '' });

  // Sort worksheets based on selected option
  const sortedWorksheets = [...worksheets].sort((a, b) => {
    switch (sortBy) {
      case 'date-desc':
        return new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime();
      case 'date-asc':
        return new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime();
      case 'student':
        return (a.student_name || '').localeCompare(b.student_name || '');
      case 'grade':
        return a.grade.localeCompare(b.grade);
      case 'score-desc':
        return b.score_percentage - a.score_percentage;
      case 'score-asc':
        return a.score_percentage - b.score_percentage;
      default:
        return 0;
    }
  });

  // Pagination
  const totalPages = Math.ceil(sortedWorksheets.length / ITEMS_PER_PAGE);
  const startIndex = (currentPage - 1) * ITEMS_PER_PAGE;
  const paginatedWorksheets = sortedWorksheets.slice(startIndex, startIndex + ITEMS_PER_PAGE);

  // Reset to page 1 when sort changes
  const handleSortChange = (newSort: SortOption) => {
    setSortBy(newSort);
    setCurrentPage(1);
  };

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

  const openOriginalPreview = (ws: WorksheetSummary) => {
    const displayName = formatSheetNameConsistent(ws.sheet_id);
    setPreviewModal({
      isOpen: true,
      pdfUrl: api.getOriginalPdfUrl(ws.id),
      downloadUrl: api.getOriginalPdfUrl(ws.id, true),
      title: `Original: ${displayName}${ws.student_name ? ` (${ws.student_name})` : ''}`,
      filename: `${displayName}-original.pdf`,
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
          <div className="flex items-center gap-3">
            <select
              value={sortBy}
              onChange={(e) => handleSortChange(e.target.value as SortOption)}
              className="px-2 py-1.5 text-sm border border-gray-300 rounded-lg bg-white text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="date-desc">Newest first</option>
              <option value="date-asc">Oldest first</option>
              <option value="student">By student</option>
              <option value="grade">By grade</option>
              <option value="score-desc">Highest score</option>
              <option value="score-asc">Lowest score</option>
            </select>
            <button
              onClick={onDeleteAll}
              disabled={deleting === 'all'}
              className="px-3 py-1.5 bg-red-100 text-red-700 text-sm rounded hover:bg-red-200 disabled:opacity-50"
            >
              {deleting === 'all' ? 'Deleting...' : 'Delete All'}
            </button>
          </div>
        </div>
        {paginatedWorksheets.map((ws) => (
        <div
          key={ws.id}
          className="bg-white rounded-lg shadow-sm border border-gray-200 p-3 sm:p-4"
        >
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
            <div className="flex-1 min-w-0">
              <div className="flex flex-wrap items-center gap-2">
                <span className="font-medium text-gray-900">
                  {formatSheetNameConsistent(ws.sheet_id)}
                  {ws.student_name && (
                    <span className="ml-1 text-gray-500 font-normal">({ws.student_name})</span>
                  )}
                </span>
                <span className={`px-2 py-0.5 rounded text-xs font-medium ${gradeColour(ws.grade)}`}>
                  {ws.grade}
                </span>
              </div>
              <div className="text-xs sm:text-sm text-gray-500 mt-1">
                {formatDateTime(ws.timestamp, timezone)} · {ws.total_questions - ws.total_errors}/{ws.total_questions} ({ws.score_percentage.toFixed(0)}%) · {ws.pages} {ws.pages === 1 ? 'page' : 'pages'}
              </div>
            </div>
            <div className="flex items-center gap-1">
              {!ws.has_marked_pdf && (
                <button
                  onClick={() => onProcess(ws.id)}
                  disabled={processing === ws.id}
                  className="p-1.5 bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50"
                  title="Process"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </button>
              )}
              <button
                onClick={() => openOriginalPreview(ws)}
                className="p-1.5 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded"
                title="Original PDF"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                </svg>
              </button>
              {ws.has_marked_pdf && (
                <button
                  onClick={() => openMarkedPreview(ws)}
                  className="p-1.5 text-green-600 hover:text-green-700 hover:bg-green-50 rounded"
                  title="Marked Worksheet"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </button>
              )}
              {ws.has_report && (
                <button
                  onClick={() => openReportPreview(ws)}
                  className="p-1.5 text-blue-600 hover:text-blue-700 hover:bg-blue-50 rounded"
                  title="Report Card"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </button>
              )}
              <button
                onClick={() => onDelete(ws.id)}
                disabled={deleting === ws.id}
                className="p-1.5 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded disabled:opacity-50"
                title="Delete"
              >
                {deleting === ws.id ? (
                  <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                  </svg>
                ) : (
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                )}
              </button>
            </div>
          </div>
        </div>
        ))}

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="flex items-center justify-center gap-2 pt-4">
            <button
              onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
              disabled={currentPage === 1}
              className="p-2 text-gray-600 hover:bg-gray-100 rounded disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
            </button>
            <span className="text-sm text-gray-600">
              Page {currentPage} of {totalPages}
            </span>
            <button
              onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
              disabled={currentPage === totalPages}
              className="p-2 text-gray-600 hover:bg-gray-100 rounded disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </button>
          </div>
        )}
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
