/* StageChart component */
import type { StageDistribution } from '../../services/analyticsService';

interface StageChartProps {
  data: StageDistribution[];
}

const BAR_COLORS = ['#5F2CFF', '#8A5EFF', '#B599FF', '#D3C4FF', '#EBE5FF'];

export function StageChart({ data }: StageChartProps) {
  return (
    <div className="bg-white p-8 rounded-[24px] border border-slate-100 shadow-[0_4px_6px_-1px_rgba(0,0,0,0.05),0_2px_4px_-1px_rgba(0,0,0,0.03)]">
      <div className="flex justify-between items-center mb-8">
        <h3 className="font-bold text-slate-800 text-xl">Use Cases by Stage</h3>
        <button className="text-slate-400 hover:text-slate-600">
          <span className="material-symbols-outlined">more_horiz</span>
        </button>
      </div>
      <div className="space-y-6">
        {data.map((item, i) => (
          <div key={item.stage} className="space-y-2">
            <div className="flex justify-between text-xs font-bold">
              <span className="text-slate-600">{item.stage}</span>
              <span className="text-slate-900">{item.count}</span>
            </div>
            <div className="w-full bg-slate-100 h-3 rounded-full overflow-hidden">
              <div
                className="h-full rounded-full"
                style={{ width: `${item.percentage}%`, backgroundColor: BAR_COLORS[i] || BAR_COLORS[0] }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
