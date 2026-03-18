/* TemplateUsageChart component */
import type { TemplateUsage } from '../../services/analyticsService';

interface TemplateUsageChartProps {
  data: TemplateUsage[];
}

export function TemplateUsageChart({ data }: TemplateUsageChartProps) {
  /* Build SVG donut from cumulative dash offsets */
  let offset = 0;
  const segments = data.map((item) => {
    const seg = { ...item, dashArray: `${item.percentage} ${100 - item.percentage}`, dashOffset: -offset };
    offset += item.percentage;
    return seg;
  });

  return (
    <div className="bg-white p-8 rounded-[24px] border border-slate-100 shadow-[0_4px_6px_-1px_rgba(0,0,0,0.05),0_2px_4px_-1px_rgba(0,0,0,0.03)]">
      <div className="flex justify-between items-center mb-8">
        <h3 className="font-bold text-slate-800 text-xl">Templates Usage</h3>
        <button className="text-slate-400 hover:text-slate-600">
          <span className="material-symbols-outlined">more_horiz</span>
        </button>
      </div>
      <div className="flex items-center justify-between gap-8 h-full">
        <div className="relative w-48 h-48 flex-shrink-0">
          <svg className="w-full h-full transform -rotate-90" viewBox="0 0 36 36">
            <circle cx="18" cy="18" r="16" fill="none" stroke="#f1f5f9" strokeWidth="4" />
            {segments.map((seg) => (
              <circle
                key={seg.category}
                cx="18" cy="18" r="16" fill="none"
                stroke={seg.color}
                strokeWidth="4"
                strokeDasharray={seg.dashArray}
                strokeDashoffset={seg.dashOffset}
              />
            ))}
          </svg>
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <span className="text-2xl font-black text-slate-800">100%</span>
            <span className="text-[10px] text-slate-500 uppercase font-bold tracking-tight">Total</span>
          </div>
        </div>
        <div className="flex-1 space-y-3">
          {data.map((item) => (
            <div key={item.category} className="flex items-center gap-3">
              <div className="w-3 h-3 rounded-sm" style={{ backgroundColor: item.color }} />
              <span className="text-sm text-slate-600">{item.category}</span>
              <span className="text-sm font-bold text-slate-900 ml-auto">{item.percentage}%</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
