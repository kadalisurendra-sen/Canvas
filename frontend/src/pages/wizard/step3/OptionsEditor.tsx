import React from 'react';
import type { FieldOption } from '../../../types/template';

interface OptionsEditorProps {
  options: FieldOption[];
  onChange: (options: FieldOption[]) => void;
}

export function OptionsEditor({ options, onChange }: OptionsEditorProps) {
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

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h4 className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">
          Options &amp; Scoring
        </h4>
        <button
          onClick={handleAdd}
          className="text-[11px] text-primary font-bold flex items-center gap-1 hover:opacity-80 transition-all"
        >
          <span className="material-symbols-outlined text-base">add</span>
          Add Option
        </button>
      </div>

      <div className="border border-[#CFD0D6] rounded-lg overflow-hidden bg-white">
        <div className="grid grid-cols-[32px_1fr_80px_32px] gap-2 px-3 py-2 bg-[#1E2345] text-white text-[10px] font-bold uppercase tracking-wider">
          <span />
          <span>Label</span>
          <span className="text-center">Score</span>
          <span />
        </div>
        <div className="divide-y divide-[#CFD0D6]">
          {options.map((opt, idx) => (
            <div
              key={idx}
              className={`grid grid-cols-[32px_1fr_80px_32px] gap-2 p-2 items-center ${
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
              <input
                className="border-[#CFD0D6] rounded text-xs px-2 py-1.5 text-center"
                type="number"
                value={opt.score}
                onChange={(e) => handleUpdate(idx, { score: Number(e.target.value) })}
              />
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
              No options yet. Click "Add Option" above.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
