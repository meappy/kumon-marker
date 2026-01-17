import { useCallback, useState } from 'react';

interface UploaderProps {
  onUpload: (file: File) => Promise<void>;
}

export function Uploader({ onUpload }: UploaderProps) {
  const [dragging, setDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleDrop = useCallback(
    async (e: React.DragEvent) => {
      e.preventDefault();
      setDragging(false);
      setError(null);

      const file = e.dataTransfer.files[0];
      if (!file || !file.name.endsWith('.pdf')) {
        setError('Please drop a PDF file');
        return;
      }

      setUploading(true);
      try {
        await onUpload(file);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Upload failed');
      } finally {
        setUploading(false);
      }
    },
    [onUpload]
  );

  const handleFileSelect = useCallback(
    async (e: React.ChangeEvent<HTMLInputElement>) => {
      setError(null);
      const file = e.target.files?.[0];
      if (!file) return;

      setUploading(true);
      try {
        await onUpload(file);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Upload failed');
      } finally {
        setUploading(false);
      }
    },
    [onUpload]
  );

  return (
    <div
      onDragOver={(e) => {
        e.preventDefault();
        setDragging(true);
      }}
      onDragLeave={() => setDragging(false)}
      onDrop={handleDrop}
      className={`
        border-2 border-dashed rounded-xl p-8 text-center cursor-pointer
        transition-colors
        ${dragging ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-gray-400'}
        ${uploading ? 'opacity-50 cursor-not-allowed' : ''}
      `}
    >
      <input
        type="file"
        accept=".pdf"
        onChange={handleFileSelect}
        disabled={uploading}
        className="hidden"
        id="file-input"
      />
      <label htmlFor="file-input" className="cursor-pointer">
        <div className="text-4xl mb-2">📤</div>
        <p className="text-gray-600">
          {uploading ? 'Uploading...' : 'Drop PDF here or click to upload'}
        </p>
      </label>
      {error && <p className="mt-2 text-red-600 text-sm">{error}</p>}
    </div>
  );
}
