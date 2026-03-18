import { useState } from 'react';
import type { MasterDataValue } from '../../services/masterDataService';

interface ValuesTableProps {
  values: MasterDataValue[];
  onEdit: (value: MasterDataValue) => void;
  onToggle: (value: MasterDataValue) => void;
  onReorder: (fromIndex: number, toIndex: number) => void;
  searchActive: boolean;
}

function SeverityBadge({ severity }: { severity: string | null }) {
  if (!severity) return <span className="text-slate-300">-</span>;
  const colors: Record<string, string> = {
    high: 'bg-[#FF4D4D]/10 border-[#FF4D4D]/20 text-[#FF4D4D]',
    medium: 'bg-[#FFB020]/10 border-[#FFB020]/20 text-[#FFB020]',
    low: 'bg-[#02F576]/10 border-[#02F576]/20 text-[#02F576]',
  };
  const cls = colors[severity] || 'bg-slate-100 text-slate-500';
  return (
    <span className={`px-2 py-1 border rounded-[4px] text-xs font-semibold ${cls}`}>
      {severity.charAt(0).toUpperCase() + severity.slice(1)}
    </span>
  );
}

function StatusBadge({ isActive }: { isActive: boolean }) {
  if (isActive) {
    return (
      <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-[4px] bg-[#5F2CFF]/10 text-[#5F2CFF] text-xs font-bold">
        <span className="w-1.5 h-1.5 rounded-full bg-[#5F2CFF]" />
        Active
      </span>
    );
  }
  return (
    <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-[4px] bg-slate-100 text-slate-400 text-xs font-bold">
      <span className="w-1.5 h-1.5 rounded-full bg-slate-400" />
      Inactive
    </span>
  );
}

export function ValuesTable({ values, onEdit, onToggle, onReorder, searchActive }: ValuesTableProps) {
  const [dragIdx, setDragIdx] = useState<number | null>(null);

  const handleDragStart = (idx: number) => {
    if (searchActive) return;
    setDragIdx(idx);
  };

  const handleDrop = (idx: number) => {
    if (dragIdx !== null && dragIdx !== idx) {
      onReorder(dragIdx, idx);
    }
    setDragIdx(null);
  };

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-left border-collapse">
        <thead>
          <tr className="bg-[#1E2345] text-white border-b border-[#E7E8EB]">
            <th className="px-4 py-4 w-12 text-center border-b border-[#E7E8EB]" />
            <th className="px-6 py-4 text-[14px] font-semibold uppercase tracking-wider border-b border-[#E7E8EB]">VALUE</th>
            <th className="px-6 py-4 text-[14px] font-semibold uppercase tracking-wider border-b border-[#E7E8EB]">LABEL</th>
            <th className="px-6 py-4 text-[14px] font-semibold uppercase tracking-wider border-b border-[#E7E8EB]">SEVERITY</th>
            <th className="px-6 py-4 text-[14px] font-semibold uppercase tracking-wider border-b border-[#E7E8EB]">DESCRIPTION</th>
            <th className="px-6 py-4 text-[14px] font-semibold uppercase tracking-wider border-b border-[#E7E8EB]">STATUS</th>
            <th className="px-6 py-4 text-[14px] font-semibold uppercase tracking-wider w-24 border-b border-[#E7E8EB]">Actions</th>
          </tr>
        </thead>
        <tbody className="text-slate-700 bg-white">
          {values.map((v, idx) => (
            <tr
              key={v.id}
              className="hover:bg-slate-50 transition-colors group border-b border-[#E7E8EB]"
              draggable={!searchActive}
              onDragStart={() => handleDragStart(idx)}
              onDragOver={(e) => e.preventDefault()}
              onDrop={() => handleDrop(idx)}
            >
              <td className="px-4 py-4 text-center cursor-move text-slate-300 group-hover:text-slate-500">
                {!searchActive && (
                  <span className="material-symbols-outlined">drag_indicator</span>
                )}
              </td>
              <td className="px-6 py-4 font-mono text-[16px] text-slate-500 font-normal">{v.value}</td>
              <td className="px-6 py-4 text-[16px] text-slate-900 font-normal">{v.label}</td>
              <td className="px-6 py-4 text-[16px] font-normal">
                <SeverityBadge severity={v.severity} />
              </td>
              <td className="px-6 py-4 text-[16px] font-normal">{v.description || ''}</td>
              <td className="px-6 py-4">
                <StatusBadge isActive={v.is_active} />
              </td>
              <td className="px-6 py-4">
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => onEdit(v)}
                    className="p-1.5 text-slate-400 hover:text-[#5F2CFF] hover:bg-[#5F2CFF]/5 rounded"
                  >
                    <span className="material-symbols-outlined text-[20px]">edit</span>
                  </button>
                  <button
                    onClick={() => onToggle(v)}
                    className="p-1.5 text-slate-400 hover:text-red-500 hover:bg-red-50 rounded"
                  >
                    <span className="material-symbols-outlined text-[20px]">
                      {v.is_active ? 'toggle_on' : 'toggle_off'}
                    </span>
                  </button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
