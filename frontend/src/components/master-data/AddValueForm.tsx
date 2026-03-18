import React, { useState } from 'react';

interface AddValueFormProps {
  onSubmit: (data: { value: string; label: string; severity?: string; description?: string }) => void;
  onCancel: () => void;
}

export function AddValueForm({ onSubmit, onCancel }: AddValueFormProps) {
  const [value, setValue] = useState('');
  const [label, setLabel] = useState('');
  const [severity, setSeverity] = useState('');
  const [description, setDescription] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!value.trim() || !label.trim()) return;
    onSubmit({
      value: value.trim(),
      label: label.trim(),
      severity: severity || undefined,
      description: description || undefined,
    });
  };

  return (
    <tr className="bg-[#5F2CFF]/5 border-b border-[#E7E8EB]">
      <td className="px-4 py-3 text-center">
        <span className="material-symbols-outlined text-[#5F2CFF] text-[20px]">add_circle</span>
      </td>
      <td className="px-6 py-3">
        <input
          type="text"
          value={value}
          onChange={(e) => setValue(e.target.value)}
          placeholder="value_key"
          className="w-full px-2 py-1.5 border border-[#E7E8EB] rounded text-sm focus:outline-none focus:ring-2 focus:ring-[#5F2CFF]/20 focus:border-[#5F2CFF]"
        />
      </td>
      <td className="px-6 py-3">
        <input
          type="text"
          value={label}
          onChange={(e) => setLabel(e.target.value)}
          placeholder="Display Label"
          className="w-full px-2 py-1.5 border border-[#E7E8EB] rounded text-sm focus:outline-none focus:ring-2 focus:ring-[#5F2CFF]/20 focus:border-[#5F2CFF]"
        />
      </td>
      <td className="px-6 py-3">
        <select
          value={severity}
          onChange={(e) => setSeverity(e.target.value)}
          className="w-full px-2 py-1.5 border border-[#E7E8EB] rounded text-sm focus:outline-none focus:ring-2 focus:ring-[#5F2CFF]/20"
        >
          <option value="">None</option>
          <option value="high">High</option>
          <option value="medium">Medium</option>
          <option value="low">Low</option>
        </select>
      </td>
      <td className="px-6 py-3">
        <input
          type="text"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="Description..."
          className="w-full px-2 py-1.5 border border-[#E7E8EB] rounded text-sm focus:outline-none focus:ring-2 focus:ring-[#5F2CFF]/20 focus:border-[#5F2CFF]"
        />
      </td>
      <td className="px-6 py-3" />
      <td className="px-6 py-3">
        <div className="flex items-center gap-2">
          <button
            onClick={handleSubmit}
            className="p-1.5 text-[#5F2CFF] hover:bg-[#5F2CFF]/10 rounded"
          >
            <span className="material-symbols-outlined text-[20px]">check</span>
          </button>
          <button
            onClick={onCancel}
            className="p-1.5 text-slate-400 hover:bg-slate-100 rounded"
          >
            <span className="material-symbols-outlined text-[20px]">close</span>
          </button>
        </div>
      </td>
    </tr>
  );
}
