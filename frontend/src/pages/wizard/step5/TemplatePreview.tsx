import React, { useState } from 'react';
import type { TemplateField, TemplateStage } from '../../../types/template';

interface TemplatePreviewProps {
  stages: TemplateStage[];
}

export function TemplatePreview({ stages }: TemplatePreviewProps) {
  const [activeStage, setActiveStage] = useState(0);
  const [activeSection, setActiveSection] = useState(0);
  const stage = stages[activeStage];
  const sections = stage?.sections || [];
  const section = sections[activeSection];

  const totalFields = sections.reduce((sum, s) => sum + s.fields.length, 0);

  return (
    <div className="bg-[#F3F4F4] rounded-3xl overflow-hidden flex flex-col min-h-[600px]">
      {/* Stage tabs */}
      <div className="bg-white/50 border-b border-slate-200 px-6 pt-6">
        <div className="flex gap-4 overflow-x-auto pb-px">
          {stages.map((s, idx) => (
            <button
              key={idx}
              onClick={() => { setActiveStage(idx); setActiveSection(0); }}
              className={`px-4 py-2 text-sm font-medium whitespace-nowrap ${
                idx === activeStage
                  ? 'bg-white border-x border-t border-slate-200 rounded-t-lg font-bold text-primary'
                  : 'text-[#6D7283]'
              }`}
            >
              {s.name}
              {s.weight_pct > 0 && (
                <span className="ml-1 text-[10px] text-slate-400">({s.weight_pct}%)</span>
              )}
            </button>
          ))}
        </div>
      </div>

      {/* Section tabs */}
      <div className="p-8 flex-1 bg-white">
        {sections.length > 0 && (
          <div className="flex items-center gap-6 border-b border-slate-200 mb-8">
            {sections.map((sec, idx) => (
              <button
                key={idx}
                onClick={() => setActiveSection(idx)}
                className={`px-1 py-3 border-b-2 text-sm font-semibold tracking-wide transition-colors ${
                  idx === activeSection
                    ? 'border-primary font-bold text-primary'
                    : 'border-transparent text-slate-400 hover:text-slate-600'
                }`}
              >
                {sec.name.toUpperCase()}
              </button>
            ))}
          </div>
        )}

        {/* Progress indicator */}
        {sections.length > 0 && (
          <div className="flex items-center gap-4 mb-10">
            {sections.map((_, idx) => (
              <div
                key={idx}
                className={`h-2 flex-1 rounded-full ${
                  idx <= activeSection ? 'bg-primary' : 'bg-slate-100'
                }`}
              />
            ))}
          </div>
        )}

        {/* Fields preview */}
        {section && (
          <div className="space-y-8">
            <div>
              <h3 className="text-xl font-bold mb-2">{section.name}</h3>
              <p className="text-sm text-[#6D7283]">
                {section.fields.length} field{section.fields.length !== 1 ? 's' : ''} in this section
                {section.fields.filter(f => f.is_mandatory).length > 0 &&
                  ` (${section.fields.filter(f => f.is_mandatory).length} required)`}
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              {section.fields.map((field, idx) => (
                <FieldPreviewItem key={idx} field={field} />
              ))}
            </div>
          </div>
        )}

        {(!section || sections.length === 0) && (
          <div className="text-center text-slate-400 py-12">
            <span className="material-symbols-outlined text-4xl mb-2 block">preview</span>
            <p className="text-sm">No sections or fields configured for this stage.</p>
          </div>
        )}

        {/* Stage summary footer */}
        {stage && (
          <div className="mt-8 pt-6 border-t border-slate-100 flex items-center justify-between text-xs text-slate-400">
            <span>{sections.length} section{sections.length !== 1 ? 's' : ''} &bull; {totalFields} field{totalFields !== 1 ? 's' : ''}</span>
            {stage.weight_pct > 0 && <span>Weight: {stage.weight_pct}%</span>}
          </div>
        )}
      </div>
    </div>
  );
}

function FieldPreviewItem({ field }: { field: TemplateField }) {
  const isFullWidth = field.field_type === 'text_long';

  return (
    <div className={`space-y-2 ${isFullWidth ? 'md:col-span-2' : ''}`}>
      <label className="text-xs font-bold uppercase text-[#6D7283] flex items-center gap-1">
        {field.label || 'Untitled Field'}
        {field.is_mandatory && <span className="text-red-500">*</span>}
        {field.is_scoring && (
          <span className="text-[9px] font-semibold text-primary bg-primary/10 px-1.5 py-0.5 rounded ml-1 normal-case">
            Scored
          </span>
        )}
      </label>

      {field.help_text && (
        <p className="text-[11px] text-slate-400">{field.help_text}</p>
      )}

      {field.field_type === 'text_short' && (
        <input
          className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-lg text-sm"
          placeholder={`Enter ${field.label.toLowerCase()}...`}
          readOnly
        />
      )}

      {field.field_type === 'text_long' && (
        <textarea
          className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-lg text-sm resize-none"
          placeholder={`Describe ${field.label.toLowerCase()}...`}
          rows={3}
          readOnly
        />
      )}

      {field.field_type === 'number' && (
        <input
          className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-lg text-sm"
          type="number"
          placeholder="0"
          readOnly
        />
      )}

      {field.field_type === 'date' && (
        <input
          className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-lg text-sm"
          type="date"
          readOnly
        />
      )}

      {field.field_type === 'single_select' && (
        <div className="space-y-1.5">
          {field.options.length > 0 ? (
            field.options.map((opt, i) => (
              <label key={i} className="flex items-center gap-3 py-2 px-3 bg-slate-50 border border-slate-200 rounded-lg cursor-pointer hover:bg-slate-100">
                <div className="w-4 h-4 rounded-full border-2 border-slate-300 flex-shrink-0" />
                <span className="text-sm text-slate-700 flex-1">{opt.label}</span>
                {field.is_scoring && Number(opt.score) > 0 && (
                  <span className="text-[10px] text-primary font-semibold">{opt.score} pts</span>
                )}
              </label>
            ))
          ) : (
            <div className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-lg text-sm text-slate-400 flex justify-between">
              <span>Select...</span>
              <span className="material-symbols-outlined text-sm">expand_more</span>
            </div>
          )}
        </div>
      )}

      {field.field_type === 'multi_select' && (
        <div className="space-y-1.5">
          {field.options.length > 0 ? (
            field.options.map((opt, i) => (
              <label key={i} className="flex items-center gap-3 py-2 px-3 bg-slate-50 border border-slate-200 rounded-lg cursor-pointer hover:bg-slate-100">
                <div className="w-4 h-4 rounded border-2 border-slate-300 flex-shrink-0" />
                <span className="text-sm text-slate-700 flex-1">{opt.label}</span>
                {field.is_scoring && Number(opt.score) > 0 && (
                  <span className="text-[10px] text-primary font-semibold">{opt.score} pts</span>
                )}
              </label>
            ))
          ) : (
            <div className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-lg text-sm text-slate-400 flex justify-between">
              <span>Select options...</span>
              <span className="material-symbols-outlined text-sm">expand_more</span>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
