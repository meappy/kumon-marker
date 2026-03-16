import { useState, useEffect, useRef } from 'react';
import type { User, Job, SharedWithMeEntry } from '../api/client';

interface HeaderProps {
  user: User | null;
  onGDriveClick: () => void;
  onUploadsClick: () => void;
  onQueueClick: () => void;
  onSettingsClick: () => void;
  onSharingClick: () => void;
  onLogout: () => void;
  activeJobs?: Job[];
  sharedDashboards?: SharedWithMeEntry[];
  viewingDashboard?: SharedWithMeEntry | null;
  onSwitchDashboard: (dashboard: SharedWithMeEntry | null) => void;
  readOnly?: boolean;
}

export function Header({
  user,
  onGDriveClick,
  onUploadsClick,
  onQueueClick,
  onSettingsClick,
  onSharingClick,
  onLogout,
  activeJobs = [],
  sharedDashboards = [],
  viewingDashboard,
  onSwitchDashboard,
  readOnly = false,
}: HeaderProps) {
  const [menuOpen, setMenuOpen] = useState(false);
  const [dashboardOpen, setDashboardOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);
  const dashboardRef = useRef<HTMLDivElement>(null);

  // Close menu on outside click
  useEffect(() => {
    const handleClick = (e: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        setMenuOpen(false);
      }
      if (dashboardRef.current && !dashboardRef.current.contains(e.target as Node)) {
        setDashboardOpen(false);
      }
    };
    if (menuOpen || dashboardOpen) document.addEventListener('mousedown', handleClick);
    return () => document.removeEventListener('mousedown', handleClick);
  }, [menuOpen, dashboardOpen]);

  // Close menus on ESC
  useEffect(() => {
    const handleKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        setMenuOpen(false);
        setDashboardOpen(false);
      }
    };
    if (menuOpen || dashboardOpen) document.addEventListener('keydown', handleKey);
    return () => document.removeEventListener('keydown', handleKey);
  }, [menuOpen, dashboardOpen]);

  // Calculate queue status
  const queuedCount = activeJobs.filter((j) => j.status === 'queued').length;
  const processingJobs = activeJobs.filter((j) => j.status === 'processing');
  const hasActiveJobs = queuedCount > 0 || processingJobs.length > 0;

  const getQueueButtonText = () => {
    if (processingJobs.length > 0) {
      return `Marking ${processingJobs[0].progress}%`;
    }
    if (queuedCount > 0) {
      return `${queuedCount} queued`;
    }
    return '';
  };

  const handleMenuItem = (action: () => void) => {
    setMenuOpen(false);
    action();
  };

  const handleDashboardSwitch = (dashboard: SharedWithMeEntry | null) => {
    setDashboardOpen(false);
    onSwitchDashboard(dashboard);
  };

  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-4xl mx-auto px-4 py-3 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <img src="/logo.svg" alt="Kumon Marker" className="w-7 h-7" />
          <h1 className="text-lg font-bold text-gray-900">Kumon Marker</h1>

          {/* Dashboard switcher */}
          {sharedDashboards.length > 0 && (
            <div className="relative" ref={dashboardRef}>
              <button
                onClick={() => setDashboardOpen(!dashboardOpen)}
                className={`ml-2 px-2.5 py-1 text-xs rounded-lg border transition-colors ${
                  viewingDashboard
                    ? 'bg-blue-50 border-blue-200 text-blue-700'
                    : 'bg-gray-50 border-gray-200 text-gray-600 hover:bg-gray-100'
                }`}
              >
                {viewingDashboard
                  ? `${viewingDashboard.owner_name || viewingDashboard.owner_email}'s`
                  : 'My Dashboard'}
                <svg className="w-3 h-3 ml-1 inline" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </button>

              {dashboardOpen && (
                <div className="absolute left-0 top-full mt-1 w-56 bg-white rounded-lg shadow-lg border border-gray-200 py-1 z-50">
                  <button
                    onClick={() => handleDashboardSwitch(null)}
                    className={`w-full px-4 py-2 text-left text-sm hover:bg-gray-50 ${
                      !viewingDashboard ? 'text-blue-600 font-medium' : 'text-gray-700'
                    }`}
                  >
                    My Dashboard
                  </button>
                  <div className="border-t border-gray-100 my-1" />
                  <p className="px-4 py-1 text-xs text-gray-400 uppercase tracking-wider">Shared with me</p>
                  {sharedDashboards.map((d) => (
                    <button
                      key={d.owner_user_id}
                      onClick={() => handleDashboardSwitch(d)}
                      className={`w-full px-4 py-2 text-left text-sm hover:bg-gray-50 ${
                        viewingDashboard?.owner_user_id === d.owner_user_id
                          ? 'text-blue-600 font-medium'
                          : 'text-gray-700'
                      }`}
                    >
                      {d.owner_name || d.owner_email}
                      <span className="ml-2 text-xs text-gray-400">
                        {d.permission === 'readwrite' ? 'edit' : 'view'}
                      </span>
                    </button>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
        <div className="flex items-center gap-2">
          {/* Read-only badge */}
          {readOnly && (
            <span className="px-2 py-1 text-xs bg-yellow-50 text-yellow-700 border border-yellow-200 rounded-lg">
              View only
            </span>
          )}

          {/* Queue status badge - only shown when jobs are active */}
          {hasActiveJobs && (
            <button
              onClick={onQueueClick}
              className="relative px-3 py-1.5 text-sm text-white rounded-lg transition-colors overflow-hidden bg-orange-500 hover:bg-orange-600"
            >
              {processingJobs.length > 0 && (
                <div
                  className="absolute inset-0 bg-orange-600 transition-all duration-300"
                  style={{ width: `${processingJobs[0].progress}%` }}
                />
              )}
              <span className="relative">{getQueueButtonText()}</span>
              <span className="absolute top-0 right-0 -mt-1 -mr-1 w-2.5 h-2.5">
                <span className="absolute inline-flex h-full w-full rounded-full bg-orange-400 opacity-75 animate-ping" />
                <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-orange-500" />
              </span>
            </button>
          )}

          {/* User avatar */}
          {user && (
            user.picture ? (
              <img
                src={user.picture}
                alt={user.name || user.email}
                className="w-8 h-8 rounded-full"
              />
            ) : (
              <div className="w-8 h-8 rounded-full bg-gray-300 flex items-center justify-center text-gray-600 text-sm font-medium">
                {(user.name || user.email).charAt(0).toUpperCase()}
              </div>
            )
          )}

          {/* Kebab menu */}
          <div className="relative" ref={menuRef}>
            <button
              onClick={() => setMenuOpen(!menuOpen)}
              className="p-1.5 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
              aria-label="Menu"
            >
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                <circle cx="12" cy="5" r="1.5" />
                <circle cx="12" cy="12" r="1.5" />
                <circle cx="12" cy="19" r="1.5" />
              </svg>
            </button>

            {menuOpen && (
              <div className="absolute right-0 top-full mt-1 w-48 bg-white rounded-lg shadow-lg border border-gray-200 py-1 z-50">
                {!viewingDashboard && (
                  <>
                    <button
                      onClick={() => handleMenuItem(onUploadsClick)}
                      className="w-full px-4 py-2.5 text-left text-sm text-gray-700 hover:bg-gray-50 flex items-center gap-3"
                    >
                      <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                      </svg>
                      Uploads
                    </button>
                    <button
                      onClick={() => handleMenuItem(onGDriveClick)}
                      className="w-full px-4 py-2.5 text-left text-sm text-gray-700 hover:bg-gray-50 flex items-center gap-3"
                    >
                      <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 15a4 4 0 004 4h9a5 5 0 10-.1-9.999 5.002 5.002 0 10-9.78 2.096A4.001 4.001 0 003 15z" />
                      </svg>
                      Google Drive
                    </button>
                    <button
                      onClick={() => handleMenuItem(onSharingClick)}
                      className="w-full px-4 py-2.5 text-left text-sm text-gray-700 hover:bg-gray-50 flex items-center gap-3"
                    >
                      <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z" />
                      </svg>
                      Sharing
                    </button>
                    <button
                      onClick={() => handleMenuItem(onSettingsClick)}
                      className="w-full px-4 py-2.5 text-left text-sm text-gray-700 hover:bg-gray-50 flex items-center gap-3"
                    >
                      <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      </svg>
                      Settings
                    </button>
                  </>
                )}
                {user && (
                  <>
                    {!viewingDashboard && <div className="border-t border-gray-100 my-1" />}
                    <button
                      onClick={() => handleMenuItem(onLogout)}
                      className="w-full px-4 py-2.5 text-left text-sm text-gray-700 hover:bg-gray-50 flex items-center gap-3"
                    >
                      <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                      </svg>
                      Sign out
                    </button>
                  </>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
}
