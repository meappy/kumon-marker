import { useEffect, useState } from 'react';
import { api } from '../api/client';
import type { ShareEntry } from '../api/client';

interface SharingModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export function SharingModal({ isOpen, onClose }: SharingModalProps) {
  const [shares, setShares] = useState<ShareEntry[]>([]);
  const [email, setEmail] = useState('');
  const [permission, setPermission] = useState('read');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen) {
      loadShares();
    }
  }, [isOpen]);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) onClose();
    };
    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  const loadShares = async () => {
    try {
      const data = await api.getShares();
      setShares(data);
    } catch {
      // Ignore load errors
    }
  };

  const handleAdd = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email.trim()) return;

    setLoading(true);
    setError(null);
    try {
      await api.addShare(email.trim(), permission);
      setEmail('');
      await loadShares();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to add share');
    } finally {
      setLoading(false);
    }
  };

  const handleRemove = async (shareEmail: string) => {
    try {
      await api.removeShare(shareEmail);
      await loadShares();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to remove share');
    }
  };

  const handleUpdatePermission = async (shareEmail: string, newPermission: string) => {
    try {
      await api.addShare(shareEmail, newPermission);
      await loadShares();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update permission');
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white rounded-xl shadow-xl w-full max-w-md mx-4 max-h-[80vh] flex flex-col">
        <div className="flex items-center justify-between p-4 border-b">
          <h2 className="text-lg font-semibold">Sharing</h2>
          <button onClick={onClose} className="text-gray-500 hover:text-gray-700 text-xl">
            &times;
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {/* Add share form */}
          <form onSubmit={handleAdd} className="space-y-2">
            <div className="flex gap-2">
              <input
                type="email"
                placeholder="Email address"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="flex-1 px-3 py-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <select
                value={permission}
                onChange={(e) => setPermission(e.target.value)}
                className="px-2 py-2 text-sm border border-gray-300 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="read">View</option>
                <option value="readwrite">Edit</option>
              </select>
              <button
                type="submit"
                disabled={loading || !email.trim()}
                className="px-4 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 disabled:opacity-50 whitespace-nowrap"
              >
                Share
              </button>
            </div>
            {error && <p className="text-sm text-red-600">{error}</p>}
          </form>

          {/* Current shares */}
          {shares.length === 0 ? (
            <p className="text-sm text-gray-500 text-center py-4">
              Not shared with anyone yet
            </p>
          ) : (
            <div className="space-y-2">
              {shares.map((share) => (
                <div
                  key={share.id}
                  className="flex items-center justify-between py-2 px-3 bg-gray-50 rounded-lg"
                >
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900 truncate">
                      {share.shared_with_email}
                    </p>
                  </div>
                  <div className="flex items-center gap-2 ml-2">
                    <select
                      value={share.permission}
                      onChange={(e) => handleUpdatePermission(share.shared_with_email, e.target.value)}
                      className="px-2 py-1 text-xs border border-gray-300 rounded bg-white"
                    >
                      <option value="read">View</option>
                      <option value="readwrite">Edit</option>
                    </select>
                    <button
                      onClick={() => handleRemove(share.shared_with_email)}
                      className="p-1 text-gray-400 hover:text-red-600 transition-colors"
                      title="Remove"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
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
