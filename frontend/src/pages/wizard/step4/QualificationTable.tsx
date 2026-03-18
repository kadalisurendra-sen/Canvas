import React from 'react';
import type { FailAction, TemplateStage } from '../../../types/template';

interface QualificationTableProps {
  stages: TemplateStage[];
  onScoreChange: (idx: number, score: number | null) => void;
  onFailActionChange: (idx: number, action: FailAction) => void;
}

export function QualificationTable({
  stages, onScoreChange, onFailActionChange,
}: QualificationTableProps) {
  return (
    <div className="bg-[#F3F4F4] rounded-2xl shadow-sm border border-slate-200 overflow-hidden">
      <div className="p-8 pb-4">
        <h3 className="text-lg font-bold text-[#1E2345]">Qualification Thresholds</h3>
        <p className="text-sm text-slate-500 mt-1">
          Set conditions for progressing through stages.
        </p>
      </div>
      <div className="p-8 pt-0 overflow-x-auto">
        <table className="w-full text-base text-left font-normal mt-4">
          <thead className="bg-[#1E2345] text-white font-medium">
            <tr>
              <th className="py-3 px-4 rounded-tl-lg">Stage Name</th>
              <th className="py-3 px-4">Min. Score to Pass</th>
              <th className="py-3 px-4 rounded-tr-lg">Action on Fail</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-200">
            {stages.map((stage, idx) => (
              <tr key={idx}>
                <td className="py-4 px-4 font-normal text-slate-700">{stage.name}</td>
                <td className="py-4 px-4">
                  <input
                    className="w-20 rounded border-slate-300 focus:ring-primary focus:border-primary text-base"
                    type="number"
                    min={0}
                    max={100}
                    value={stage.min_pass_score ?? ''}
                    onChange={(e) => {
                      const val = e.target.value === '' ? null : Number(e.target.value);
                      onScoreChange(idx, val);
                    }}
                  />
                </td>
                <td className="py-4 px-4">
                  <select
                    className="rounded border-slate-300 text-base focus:ring-primary focus:border-primary w-full"
                    value={stage.fail_action}
                    onChange={(e) => onFailActionChange(idx, e.target.value as FailAction)}
                  >
                    <option value="warn">Warn</option>
                    <option value="block">Block</option>
                    <option value="allow">Allow</option>
                  </select>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
