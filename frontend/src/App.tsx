import { useCallback, useEffect, useState, useRef } from 'react';
import { api } from './api/client';
import type { WorksheetSummary, AuthStatus, Job } from './api/client';
import { Header } from './components/Header';
import { Uploader } from './components/Uploader';
import { WorksheetList } from './components/WorksheetList';
import { GDriveModal } from './components/GDriveModal';
import { SettingsModal } from './components/SettingsModal';
import { LoginPage } from './components/LoginPage';
import { QueuePanel } from './components/QueuePanel';

function App() {
  // Auth state
  const [authStatus, setAuthStatus] = useState<AuthStatus | null>(null);
  const [authLoading, setAuthLoading] = useState(true);
  const [authError, setAuthError] = useState<string | null>(null);

  // App state
  const [worksheets, setWorksheets] = useState<WorksheetSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [processing, setProcessing] = useState<string | null>(null);
  const [deleting, setDeleting] = useState<string | null>(null);
  const [showGDrive, setShowGDrive] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [showQueue, setShowQueue] = useState(false);
  const [, setSyncing] = useState(false);
  const [notification, setNotification] = useState<{ type: 'success' | 'error'; message: string } | null>(null);
  const [timezone, setTimezone] = useState<string>('Australia/Sydney');

  // Job queue state
  const [activeJobs, setActiveJobs] = useState<Job[]>([]);
  const [queueEnabled, setQueueEnabled] = useState(false);
  const pollIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  // Check auth status on load
  useEffect(() => {
    const checkAuth = async () => {
      try {
        const status = await api.getAuthStatus();
        setAuthStatus(status);
      } catch (err) {
        console.error('Auth check failed:', err);
        setAuthStatus({ authenticated: false, user: null, google_drive_connected: false });
      } finally {
        setAuthLoading(false);
      }
    };

    // Check for auth callback results in URL
    const params = new URLSearchParams(window.location.search);
    const authSuccess = params.get('auth_success');
    const error = params.get('auth_error');

    if (error) {
      setAuthError(error);
      // Clean URL
      window.history.replaceState({}, '', window.location.pathname);
    } else if (authSuccess) {
      setNotification({ type: 'success', message: 'Signed in successfully!' });
      window.history.replaceState({}, '', window.location.pathname);
    }

    checkAuth();
  }, []);

  // Auto-dismiss notifications
  useEffect(() => {
    if (notification) {
      const timer = setTimeout(() => setNotification(null), 5000);
      return () => clearTimeout(timer);
    }
  }, [notification]);

  const loadWorksheets = useCallback(async () => {
    if (!authStatus?.authenticated) return;

    try {
      const data = await api.listWorksheets();
      setWorksheets(data);
    } catch (err) {
      console.error('Failed to load worksheets:', err);
    } finally {
      setLoading(false);
    }
  }, [authStatus?.authenticated]);

  const loadSettings = useCallback(async () => {
    try {
      const settings = await api.getSettings();
      setTimezone(settings.timezone.value);
    } catch (err) {
      console.error('Failed to load settings:', err);
    }
  }, []);

  useEffect(() => {
    if (authStatus?.authenticated) {
      loadWorksheets();
      loadSettings();
    }
  }, [authStatus?.authenticated, loadWorksheets, loadSettings]);

  // Poll job status when there are active jobs
  const pollJobStatus = useCallback(async () => {
    if (!authStatus?.authenticated) return;

    try {
      const status = await api.getQueueStatus();
      setQueueEnabled(status.enabled);
      setActiveJobs(status.jobs);

      // Reload worksheets if a job just completed
      const completedJobs = status.jobs.filter((j) => j.status === 'completed');
      if (completedJobs.length > 0) {
        loadWorksheets();
      }
    } catch (err) {
      console.error('Failed to poll job status:', err);
    }
  }, [authStatus?.authenticated, loadWorksheets]);

  // Start/stop polling based on active jobs
  useEffect(() => {
    // Initial poll on mount
    if (authStatus?.authenticated) {
      pollJobStatus();
    }

    // Set up interval polling when modal is open or there are active jobs
    const shouldPoll = authStatus?.authenticated && (showGDrive || activeJobs.length > 0);

    if (shouldPoll && !pollIntervalRef.current) {
      pollIntervalRef.current = setInterval(pollJobStatus, 2000);
    } else if (!shouldPoll && pollIntervalRef.current) {
      clearInterval(pollIntervalRef.current);
      pollIntervalRef.current = null;
    }

    return () => {
      if (pollIntervalRef.current) {
        clearInterval(pollIntervalRef.current);
        pollIntervalRef.current = null;
      }
    };
  }, [authStatus?.authenticated, showGDrive, activeJobs.length, pollJobStatus]);

  const handleLogout = useCallback(async () => {
    try {
      await api.logout();
      setAuthStatus({ authenticated: false, user: null, google_drive_connected: false });
      setWorksheets([]);
    } catch (err) {
      console.error('Logout failed:', err);
    }
  }, []);

  const handleUpload = useCallback(
    async (file: File) => {
      const result = await api.uploadWorksheet(file);
      // Process immediately after upload
      setProcessing(result.id);
      try {
        await api.processWorksheet(result.id);
        // Wait a bit for processing to complete
        setTimeout(loadWorksheets, 2000);
      } finally {
        setProcessing(null);
      }
    },
    [loadWorksheets]
  );

  const handleProcess = useCallback(
    async (id: string) => {
      setProcessing(id);
      try {
        await api.processWorksheet(id);
        setTimeout(loadWorksheets, 2000);
      } finally {
        setProcessing(null);
      }
    },
    [loadWorksheets]
  );

  const handleGDriveSync = useCallback(
    async (fileId: string, filename: string, studentName: string | null) => {
      setSyncing(true);
      try {
        const result = await api.syncFromGDrive(fileId, filename);
        // Process immediately, passing the pre-extracted student name
        setProcessing(result.id);
        await api.processWorksheet(result.id, studentName);
        setTimeout(loadWorksheets, 2000);
      } finally {
        setSyncing(false);
        setProcessing(null);
      }
    },
    [loadWorksheets]
  );

  const handleDelete = useCallback(
    async (id: string) => {
      if (!confirm('Are you sure you want to delete this worksheet?')) return;
      setDeleting(id);
      try {
        await api.deleteWorksheet(id);
        setNotification({ type: 'success', message: 'Worksheet deleted' });
        loadWorksheets();
      } catch (err) {
        setNotification({ type: 'error', message: `Failed to delete: ${err}` });
      } finally {
        setDeleting(null);
      }
    },
    [loadWorksheets]
  );

  const handleDeleteAll = useCallback(async () => {
    if (!confirm('Are you sure you want to delete ALL worksheets? This cannot be undone.')) return;
    setDeleting('all');
    try {
      await api.deleteAllWorksheets();
      setNotification({ type: 'success', message: 'All worksheets deleted' });
      loadWorksheets();
    } catch (err) {
      setNotification({ type: 'error', message: `Failed to delete: ${err}` });
    } finally {
      setDeleting(null);
    }
  }, [loadWorksheets]);

  // Show loading while checking auth
  if (authLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-gray-500">Loading...</div>
      </div>
    );
  }

  // Show login page if not authenticated
  if (!authStatus?.authenticated) {
    return <LoginPage error={authError || undefined} />;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header
        user={authStatus.user}
        onGDriveClick={() => setShowGDrive(true)}
        onQueueClick={() => setShowQueue(true)}
        onSettingsClick={() => setShowSettings(true)}
        onLogout={handleLogout}
        activeJobs={activeJobs}
      />

      {/* Notification banner */}
      {notification && (
        <div
          className={`mx-auto max-w-4xl mt-4 px-4 py-3 rounded-lg ${
            notification.type === 'success'
              ? 'bg-green-50 text-green-700 border border-green-200'
              : 'bg-red-50 text-red-700 border border-red-200'
          }`}
        >
          <div className="flex items-center justify-between">
            <span>{notification.message}</span>
            <button
              onClick={() => setNotification(null)}
              className="text-current opacity-60 hover:opacity-100"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>
      )}

      <main className="max-w-4xl mx-auto px-4 py-8">
        <div className="mb-8">
          <Uploader onUpload={handleUpload} />
        </div>

        {loading ? (
          <div className="text-center py-12 text-gray-500">Loading...</div>
        ) : (
          <WorksheetList
            worksheets={worksheets}
            onProcess={handleProcess}
            onDelete={handleDelete}
            onDeleteAll={handleDeleteAll}
            processing={processing}
            deleting={deleting}
            timezone={timezone}
          />
        )}
      </main>

      <GDriveModal
        isOpen={showGDrive}
        onClose={() => setShowGDrive(false)}
        onSync={handleGDriveSync}
        worksheets={worksheets}
        timezone={timezone}
        activeJobs={activeJobs}
        queueEnabled={queueEnabled}
      />

      <SettingsModal
        isOpen={showSettings}
        onClose={() => {
          setShowSettings(false);
          loadSettings(); // Reload settings to get updated timezone
        }}
      />

      <QueuePanel
        isOpen={showQueue}
        onClose={() => setShowQueue(false)}
        jobs={activeJobs}
      />
    </div>
  );
}

export default App;
