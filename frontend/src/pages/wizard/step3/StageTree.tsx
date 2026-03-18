import React, { useState } from 'react';
import type { TemplateStage } from '../../../types/template';

interface StageTreeProps {
  stages: TemplateStage[];
  activeStageIdx: number;
  activeSectionIdx: number;
  onSelectStage: (idx: number) => void;
  onSelectSection: (stageIdx: number, sectionIdx: number) => void;
}

export function StageTree({
  stages, activeStageIdx, activeSectionIdx, onSelectStage, onSelectSection,
}: StageTreeProps) {
  const [expanded, setExpanded] = useState<Record<number, boolean>>({ 0: true });

  const toggleExpand = (idx: number) => {
    setExpanded((prev) => ({ ...prev, [idx]: !prev[idx] }));
    onSelectStage(idx);
  };

  return (
    <div className="flex-1 overflow-y-auto p-4">
      <div className="space-y-1">
        {stages.map((stage, stageIdx) => (
          <div key={stageIdx}>
            <div
              className={`flex items-center gap-2 py-2 cursor-pointer ${
                stageIdx === activeStageIdx ? 'text-[#1E2345] font-bold' : 'text-slate-400'
              }`}
              onClick={() => toggleExpand(stageIdx)}
            >
              <span className="material-symbols-outlined text-lg">
                {expanded[stageIdx] ? 'expand_more' : 'chevron_right'}
              </span>
              <span className="text-sm">{stageIdx + 1}. {stage.name}</span>
            </div>

            {expanded[stageIdx] && stage.sections && (
              <div className="ml-6 space-y-1 mt-1 border-l border-slate-100">
                {stage.sections.map((section, secIdx) => (
                  <div
                    key={secIdx}
                    onClick={() => onSelectSection(stageIdx, secIdx)}
                    className={`flex items-center gap-2 py-2 px-3 rounded-l-md cursor-pointer transition-colors ${
                      stageIdx === activeStageIdx && secIdx === activeSectionIdx
                        ? 'bg-primary/5 text-primary border-r-4 border-primary'
                        : 'text-slate-500 hover:bg-slate-50'
                    }`}
                  >
                    <span className={`text-xs ${
                      stageIdx === activeStageIdx && secIdx === activeSectionIdx
                        ? 'font-semibold' : 'font-medium'
                    }`}>
                      {section.name}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
