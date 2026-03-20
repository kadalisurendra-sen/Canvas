import React from 'react';

interface StageRowProps {
  index: number;
  name: string;
  total: number;
  onNameChange: (name: string) => void;
  onRemove: () => void;
  onMoveUp: () => void;
  onMoveDown: () => void;
}

export function StageRow({
  index, name, total, onNameChange, onRemove, onMoveUp, onMoveDown,
}: StageRowProps) {
  return (
    <div className="p-4 bg-[#F3F4F4] rounded-lg flex items-center gap-4 group border border-[#E7E8EB]">
      {/* Reorder buttons */}
      <div className="flex flex-col gap-0.5">
        <button
          onClick={onMoveUp}
          disabled={index === 0}
          className="text-slate-400 hover:text-primary disabled:opacity-20 disabled:cursor-not-allowed transition-colors"
          title="Move up"
        >
          <span className="material-symbols-outlined text-base">keyboard_arrow_up</span>
        </button>
        <button
          onClick={onMoveDown}
          disabled={index === total - 1}
          className="text-slate-400 hover:text-primary disabled:opacity-20 disabled:cursor-not-allowed transition-colors"
          title="Move down"
        >
          <span className="material-symbols-outlined text-base">keyboard_arrow_down</span>
        </button>
      </div>

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

      <button
        onClick={onRemove}
        className="text-slate-400 hover:text-red-500 transition-colors"
      >
        <span className="material-symbols-outlined text-lg">delete</span>
      </button>
    </div>
  );
}
