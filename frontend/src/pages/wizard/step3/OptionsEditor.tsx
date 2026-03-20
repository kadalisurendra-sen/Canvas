import React, { useEffect, useState } from 'react';
import type { FieldOption } from '../../../types/template';
import { fetchCategories, fetchValues } from '../../../services/masterDataService';
import type { Category, MasterDataValue } from '../../../services/masterDataService';

interface OptionsEditorProps {
  options: FieldOption[];
  onChange: (options: FieldOption[]) => void;
  showScores?: boolean;
}

export function OptionsEditor({ options, onChange, showScores = true }: OptionsEditorProps) {
  const [showImport, setShowImport] = useState(false);

  const handleAdd = () => {
    const newOption: FieldOption = {
      label: '',
      value: '',
      score: 0,
      sort_order: options.length + 1,
    };
    onChange([...options, newOption]);
  };

  const handleUpdate = (idx: number, partial: Partial<FieldOption>) => {
    const updated = [...options];
    updated[idx] = { ...updated[idx], ...partial };
    onChange(updated);
  };

  const handleRemove = (idx: number) => {
    onChange(options.filter((_, i) => i !== idx));
  };

  const handleImport = (values: MasterDataValue[]) => {
    const imported: FieldOption[] = values.map((v, i) => ({
      label: v.label,
      value: v.value,
      score: 0,
      sort_order: options.length + i + 1,
    }));
    onChange([...options, ...imported]);
    setShowImport(false);
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h4 className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">
          Options &amp; Scoring
        </h4>
        <div className="flex items-center gap-3">
          <button
            onClick={() => setShowImport(true)}
            className="text-[11px] text-emerald-600 font-bold flex items-center gap-1 hover:opacity-80 transition-all"
          >
            <span className="material-symbols-outlined text-base">database</span>
            Import from Master Data
          </button>
          <button
            onClick={handleAdd}
            className="text-[11px] text-primary font-bold flex items-center gap-1 hover:opacity-80 transition-all"
          >
            <span className="material-symbols-outlined text-base">add</span>
            Add Option
          </button>
        </div>
      </div>

      <div className="border border-[#CFD0D6] rounded-lg overflow-hidden bg-white">
        <div className={`grid ${showScores ? 'grid-cols-[32px_1fr_80px_32px]' : 'grid-cols-[32px_1fr_32px]'} gap-2 px-3 py-2 bg-[#1E2345] text-white text-[10px] font-bold uppercase tracking-wider`}>
          <span />
          <span>Label</span>
          {showScores && <span className="text-center">Score</span>}
          <span />
        </div>
        <div className="divide-y divide-[#CFD0D6]">
          {options.map((opt, idx) => (
            <div
              key={idx}
              className={`grid ${showScores ? 'grid-cols-[32px_1fr_80px_32px]' : 'grid-cols-[32px_1fr_32px]'} gap-2 p-2 items-center ${
                idx % 2 === 0 ? 'bg-white' : 'bg-slate-50/50'
              }`}
            >
              <span className="material-symbols-outlined text-slate-300 text-base">
                drag_handle
              </span>
              <input
                className="border-[#CFD0D6] rounded text-xs px-2 py-1.5"
                type="text"
                value={opt.label}
                onChange={(e) => handleUpdate(idx, { label: e.target.value, value: e.target.value.toLowerCase().replace(/\s+/g, '_') })}
                placeholder="Option label"
              />
              {showScores && (
                <input
                  className="border-[#CFD0D6] rounded text-xs px-2 py-1.5 text-center"
                  type="number"
                  value={opt.score}
                  onChange={(e) => handleUpdate(idx, { score: Number(e.target.value) })}
                />
              )}
              <button
                onClick={() => handleRemove(idx)}
                className="text-slate-300 hover:text-red-500 transition-colors"
              >
                <span className="material-symbols-outlined text-sm">close</span>
              </button>
            </div>
          ))}
          {options.length === 0 && (
            <div className="p-4 text-center text-xs text-slate-400">
              No options yet. Click "Add Option" or "Import from Master Data".
            </div>
          )}
        </div>
      </div>

      {showImport && (
        <MasterDataImportModal
          onImport={handleImport}
          onClose={() => setShowImport(false)}
        />
      )}
    </div>
  );
}


interface MasterDataImportModalProps {
  onImport: (values: MasterDataValue[]) => void;
  onClose: () => void;
}

function MasterDataImportModal({ onImport, onClose }: MasterDataImportModalProps) {
  const [categories, setCategories] = useState<Category[]>([]);
  const [selectedCatId, setSelectedCatId] = useState('');
  const [values, setValues] = useState<MasterDataValue[]>([]);
  const [selectedValues, setSelectedValues] = useState<Set<string>>(new Set());
  const [loading, setLoading] = useState(true);
  const [loadingValues, setLoadingValues] = useState(false);

  useEffect(() => {
    fetchCategories()
      .then(setCategories)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    if (!selectedCatId) {
      setValues([]);
      setSelectedValues(new Set());
      return;
    }
    setLoadingValues(true);
    fetchValues(selectedCatId, '', 1, 100)
      .then((resp) => {
        setValues(resp.items);
        // Select all by default
        setSelectedValues(new Set(resp.items.map((v: MasterDataValue) => v.id)));
      })
      .catch(() => setValues([]))
      .finally(() => setLoadingValues(false));
  }, [selectedCatId]);

  const toggleValue = (id: string) => {
    const next = new Set(selectedValues);
    if (next.has(id)) next.delete(id);
    else next.add(id);
    setSelectedValues(next);
  };

  const toggleAll = () => {
    if (selectedValues.size === values.length) {
      setSelectedValues(new Set());
    } else {
      setSelectedValues(new Set(values.map((v) => v.id)));
    }
  };

  const handleImport = () => {
    const selected = values.filter((v) => selectedValues.has(v.id));
    onImport(selected);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
      <div className="bg-white rounded-2xl shadow-xl w-full max-w-lg mx-4 max-h-[80vh] flex flex-col">
        {/* Header */}
        <div className="px-6 py-4 border-b border-gray-100 flex items-center justify-between">
          <div>
            <h3 className="text-lg font-bold text-[#1E2345]">Import from Master Data</h3>
            <p className="text-xs text-[#7D8494] mt-0.5">Select a category and pick values to use as options</p>
          </div>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
            <span className="material-symbols-outlined">close</span>
          </button>
        </div>

        {/* Category selector */}
        <div className="px-6 py-4 border-b border-gray-100">
          <label className="block text-xs font-semibold text-slate-600 mb-2">Category</label>
          {loading ? (
            <span className="text-xs text-gray-400">Loading categories...</span>
          ) : (
            <select
              value={selectedCatId}
              onChange={(e) => setSelectedCatId(e.target.value)}
              className="w-full h-9 px-3 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary/50"
            >
              <option value="">Select a category...</option>
              {categories.map((cat) => (
                <option key={cat.id} value={cat.id}>
                  {cat.display_name} ({cat.item_count} items)
                </option>
              ))}
            </select>
          )}
        </div>

        {/* Values list */}
        <div className="flex-1 overflow-y-auto px-6 py-3">
          {loadingValues ? (
            <div className="text-center py-8 text-xs text-gray-400">Loading values...</div>
          ) : values.length === 0 && selectedCatId ? (
            <div className="text-center py-8 text-xs text-gray-400">No values in this category</div>
          ) : values.length > 0 ? (
            <>
              <div className="flex items-center gap-2 mb-3 pb-2 border-b border-gray-100">
                <input
                  type="checkbox"
                  checked={selectedValues.size === values.length && values.length > 0}
                  onChange={toggleAll}
                  className="w-4 h-4 rounded border-gray-300 text-primary focus:ring-primary"
                />
                <span className="text-xs font-semibold text-slate-600">
                  Select All ({selectedValues.size}/{values.length})
                </span>
              </div>
              {values.map((v) => (
                <label
                  key={v.id}
                  className="flex items-center gap-3 py-2 px-2 rounded hover:bg-gray-50 cursor-pointer"
                >
                  <input
                    type="checkbox"
                    checked={selectedValues.has(v.id)}
                    onChange={() => toggleValue(v.id)}
                    className="w-4 h-4 rounded border-gray-300 text-primary focus:ring-primary"
                  />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-slate-700 truncate">{v.label}</p>
                    {v.description && (
                      <p className="text-xs text-slate-400 truncate">{v.description}</p>
                    )}
                  </div>
                  {v.severity && (
                    <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full ${
                      v.severity === 'high' || v.severity === 'High'
                        ? 'bg-red-50 text-red-600'
                        : v.severity === 'medium' || v.severity === 'Medium'
                        ? 'bg-amber-50 text-amber-600'
                        : 'bg-green-50 text-green-600'
                    }`}>
                      {v.severity}
                    </span>
                  )}
                </label>
              ))}
            </>
          ) : (
            <div className="text-center py-8 text-xs text-gray-400">
              Select a category above to see available values
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-4 border-t border-gray-100 flex items-center justify-between">
          <span className="text-xs text-[#7D8494]">
            {selectedValues.size > 0 ? `${selectedValues.size} values selected` : 'No values selected'}
          </span>
          <div className="flex gap-3">
            <button
              onClick={onClose}
              className="px-4 py-2 text-sm font-semibold text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
            >
              Cancel
            </button>
            <button
              onClick={handleImport}
              disabled={selectedValues.size === 0}
              className="px-4 py-2 text-sm font-semibold text-white bg-primary hover:bg-primary/90 rounded-lg transition-colors disabled:opacity-50"
            >
              Import {selectedValues.size > 0 ? `(${selectedValues.size})` : ''}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
