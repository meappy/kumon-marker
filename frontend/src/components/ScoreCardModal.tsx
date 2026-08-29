import { useCallback, useEffect, useState } from 'react';
import { api } from '../api/client';
import type { PrinterList, ScoreEntry, ScoreLog } from '../api/client';

interface ScoreCardModalProps {
  isOpen: boolean;
  onClose: () => void;
  readOnly?: boolean;
}

const MARK_COLUMNS = 5;

/** Fields a row can be corrected on — handwritten times are the usual reason. */
const EDITABLE: { key: keyof ScoreEntry; label: string; width: string }[] = [
  { key: 'date', label: 'Date', width: 'w-16' },
  { key: 'time_started', label: 'Started', width: 'w-16' },
  { key: 'time_finished', label: 'Finished', width: 'w-16' },
  { key: 'time_used', label: 'Mins', width: 'w-12' },
  { key: 'level', label: 'Level', width: 'w-10' },
  { key: 'sheet_no', label: 'Sheet', width: 'w-14' },
];

export function ScoreCardModal({ isOpen, onClose, readOnly = false }: ScoreCardModalProps) {
  const [logs, setLogs] = useState<ScoreLog[]>([]);
  const [student, setStudent] = useState<string | null>(null);
  const [printers, setPrinters] = useState<PrinterList | null>(null);
  const [loading, setLoading] = useState(false);
  const [busy, setBusy] = useState<string | null>(null);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const [scoreLogs, printerList] = await Promise.all([
        api.getScoreCards(),
        api.getPrinters().catch(() => ({ available: false, printers: [] })),
      ]);
      setLogs(scoreLogs);
      setPrinters(printerList);
      setStudent((current) =>
        current && scoreLogs.some((l) => l.student === current)
          ? current
          : scoreLogs[0]?.student ?? null,
      );
    } catch (err) {
      setMessage({ type: 'error', text: err instanceof Error ? err.message : 'Failed to load' });
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (isOpen) load();
  }, [isOpen, load]);

  if (!isOpen) return null;

  const current = logs.find((l) => l.student === student);
  const entries = current?.entries ?? [];

  const patch = async (entry: ScoreEntry, key: keyof ScoreEntry, value: string) => {
    if (!student || readOnly) return;
    const previous = entry[key];
    if (String(previous) === value) return;

    setLogs((all) =>
      all.map((log) =>
        log.student === student
          ? {
              ...log,
              entries: log.entries.map((e) => (e.id === entry.id ? { ...e, [key]: value } : e)),
            }
          : log,
      ),
    );
    try {
      await api.updateScoreEntry(student, entry.id, { [key]: value });
    } catch (err) {
      setMessage({ type: 'error', text: err instanceof Error ? err.message : 'Save failed' });
      load();
    }
  };

  const patchMark = async (entry: ScoreEntry, index: number, value: string) => {
    if (!student || readOnly) return;
    const marks = [...entry.marks];
    while (marks.length <= index) marks.push('');
    marks[index] = value.toUpperCase().slice(0, 1);
    setLogs((all) =>
      all.map((log) =>
        log.student === student
          ? { ...log, entries: log.entries.map((e) => (e.id === entry.id ? { ...e, marks } : e)) }
          : log,
      ),
    );
    try {
      await api.updateScoreEntry(student, entry.id, { marks });
    } catch (err) {
      setMessage({ type: 'error', text: err instanceof Error ? err.message : 'Save failed' });
      load();
    }
  };

  const remove = async (entry: ScoreEntry) => {
    if (!student || readOnly) return;
    if (!window.confirm(`Remove the ${entry.level}${entry.sheet_no} row?`)) return;
    try {
      await api.deleteScoreEntry(student, entry.id);
      load();
    } catch (err) {
      setMessage({ type: 'error', text: err instanceof Error ? err.message : 'Delete failed' });
    }
  };

  const print = async () => {
    if (!student) return;
    setBusy('print');
    setMessage(null);
    try {
      const result = await api.printScoreCard(student);
      setMessage({ type: 'success', text: `Sent to printer (job ${result.job_id})` });
    } catch (err) {
      setMessage({ type: 'error', text: err instanceof Error ? err.message : 'Print failed' });
    } finally {
      setBusy(null);
    }
  };

  const printerName =
    printers?.printers.find((p) => p.is_default)?.name ?? printers?.printers[0]?.name;

  return (
    <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-xl w-full max-w-5xl max-h-[85vh] flex flex-col">
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200">
          <div>
            <h2 className="text-lg font-semibold text-gray-900">Score Report</h2>
            <p className="text-sm text-gray-500">
              One row per packet, recorded as each worksheet is marked
            </p>
          </div>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600" aria-label="Close">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {message && (
          <div
            className={`mx-6 mt-4 px-3 py-2 rounded-lg text-sm ${
              message.type === 'success'
                ? 'bg-green-50 text-green-700 border border-green-200'
                : 'bg-red-50 text-red-700 border border-red-200'
            }`}
          >
            {message.text}
          </div>
        )}

        <div className="px-6 py-4 flex flex-wrap items-center gap-2 border-b border-gray-100">
          {logs.map((log) => (
            <button
              key={log.student}
              onClick={() => setStudent(log.student)}
              className={`px-3 py-1.5 rounded-lg text-sm ${
                log.student === student
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {log.student}
              <span className="ml-2 opacity-70">{log.entries.length}</span>
            </button>
          ))}

          {student && (
            <div className="ml-auto flex items-center gap-2">
              <a
                href={api.getScoreCardPdfUrl(student)}
                target="_blank"
                rel="noreferrer"
                className="px-3 py-1.5 rounded-lg text-sm bg-gray-100 text-gray-700 hover:bg-gray-200"
              >
                Download PDF
              </a>
              <button
                onClick={print}
                disabled={busy === 'print' || !printers?.available}
                title={
                  printers?.available
                    ? `Print to ${printerName ?? 'the default printer'}`
                    : 'No printer available on the server'
                }
                className="px-3 py-1.5 rounded-lg text-sm bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-50"
              >
                {busy === 'print' ? 'Sending…' : 'Print'}
              </button>
            </div>
          )}
        </div>

        <div className="flex-1 overflow-auto px-6 py-4">
          {loading ? (
            <div className="text-center py-12 text-gray-500">Loading…</div>
          ) : entries.length === 0 ? (
            <div className="text-center py-12 text-gray-500">
              No rows yet. Mark a worksheet and a row is added automatically.
            </div>
          ) : (
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-xs uppercase tracking-wide text-gray-500">
                  {EDITABLE.map((field) => (
                    <th key={field.key} className="pb-2 pr-2 font-medium">
                      {field.label}
                    </th>
                  ))}
                  <th className="pb-2 pr-2 font-medium" colSpan={MARK_COLUMNS}>
                    Marks
                  </th>
                  <th className="pb-2" />
                </tr>
              </thead>
              <tbody>
                {entries.map((entry) => (
                  <tr key={entry.id} className="border-t border-gray-100">
                    {EDITABLE.map((field) => (
                      <td key={field.key} className="py-1 pr-2">
                        <input
                          defaultValue={String(entry[field.key] ?? '')}
                          onBlur={(e) => patch(entry, field.key, e.target.value)}
                          readOnly={readOnly}
                          className={`${field.width} px-1.5 py-1 rounded border border-transparent hover:border-gray-200 focus:border-blue-400 focus:outline-none read-only:hover:border-transparent`}
                        />
                      </td>
                    ))}
                    {Array.from({ length: MARK_COLUMNS }).map((_, i) => (
                      <td key={i} className="py-1 pr-1">
                        <input
                          defaultValue={entry.marks[i] ?? ''}
                          onBlur={(e) => patchMark(entry, i, e.target.value)}
                          readOnly={readOnly}
                          maxLength={1}
                          className="w-7 px-1 py-1 text-center rounded border border-transparent hover:border-gray-200 focus:border-blue-400 focus:outline-none read-only:hover:border-transparent"
                        />
                      </td>
                    ))}
                    <td className="py-1 text-right">
                      {!readOnly && (
                        <button
                          onClick={() => remove(entry)}
                          className="text-gray-400 hover:text-red-600 px-2"
                          title="Remove row"
                        >
                          ×
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

        <div className="px-6 py-3 border-t border-gray-100 text-xs text-gray-500">
          Grades come from the marking percentage, not each sheet's printed mistakes
          table — check them against the worksheet before filing the card.
        </div>
      </div>
    </div>
  );
}
