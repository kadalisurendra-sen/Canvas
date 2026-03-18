import React from 'react';

const ICONS = [
  'psychology', 'smart_toy', 'hub', 'cloud', 'database', 'shield',
  'insights', 'precision_manufacturing', 'speed', 'settings_suggest',
  'account_tree', 'memory',
];

interface IconPickerProps {
  selected: string;
  onSelect: (icon: string) => void;
}

export function IconPicker({ selected, onSelect }: IconPickerProps) {
  return (
    <div className="flex flex-col gap-3">
      <label className="text-[14px] font-medium text-[#3D4353]">Template Icon</label>
      <div className="grid grid-cols-6 gap-3 sm:grid-cols-12 md:grid-cols-6 lg:grid-cols-12">
        {ICONS.map((icon) => (
          <button
            key={icon}
            type="button"
            onClick={() => onSelect(icon)}
            className={`aspect-square rounded-[8px] border-2 flex items-center justify-center transition-all ${
              selected === icon
                ? 'border-primary bg-primary/5 text-primary'
                : 'border-[#CFD0D6] bg-white hover:border-primary text-slate-500'
            }`}
          >
            <span className="material-symbols-outlined">{icon}</span>
          </button>
        ))}
      </div>
    </div>
  );
}
