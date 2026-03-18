import React from 'react';

interface StageRowProps {
  index: number;
  name: string;
  onNameChange: (name: string) => void;
  onRemove: () => void;
  onMoveUp: () => void;
  onMoveDown: () => void;
}

const STAGE_COLORS = ['#0df2f2', '#a855f7', '#94a3b8', '#f97316', '#22c55e', '#ec4899'];

export function StageRow({
  index, name, onNameChange, onRemove, onMoveUp, onMoveDown,
}: StageRowProps) {
  const color = STAGE_COLORS[index % STAGE_COLORS.length];

  return (
    <div className="p-4 bg-[#F3F4F4] rounded-lg flex items-center gap-4 group border border-[#E7E8EB]">
      <span
        className="material-symbols-outlined text-slate-400 cursor-grab active:cursor-grabbing hover:text-[#151C28]"
        onDoubleClick={onMoveUp}
      >
        drag_indicator
      </span>

      <div className="w-8 h-8 rounded bg-white border border-[#E7E8EB] flex items-center justify-center text-xs font-bold text-[#151C28]">
        {index + 1}
      </div>

      <div className="flex-1">
        <input
          className="w-full border-none focus:ring-0 text-sm font-semibold text-[#151C28] p-0 bg-transparent"
          type="text"
          value={name}
          onChange={(e) => onNameChange(e.target.value)}
          placeholder="Enter stage name..."
        />
      </div>

      <div className="flex items-center gap-6">
        <div
          className="w-6 h-6 rounded-full border border-[#E7E8EB]"
          style={{ backgroundColor: color }}
        />
        <div className="flex items-center gap-2">
          <div className="w-10 h-5 bg-primary rounded-full relative cursor-pointer">
            <div className="absolute right-1 top-1 w-3 h-3 bg-white rounded-full" />
          </div>
        </div>
        <button
          onClick={onRemove}
          className="text-slate-400 hover:text-red-500 transition-colors"
        >
          <span className="material-symbols-outlined text-lg">delete</span>
        </button>
      </div>
    </div>
  );
}
