import { useState } from 'react';
import type { MasterDataValue } from '../../services/masterDataService';

interface EditValueRowProps {
  item: MasterDataValue;
  onSave: (data: Partial<MasterDataValue>) => void;
  onCancel: () => void;
}

export function EditValueRow({ item, onSave, onCancel }: EditValueRowProps) {
  const [value, setValue] = useState(item.value);
  const [label, setLabel] = useState(item.label);
  const [severity, setSeverity] = useState(item.severity || '');
  const [description, setDescription] = useState(item.description || '');

  const handleSave = () => {
    onSave({
      value: value.trim(),
      label: label.trim(),
      severity: severity || undefined,
      description: description || undefined,
    });
  };

  return (
    <tr className="bg-yellow-50/50 border-b border-[#E7E8EB]">
      <td className="px-4 py-3 text-center">
        <span className="material-symbols-outlined text-yellow-500 text-[20px]">edit</span>
      </td>
      <td className="px-6 py-3">
        <input
          type="text"
          value={value}
          onChange={(e) => setValue(e.target.value)}
          className="w-full px-2 py-1.5 border border-[#E7E8EB] rounded text-sm focus:outline-none focus:ring-2 focus:ring-[#5F2CFF]/20"
        />
      </td>
      <td className="px-6 py-3">
        <input
          type="text"
          value={label}
          onChange={(e) => setLabel(e.target.value)}
          className="w-full px-2 py-1.5 border border-[#E7E8EB] rounded text-sm focus:outline-none focus:ring-2 focus:ring-[#5F2CFF]/20"
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
          className="w-full px-2 py-1.5 border border-[#E7E8EB] rounded text-sm focus:outline-none focus:ring-2 focus:ring-[#5F2CFF]/20"
        />
      </td>
      <td className="px-6 py-3" />
      <td className="px-6 py-3">
        <div className="flex items-center gap-2">
          <button onClick={handleSave} className="p-1.5 text-green-600 hover:bg-green-50 rounded">
            <span className="material-symbols-outlined text-[20px]">check</span>
          </button>
          <button onClick={onCancel} className="p-1.5 text-slate-400 hover:bg-slate-100 rounded">
            <span className="material-symbols-outlined text-[20px]">close</span>
          </button>
        </div>
      </td>
    </tr>
  );
}
