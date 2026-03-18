import React from 'react';
import type { TemplateSection } from '../../../types/template';

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
          <p className="text-xs text-slate-400 italic">
            Add fields to see a preview here.
          </p>
        )}

        {section?.fields.map((field, idx) => (
          <div key={idx}>
            <label className="block text-[11px] font-bold text-slate-700 mb-1.5">
              {field.label || 'Untitled'}
              {field.is_mandatory && <span className="text-red-500"> *</span>}
            </label>

            {field.field_type === 'text_short' && (
              <input
                className="w-full border-[#CFD0D6] rounded text-xs p-2.5 focus:ring-primary focus:border-primary"
                placeholder={`Enter ${field.label.toLowerCase() || 'value'}`}
                type="text"
                readOnly
              />
            )}

            {field.field_type === 'text_long' && (
              <textarea
                className="w-full border-[#CFD0D6] rounded text-xs p-2.5 focus:ring-primary focus:border-primary"
                placeholder={`Describe ${field.label.toLowerCase() || 'value'}`}
                rows={3}
                readOnly
              />
            )}

            {(field.field_type === 'single_select' || field.field_type === 'multi_select') && (
              <>
                <div className="w-full border-2 border-primary bg-white rounded p-2.5 text-xs flex items-center justify-between cursor-pointer">
                  <span className="text-slate-800 font-medium">
                    Select {field.label || 'option'}...
                  </span>
                  <span className="material-symbols-outlined text-primary">arrow_drop_down</span>
                </div>
                {field.help_text && (
                  <p className="text-[10px] text-slate-400 mt-1">{field.help_text}</p>
                )}
              </>
            )}

            {field.field_type === 'number' && (
              <input
                className="w-full border-[#CFD0D6] rounded text-xs p-2.5 focus:ring-primary focus:border-primary"
                placeholder="0"
                type="number"
                readOnly
              />
            )}

            {field.field_type === 'date' && (
              <input
                className="w-full border-[#CFD0D6] rounded text-xs p-2.5 focus:ring-primary focus:border-primary"
                type="date"
                readOnly
              />
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
