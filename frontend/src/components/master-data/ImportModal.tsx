import React, { useCallback, useRef, useState } from 'react';
import type { ImportResult } from '../../services/masterDataService';

interface ImportModalProps {
  onImport: (file: File) => Promise<ImportResult>;
  onClose: () => void;
}

export function ImportModal({ onImport, onClose }: ImportModalProps) {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string[][]>([]);
  const [result, setResult] = useState<ImportResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const inputRef = useRef<HTMLInputElement>(null);

  const handleFile = useCallback((f: File) => {
    if (!f.name.endsWith('.csv')) {
      setError('Only .csv files accepted');
      return;
    }
    setFile(f);
    setError('');
    const reader = new FileReader();
    reader.onload = (e) => {
      const text = e.target?.result as string;
      const lines = text.split('\n').filter((l) => l.trim());
      if (lines.length > 1001) {
        setError('Maximum 1000 rows allowed');
        setFile(null);
        return;
      }
      const rows = lines.slice(0, 6).map((l) => l.split(',').map((c) => c.trim()));
      setPreview(rows);
    };
    reader.readAsText(f);
  }, []);

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    const f = e.dataTransfer.files[0];
    if (f) handleFile(f);
  };

  const handleSubmit = async () => {
    if (!file) return;
    setLoading(true);
    try {
      const res = await onImport(file);
      setResult(res);
    } catch {
      setError('Import failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white rounded-xl shadow-xl w-full max-w-2xl mx-4 max-h-[80vh] flex flex-col">
        <div className="flex items-center justify-between p-6 border-b border-[#E7E8EB]">
          <h3 className="text-lg font-bold text-slate-800">Import from CSV</h3>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-600">
            <span className="material-symbols-outlined">close</span>
          </button>
        </div>
        <div className="p-6 flex-1 overflow-y-auto space-y-4">
          {!result ? (
            <>
              <div
                onDrop={handleDrop}
                onDragOver={(e) => e.preventDefault()}
                onClick={() => inputRef.current?.click()}
                className="border-2 border-dashed border-[#E7E8EB] rounded-lg p-8 text-center cursor-pointer hover:border-[#5F2CFF]/30 transition-colors"
              >
                <span className="material-symbols-outlined text-4xl text-slate-300 mb-2">upload_file</span>
                <p className="text-sm text-slate-500">{file ? file.name : 'Drag & drop a CSV file or click to browse'}</p>
                <input
                  ref={inputRef}
                  type="file"
                  accept=".csv"
                  className="hidden"
                  onChange={(e) => e.target.files?.[0] && handleFile(e.target.files[0])}
                />
              </div>
              {error && <p className="text-sm text-red-500">{error}</p>}
              {preview.length > 0 && (
                <div className="overflow-x-auto border border-[#E7E8EB] rounded-lg">
                  <table className="w-full text-sm">
                    <thead><tr className="bg-slate-50">
                      {preview[0].map((h, i) => <th key={i} className="px-3 py-2 text-left font-semibold text-slate-600">{h}</th>)}
                    </tr></thead>
                    <tbody>
                      {preview.slice(1).map((row, ri) => (
                        <tr key={ri} className="border-t border-[#E7E8EB]">
                          {row.map((c, ci) => <td key={ci} className="px-3 py-2 text-slate-700">{c}</td>)}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </>
          ) : (
            <div className="space-y-3">
              <p className="text-sm"><span className="font-semibold text-green-600">{result.imported}</span> rows imported</p>
              <p className="text-sm"><span className="font-semibold text-yellow-600">{result.skipped}</span> rows skipped (duplicates)</p>
              {result.errors.length > 0 && (
                <div>
                  <p className="text-sm font-semibold text-red-600 mb-1">{result.errors.length} errors:</p>
                  <ul className="text-xs text-red-500 space-y-1">
                    {result.errors.map((err, i) => <li key={i}>Row {err.row}: {err.message}</li>)}
                  </ul>
                </div>
              )}
            </div>
          )}
        </div>
        <div className="flex justify-end gap-3 p-6 border-t border-[#E7E8EB]">
          <button onClick={onClose} className="px-4 py-2 border border-slate-300 text-slate-700 font-semibold rounded-[8px] text-sm hover:bg-slate-50">
            {result ? 'Close' : 'Cancel'}
          </button>
          {!result && (
            <button
              onClick={handleSubmit}
              disabled={!file || loading}
              className="px-4 py-2 bg-[#5F2CFF] text-white font-semibold rounded-[8px] text-sm hover:bg-[#5F2CFF]/90 disabled:opacity-50"
            >
              {loading ? 'Importing...' : 'Import'}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
