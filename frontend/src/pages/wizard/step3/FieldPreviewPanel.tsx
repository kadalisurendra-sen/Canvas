import React from 'react';
import type { TemplateField, TemplateSection } from '../../../types/template';

interface FieldPreviewPanelProps {
  section: TemplateSection | undefined;
}

export function FieldPreviewPanel({ section }: FieldPreviewPanelProps) {
  return (
    <div className="flex-1 bg-white rounded-lg shadow-sm border border-[#CFD0D6] overflow-hidden flex flex-col">
      <div className="p-5 border-b border-[#CFD0D6] bg-slate-50/30">
        <h4 className="text-base font-bold text-[#1E2345]">
          {section?.name || 'Preview'}
        </h4>
        <p className="text-[10px] text-slate-400 mt-1">
          Real-time preview of the current section form
        </p>
      </div>

      <div className="flex-1 overflow-y-auto p-5 space-y-5">
        {(!section || section.fields.length === 0) && (
          <div className="flex flex-col items-center justify-center py-8 text-slate-300">
            <span className="material-symbols-outlined text-3xl mb-2">preview</span>
            <p className="text-xs font-medium">
              Add fields to see a preview here
            </p>
          </div>
        )}

        {section?.fields.map((field, idx) => (
          <FieldPreview key={idx} field={field} />
        ))}
      </div>

      {section && section.fields.length > 0 && (
        <div className="px-5 py-3 border-t border-[#CFD0D6] bg-slate-50/30">
          <span className="text-[10px] text-slate-400">
            {section.fields.length} field{section.fields.length !== 1 ? 's' : ''} &bull;{' '}
            {section.fields.filter(f => f.is_mandatory).length} mandatory &bull;{' '}
            {section.fields.filter(f => f.is_scoring).length} scoring
          </span>
        </div>
      )}
    </div>
  );
}

function FieldPreview({ field }: { field: TemplateField }) {
  return (
    <div className="pb-4 border-b border-slate-100 last:border-b-0 last:pb-0">
      <label className="block text-[11px] font-bold text-slate-700 mb-1.5">
        {field.label || 'Untitled Field'}
        {field.is_mandatory && <span className="text-red-500 ml-0.5">*</span>}
        {field.is_scoring && (
          <span className="ml-2 text-[9px] font-semibold text-primary bg-primary/10 px-1.5 py-0.5 rounded">
            SCORED
          </span>
        )}
      </label>

      {field.help_text && (
        <p className="text-[10px] text-slate-400 mb-1.5">{field.help_text}</p>
      )}

      {field.field_type === 'text_short' && (
        <input
          className="w-full border border-[#CFD0D6] rounded text-xs p-2 bg-slate-50"
          placeholder={`Enter ${field.label.toLowerCase() || 'value'}...`}
          type="text"
          readOnly
        />
      )}

      {field.field_type === 'text_long' && (
        <textarea
          className="w-full border border-[#CFD0D6] rounded text-xs p-2 bg-slate-50"
          placeholder={`Describe ${field.label.toLowerCase() || 'value'}...`}
          rows={2}
          readOnly
        />
      )}

      {field.field_type === 'single_select' && (
        <div className="space-y-1.5">
          {field.options.length > 0 ? (
            field.options.map((opt, i) => (
              <label key={i} className="flex items-center gap-2 py-1 px-2 rounded hover:bg-slate-50 cursor-pointer">
                <div className="w-3.5 h-3.5 rounded-full border-2 border-slate-300 flex-shrink-0" />
                <span className="text-xs text-slate-700">{opt.label || 'Option'}</span>
                {field.is_scoring && opt.score > 0 && (
                  <span className="text-[9px] text-primary font-semibold ml-auto">{opt.score} pts</span>
                )}
              </label>
            ))
          ) : (
            <div className="border border-[#CFD0D6] rounded p-2 text-xs text-slate-400 bg-slate-50 flex items-center justify-between">
              <span>Select {field.label || 'option'}...</span>
              <span className="material-symbols-outlined text-sm">arrow_drop_down</span>
            </div>
          )}
        </div>
      )}

      {field.field_type === 'multi_select' && (
        <div className="space-y-1.5">
          {field.options.length > 0 ? (
            field.options.map((opt, i) => (
              <label key={i} className="flex items-center gap-2 py-1 px-2 rounded hover:bg-slate-50 cursor-pointer">
                <div className="w-3.5 h-3.5 rounded border-2 border-slate-300 flex-shrink-0" />
                <span className="text-xs text-slate-700">{opt.label || 'Option'}</span>
                {field.is_scoring && opt.score > 0 && (
                  <span className="text-[9px] text-primary font-semibold ml-auto">{opt.score} pts</span>
                )}
              </label>
            ))
          ) : (
            <div className="border border-[#CFD0D6] rounded p-2 text-xs text-slate-400 bg-slate-50 flex items-center justify-between">
              <span>Select {field.label || 'options'}...</span>
              <span className="material-symbols-outlined text-sm">arrow_drop_down</span>
            </div>
          )}
        </div>
      )}

      {field.field_type === 'number' && (
        <input
          className="w-full border border-[#CFD0D6] rounded text-xs p-2 bg-slate-50"
          placeholder="0"
          type="number"
          readOnly
        />
      )}

      {field.field_type === 'date' && (
        <input
          className="w-full border border-[#CFD0D6] rounded text-xs p-2 bg-slate-50"
          type="date"
          readOnly
        />
      )}
    </div>
  );
}
