import { useCallback, useEffect, useState } from 'react';
import { api } from '../api/client';
import type { AppSettings, GoogleAuthStatus } from '../api/client';

interface SettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
}

type SettingKey = 'gdrive_folder' | 'timezone';

// Common IANA timezone names
const TIMEZONES = [
  'Australia/Sydney',
  'Australia/Melbourne',
  'Australia/Brisbane',
  'Australia/Perth',
  'Australia/Adelaide',
  'Pacific/Auckland',
  'Asia/Singapore',
  'Asia/Hong_Kong',
  'Asia/Tokyo',
  'Asia/Shanghai',
  'Europe/London',
  'Europe/Paris',
  'Europe/Berlin',
  'America/New_York',
  'America/Chicago',
  'America/Denver',
  'America/Los_Angeles',
  'UTC',
];

export function SettingsModal({ isOpen, onClose }: SettingsModalProps) {
  const [settings, setSettings] = useState<AppSettings | null>(null);
  const [googleStatus, setGoogleStatus] = useState<GoogleAuthStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Form state
  const [folder, setFolder] = useState('');
  const [timezone, setTimezone] = useState('');

  const loadSettings = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [settingsData, authStatus] = await Promise.all([
        api.getSettings(),
        api.getGoogleAuthStatus(),
      ]);
      setSettings(settingsData);
      setGoogleStatus(authStatus);

      // Initialize form with current values
      setFolder(settingsData.gdrive_folder.value);
      setTimezone(settingsData.timezone.value);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load settings');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (isOpen) {
      loadSettings();
    }
  }, [isOpen, loadSettings]);

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

  const handleSave = async () => {
    setSaving(true);
    setError(null);
    try {
      const updates: Record<string, string> = {};
      if (folder !== settings?.gdrive_folder.value) updates.gdrive_folder = folder;
      if (timezone !== settings?.timezone.value) updates.timezone = timezone;

      if (Object.keys(updates).length > 0) {
        const updated = await api.updateSettings(updates);
        setSettings(updated);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save settings');
    } finally {
      setSaving(false);
    }
  };

  const handleReset = async (key: SettingKey) => {
    try {
      await api.resetSetting(key);
      await loadSettings();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to reset setting');
    }
  };

  const handleGoogleConnect = async () => {
    try {
      const { url } = await api.getGoogleAuthUrl();
      window.location.href = url;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to get auth URL');
    }
  };

  const handleGoogleDisconnect = async () => {
    try {
      await api.disconnectGoogle();
      setGoogleStatus({ connected: false, email: null });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to disconnect');
    }
  };

  if (!isOpen) return null;

  const getSourceBadge = (source: string) => {
    const colors = {
      default: 'bg-gray-100 text-gray-600',
      env: 'bg-blue-100 text-blue-600',
      user: 'bg-green-100 text-green-600',
    };
    return (
      <span className={`text-xs px-2 py-0.5 rounded ${colors[source as keyof typeof colors] || colors.default}`}>
        {source}
      </span>
    );
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white rounded-xl shadow-xl w-full max-w-lg mx-4 max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b">
          <h2 className="text-lg font-semibold">Settings</h2>
          <button
            onClick={onClose}
            className="p-1 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Content */}
        <div className="p-4 space-y-6">
          {loading ? (
            <div className="text-center py-8 text-gray-500">Loading settings...</div>
          ) : (
            <>
              {error && (
                <div className="p-3 bg-red-50 text-red-700 rounded-lg text-sm">
                  {error}
                </div>
              )}

              {/* Google Drive Connection */}
              <div className="space-y-3">
                <h3 className="font-medium text-gray-900">Google Drive</h3>
                {settings?.google_configured ? (
                  <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div>
                      {googleStatus?.connected ? (
                        <div className="flex items-center gap-2">
                          <span className="w-2 h-2 bg-green-500 rounded-full" />
                          <span className="text-sm text-gray-700">
                            Connected{googleStatus.email ? ` as ${googleStatus.email}` : ''}
                          </span>
                        </div>
                      ) : (
                        <div className="flex items-center gap-2">
                          <span className="w-2 h-2 bg-gray-400 rounded-full" />
                          <span className="text-sm text-gray-500">Not connected</span>
                        </div>
                      )}
                    </div>
                    {googleStatus?.connected ? (
                      <button
                        onClick={handleGoogleDisconnect}
                        className="text-sm text-red-600 hover:text-red-700"
                      >
                        Disconnect
                      </button>
                    ) : (
                      <button
                        onClick={handleGoogleConnect}
                        className="px-3 py-1.5 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700"
                      >
                        Connect
                      </button>
                    )}
                  </div>
                ) : (
                  <div className="p-3 bg-yellow-50 text-yellow-700 rounded-lg text-sm">
                    Google OAuth not configured. Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET environment variables.
                  </div>
                )}
              </div>

              {/* Google Drive Folder */}
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <label className="font-medium text-gray-900">Google Drive Folder</label>
                  {settings && getSourceBadge(settings.gdrive_folder.source)}
                </div>
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={folder}
                    onChange={(e) => setFolder(e.target.value)}
                    placeholder="Folder name in Google Drive"
                    className="flex-1 px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                  {settings?.gdrive_folder.source === 'user' && (
                    <button
                      onClick={() => handleReset('gdrive_folder')}
                      className="px-3 py-2 text-gray-600 hover:bg-gray-100 rounded-lg text-sm"
                      title="Reset to default"
                    >
                      Reset
                    </button>
                  )}
                </div>
                <p className="text-xs text-gray-500">
                  Name of the folder in Google Drive containing scanned worksheets
                </p>
              </div>

              {/* Timezone */}
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <label className="font-medium text-gray-900">Timezone</label>
                  {settings && getSourceBadge(settings.timezone.source)}
                </div>
                <div className="flex gap-2">
                  <select
                    value={timezone}
                    onChange={(e) => setTimezone(e.target.value)}
                    className="flex-1 px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  >
                    {TIMEZONES.map((tz) => (
                      <option key={tz} value={tz}>
                        {tz}
                      </option>
                    ))}
                  </select>
                  {settings?.timezone.source === 'user' && (
                    <button
                      onClick={() => handleReset('timezone')}
                      className="px-3 py-2 text-gray-600 hover:bg-gray-100 rounded-lg text-sm"
                      title="Reset to default"
                    >
                      Reset
                    </button>
                  )}
                </div>
                <p className="text-xs text-gray-500">
                  Timezone for displaying dates and times
                </p>
              </div>
            </>
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between p-4 border-t">
          <span className="text-xs text-gray-400">
            v{__APP_VERSION__}
          </span>
          <div className="flex gap-3">
            <button
              onClick={onClose}
              className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
            >
              Cancel
            </button>
            <button
              onClick={handleSave}
              disabled={saving || loading}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {saving ? 'Saving...' : 'Save Changes'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
