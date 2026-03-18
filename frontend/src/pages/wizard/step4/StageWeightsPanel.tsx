import React from 'react';
import type { TemplateStage } from '../../../types/template';

interface StageWeightsPanelProps {
  stages: TemplateStage[];
  onWeightChange: (idx: number, weight: number) => void;
  totalWeight: number;
  weightValid: boolean;
}

const BAR_COLORS = ['#00A1FF', '#00D67D', '#5F2CFF', '#F97316', '#EC4899', '#14B8A6'];

export function StageWeightsPanel({
  stages, onWeightChange, totalWeight, weightValid,
}: StageWeightsPanelProps) {
  return (
    <div className="bg-[#F3F4F4] rounded-2xl shadow-sm border border-slate-200 overflow-hidden">
      <div className="p-8 pb-4">
        <h3 className="text-lg font-bold text-[#1E2345]">Stage Weights</h3>
        <p className="text-sm text-slate-500 mt-1">
          Define how each stage contributes to the final score.
        </p>
      </div>
      <div className="p-8 pt-0">
        <div className="grid grid-cols-1 md:grid-cols-[1fr_120px] gap-8 mt-6">
          <div className="space-y-6">
            {stages.map((stage, idx) => (
              <div key={idx} className="space-y-2">
                <div className="flex justify-between items-center text-sm font-semibold">
                  <span className="text-slate-700">{stage.name}</span>
                  <span className="text-primary bg-primary/10 px-2 py-0.5 rounded">
                    {stage.weight_pct}%
                  </span>
                </div>
                <input
                  className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-primary"
                  type="range"
                  min={0}
                  max={100}
                  value={stage.weight_pct}
                  onChange={(e) => onWeightChange(idx, Number(e.target.value))}
                />
              </div>
            ))}

            {!weightValid && (
              <p className="text-xs text-rose-500 font-medium">
                Weights must sum to 100% (currently {totalWeight}%)
              </p>
            )}
          </div>

          <div className="flex flex-col items-center justify-center gap-2">
            <div className="h-40 w-12 bg-slate-200 rounded-lg overflow-hidden flex flex-col-reverse">
              {stages.map((stage, idx) => (
                <div
                  key={idx}
                  style={{
                    height: `${stage.weight_pct}%`,
                    backgroundColor: BAR_COLORS[idx % BAR_COLORS.length],
                  }}
                  title={stage.name}
                />
              ))}
            </div>
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">
              Distribution
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
