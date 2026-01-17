import type { User, Job } from '../api/client';

interface HeaderProps {
  user: User | null;
  onGDriveClick: () => void;
  onQueueClick: () => void;
  onSettingsClick: () => void;
  onLogout: () => void;
  syncing: boolean;
  activeJobs?: Job[];
  queueEnabled?: boolean;
}

export function Header({ user, onGDriveClick, onQueueClick, onSettingsClick, onLogout, syncing, activeJobs = [], queueEnabled = false }: HeaderProps) {
  // Calculate queue status
  const queuedCount = activeJobs.filter((j) => j.status === 'queued').length;
  const processingJobs = activeJobs.filter((j) => j.status === 'processing');
  const hasActiveJobs = queuedCount > 0 || processingJobs.length > 0;

  // Get queue button text
  const getQueueButtonText = () => {
    if (processingJobs.length > 0) {
      const job = processingJobs[0];
      return `Marking ${job.progress}%`;
    }
    if (queuedCount > 0) {
      return `${queuedCount} queued`;
    }
    return '';
  };

  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <span className="text-2xl">🎯</span>
          <h1 className="text-xl font-bold text-gray-900">Kumon Marker</h1>
        </div>
        <div className="flex items-center gap-3">
          {/* Queue status button - only shown when jobs are active */}
          {hasActiveJobs && (
            <button
              onClick={onQueueClick}
              className="relative px-4 py-2 text-white rounded-lg transition-colors overflow-hidden bg-orange-500 hover:bg-orange-600"
            >
              {/* Progress fill animation */}
              {processingJobs.length > 0 && (
                <div
                  className="absolute inset-0 bg-orange-600 transition-all duration-300"
                  style={{ width: `${processingJobs[0].progress}%` }}
                />
              )}
              <span className="relative">{getQueueButtonText()}</span>
              <span className="absolute top-0 right-0 -mt-1 -mr-1 w-3 h-3">
                <span className="absolute inline-flex h-full w-full rounded-full bg-orange-400 opacity-75 animate-ping" />
                <span className="relative inline-flex rounded-full h-3 w-3 bg-orange-500" />
              </span>
            </button>
          )}
          {/* Google Drive button */}
          <button
            onClick={onGDriveClick}
            className="px-4 py-2 text-white rounded-lg transition-colors bg-blue-600 hover:bg-blue-700"
          >
            Google Drive
          </button>
          <button
            onClick={onSettingsClick}
            className="p-2 text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
            title="Settings"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
          </button>

          {/* User menu */}
          {user && (
            <div className="flex items-center gap-2 ml-2 pl-3 border-l border-gray-200">
              {user.picture ? (
                <img
                  src={user.picture}
                  alt={user.name || user.email}
                  className="w-8 h-8 rounded-full"
                />
              ) : (
                <div className="w-8 h-8 rounded-full bg-gray-300 flex items-center justify-center text-gray-600 text-sm font-medium">
                  {(user.name || user.email).charAt(0).toUpperCase()}
                </div>
              )}
              <div className="hidden sm:block">
                <p className="text-sm font-medium text-gray-900 truncate max-w-[120px]">
                  {user.name || user.email.split('@')[0]}
                </p>
              </div>
              <button
                onClick={onLogout}
                className="p-1.5 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded transition-colors"
                title="Sign out"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                </svg>
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
