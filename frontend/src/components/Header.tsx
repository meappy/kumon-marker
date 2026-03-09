import { useState, useEffect, useRef } from 'react';
import type { User, Job } from '../api/client';

interface HeaderProps {
  user: User | null;
  onGDriveClick: () => void;
  onUploadsClick: () => void;
  onQueueClick: () => void;
  onSettingsClick: () => void;
  onLogout: () => void;
  activeJobs?: Job[];
}

export function Header({ user, onGDriveClick, onUploadsClick, onQueueClick, onSettingsClick, onLogout, activeJobs = [] }: HeaderProps) {
  const [menuOpen, setMenuOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  // Close menu on outside click
  useEffect(() => {
    const handleClick = (e: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        setMenuOpen(false);
      }
    };
    if (menuOpen) document.addEventListener('mousedown', handleClick);
    return () => document.removeEventListener('mousedown', handleClick);
  }, [menuOpen]);

  // Close menu on ESC
  useEffect(() => {
    const handleKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') setMenuOpen(false);
    };
    if (menuOpen) document.addEventListener('keydown', handleKey);
    return () => document.removeEventListener('keydown', handleKey);
  }, [menuOpen]);

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

  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-2xl mx-auto px-4 py-3 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <img src="/logo.svg" alt="Kumon Marker" className="w-7 h-7" />
          <h1 className="text-lg font-bold text-gray-900">Kumon Marker</h1>
        </div>
        <div className="flex items-center gap-2">
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
                  onClick={() => handleMenuItem(onSettingsClick)}
                  className="w-full px-4 py-2.5 text-left text-sm text-gray-700 hover:bg-gray-50 flex items-center gap-3"
                >
                  <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  </svg>
                  Settings
                </button>
                {user && (
                  <>
                    <div className="border-t border-gray-100 my-1" />
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
