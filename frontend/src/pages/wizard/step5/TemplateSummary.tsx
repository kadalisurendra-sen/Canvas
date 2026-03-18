import React from 'react';

interface TemplateSummaryProps {
  stageCount: number;
  fieldCount: number;
  hasScoring: boolean;
}

export function TemplateSummary({ stageCount, fieldCount, hasScoring }: TemplateSummaryProps) {
  return (
    <div className="bg-[#F3F4F4] rounded-3xl p-8 sticky top-24">
      <h3 className="text-xl font-bold mb-6">Template Summary</h3>

      <div className="space-y-6">
        <div className="flex justify-between items-start border-b border-slate-200 pb-4">
          <div>
            <p className="text-sm font-bold text-slate-800">Stages Configured</p>
            <p className="text-xs text-[#6D7283] mt-1">Total evaluation stages</p>
          </div>
          <span className="text-lg font-bold text-primary">{stageCount}</span>
        </div>

        <div className="flex justify-between items-start border-b border-slate-200 pb-4">
          <div>
            <p className="text-sm font-bold text-slate-800">Total Fields</p>
            <p className="text-xs text-[#6D7283] mt-1">Across all stages</p>
          </div>
          <span className="text-lg font-bold text-primary">{fieldCount}</span>
        </div>

        <div className="flex justify-between items-start border-b border-slate-200 pb-4">
          <div>
            <p className="text-sm font-bold text-slate-800">Scoring Model</p>
            <p className="text-xs text-[#6D7283] mt-1">
              {hasScoring ? 'Weighted average' : 'No scoring'}
            </p>
          </div>
          <span className="text-sm font-bold text-primary bg-primary/10 px-2 py-1 rounded">
            {hasScoring ? 'Active' : 'Inactive'}
          </span>
        </div>

        <div className="pt-2">
          <p className="text-sm text-slate-600 italic">
            By publishing this template, it will become available for new project evaluations
            immediately. Existing drafts will not be affected.
          </p>
        </div>
      </div>
    </div>
  );
}
