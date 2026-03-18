import React from 'react';

const COLORS = [
  '#02F576', '#3B82F6', '#6366F1', '#5F2CFF',
  '#EC4899', '#F97316', '#F59E0B', '#64748B',
];

interface ColorPickerProps {
  selected: string;
  onSelect: (color: string) => void;
}

export function ColorPicker({ selected, onSelect }: ColorPickerProps) {
  return (
    <div className="flex flex-col gap-3">
      <label className="text-[14px] font-medium text-[#3D4353]">Theme Color</label>
      <div className="flex flex-wrap gap-2">
        {COLORS.map((color) => (
          <button
            key={color}
            type="button"
            onClick={() => onSelect(color)}
            className={`w-8 h-8 rounded-full border-2 border-white flex items-center justify-center ${
              selected === color ? 'ring-2 ring-primary' : ''
            }`}
            style={{ backgroundColor: color }}
          >
            {selected === color && (
              <span className="material-symbols-outlined text-[16px] text-[#1E2345] font-bold">
                check
              </span>
            )}
          </button>
        ))}
      </div>
    </div>
  );
}
