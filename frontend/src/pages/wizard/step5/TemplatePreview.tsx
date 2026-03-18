import React, { useState } from 'react';
import type { TemplateStage } from '../../../types/template';

interface TemplatePreviewProps {
  stages: TemplateStage[];
}

export function TemplatePreview({ stages }: TemplatePreviewProps) {
  const [activeStage, setActiveStage] = useState(0);
  const [activeSection, setActiveSection] = useState(0);
  const stage = stages[activeStage];
  const sections = stage?.sections || [];
  const section = sections[activeSection];

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

        {/* Fields preview */}
        {section && (
          <div className="space-y-8">
            <div>
              <h3 className="text-xl font-bold mb-2">{section.name}</h3>
              <p className="text-sm text-[#6D7283]">
                Provide the foundational information for this evaluation.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              {section.fields.map((field, idx) => (
                <div
                  key={idx}
                  className={`space-y-2 ${
                    field.field_type === 'text_long' ? 'md:col-span-2' : ''
                  }`}
                >
                  <label className="text-xs font-bold uppercase text-[#6D7283]">
                    {field.label}
                  </label>
                  {field.field_type === 'text_long' ? (
                    <div className="w-full h-32 px-4 py-3 bg-slate-50 border border-slate-200 rounded-lg text-sm text-slate-700 italic">
                      Sample long text content...
                    </div>
                  ) : field.field_type === 'single_select' || field.field_type === 'multi_select' ? (
                    <div className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-lg text-sm text-slate-700 flex justify-between items-center">
                      {field.options[0]?.label || 'Select...'}
                      <span className="material-symbols-outlined text-sm">expand_more</span>
                    </div>
                  ) : (
                    <div className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-lg text-sm text-slate-700">
                      Sample value
                    </div>
                  )}
                </div>
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
      </div>
    </div>
  );
}
