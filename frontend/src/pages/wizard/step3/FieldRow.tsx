import React, { useState } from 'react';
import { OptionsEditor } from './OptionsEditor';
import type { FieldType, TemplateField } from '../../../types/template';

interface FieldRowProps {
  field: TemplateField;
  onUpdate: (field: TemplateField) => void;
  onRemove: () => void;
}

const FIELD_TYPES: { value: FieldType; label: string }[] = [
  { value: 'text_short', label: 'Text (Short)' },
  { value: 'text_long', label: 'Text (Long)' },
  { value: 'single_select', label: 'Single Select' },
  { value: 'multi_select', label: 'Multi Select' },
  { value: 'number', label: 'Number' },
  { value: 'date', label: 'Date' },
];

export function FieldRow({ field, onUpdate, onRemove }: FieldRowProps) {
  const [expanded, setExpanded] = useState(false);
  const isSelectType = field.field_type === 'single_select' || field.field_type === 'multi_select';

  return (
    <div className={`bg-white overflow-hidden ${
      expanded
        ? 'border-2 border-primary rounded-xl shadow-lg shadow-primary/5'
        : 'border border-[#CFD0D6] rounded-lg shadow-sm'
    }`}>
      {/* Header */}
      <div
        className="px-5 py-4 border-b border-[#CFD0D6] flex items-center justify-between bg-white cursor-pointer"
        onClick={() => setExpanded(!expanded)}
      >
        <div className="flex items-center gap-4">
          <span className="material-symbols-outlined text-slate-300">drag_indicator</span>
          <div className="flex items-center gap-2">
            <span className="text-sm font-bold text-[#1E2345]">
              {field.label || 'Untitled Field'}
            </span>
            <span className={`text-[9px] px-1.5 py-0.5 rounded font-bold uppercase ${
              expanded ? 'bg-primary/10 text-primary' : 'bg-slate-100 text-slate-500'
            }`}>
              {field.field_type}
            </span>
          </div>
        </div>
        <div className="flex items-center gap-2">
          {expanded && (
            <button
              onClick={(e) => { e.stopPropagation(); onRemove(); }}
              className="w-8 h-8 text-slate-400 hover:text-red-500 transition-colors"
            >
              <span className="material-symbols-outlined text-xl">delete</span>
            </button>
          )}
          <button className="w-8 h-8 text-[#1E2345]">
            <span className="material-symbols-outlined text-xl">
              {expanded ? 'expand_less' : 'expand_more'}
            </span>
          </button>
        </div>
      </div>

      {/* Expanded editor */}
      {expanded && (
        <div className="p-6 space-y-6">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-[10px] font-bold text-slate-500 uppercase mb-1.5 tracking-wider">
                Field Key
              </label>
              <input
                className="w-full border-[#CFD0D6] rounded text-sm px-3 py-2 bg-slate-50 focus:ring-1 focus:ring-primary focus:border-primary"
                type="text"
                value={field.field_key}
                onChange={(e) => onUpdate({ ...field, field_key: e.target.value })}
              />
            </div>
            <div>
              <label className="block text-[10px] font-bold text-slate-500 uppercase mb-1.5 tracking-wider">
                Label
              </label>
              <input
                className="w-full border-[#CFD0D6] rounded text-sm px-3 py-2 bg-white focus:ring-1 focus:ring-primary focus:border-primary"
                type="text"
                value={field.label}
                onChange={(e) => onUpdate({ ...field, label: e.target.value })}
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-[10px] font-bold text-slate-500 uppercase mb-1.5 tracking-wider">
                Field Type
              </label>
              <select
                className="w-full border-[#CFD0D6] rounded text-sm px-3 py-2 focus:ring-1 focus:ring-primary focus:border-primary"
                value={field.field_type}
                onChange={(e) => onUpdate({ ...field, field_type: e.target.value as FieldType })}
              >
                {FIELD_TYPES.map((ft) => (
                  <option key={ft.value} value={ft.value}>{ft.label}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-[10px] font-bold text-slate-500 uppercase mb-1.5 tracking-wider">
                Help Text
              </label>
              <input
                className="w-full border-[#CFD0D6] rounded text-sm px-3 py-2 focus:ring-1 focus:ring-primary focus:border-primary"
                placeholder="Explain context of the field..."
                type="text"
                value={field.help_text || ''}
                onChange={(e) => onUpdate({ ...field, help_text: e.target.value })}
              />
            </div>
          </div>

          <div className="flex gap-8 py-4 border-y border-slate-100">
            <div className="flex items-center gap-3">
              <span className="text-xs font-semibold text-slate-700">Mandatory</span>
              <button
                onClick={() => onUpdate({ ...field, is_mandatory: !field.is_mandatory })}
                className={`w-9 h-5 rounded-full relative cursor-pointer transition-colors ${
                  field.is_mandatory ? 'bg-primary' : 'bg-slate-300'
                }`}
              >
                <div className={`absolute top-0.5 w-4 h-4 bg-white rounded-full transition-all ${
                  field.is_mandatory ? 'right-0.5' : 'left-0.5'
                }`} />
              </button>
            </div>
            <div className="flex items-center gap-3">
              <span className="text-xs font-semibold text-slate-700">Scoring</span>
              <button
                onClick={() => onUpdate({ ...field, is_scoring: !field.is_scoring })}
                className={`w-9 h-5 rounded-full relative cursor-pointer transition-colors ${
                  field.is_scoring ? 'bg-primary' : 'bg-slate-300'
                }`}
              >
                <div className={`absolute top-0.5 w-4 h-4 bg-white rounded-full transition-all ${
                  field.is_scoring ? 'right-0.5' : 'left-0.5'
                }`} />
              </button>
            </div>
          </div>

          {isSelectType && (
            <OptionsEditor
              options={field.options}
              onChange={(options) => onUpdate({ ...field, options })}
              showScores={field.is_scoring}
            />
          )}

          {!isSelectType && field.is_scoring && (
            <div className="pt-4">
              <h4 className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-3">
                Score Value
              </h4>
              <div className="flex items-center gap-3">
                <span className="text-xs text-slate-600">
                  Points awarded when this field is completed:
                </span>
                <input
                  className="w-20 border-[#CFD0D6] rounded text-xs px-2 py-1.5 text-center"
                  type="number"
                  min={0}
                  value={field.options[0]?.score || 0}
                  onChange={(e) => {
                    const score = Number(e.target.value);
                    onUpdate({
                      ...field,
                      options: [{
                        label: field.label,
                        value: field.field_key || 'score',
                        score,
                        sort_order: 1,
                      }],
                    });
                  }}
                />
                <span className="text-xs text-slate-400">pts</span>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
