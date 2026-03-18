/* MetricCards component */
import type { MetricCard } from '../../services/analyticsService';

interface MetricCardsProps {
  metrics: MetricCard[];
}

export function MetricCards({ metrics }: MetricCardsProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4 mb-8">
      {metrics.map((m, i) => {
        const isGreen = m.label === 'Completed Evaluations' || m.label === 'Average ROI';
        return (
          <div key={i} className="bg-white p-6 rounded-[24px] border border-slate-100 shadow-[0_4px_6px_-1px_rgba(0,0,0,0.05),0_2px_4px_-1px_rgba(0,0,0,0.03)] flex flex-col gap-1">
            <p className="text-slate-500 text-xs font-bold uppercase tracking-wider">{m.label}</p>
            <div className="flex items-baseline gap-2 mt-2">
              <span className={`text-[48px] font-bold leading-none ${isGreen ? 'text-green-600' : 'text-[#5F2CFF]'}`}>
                {m.value}
              </span>
              {m.change && (
                <span className="text-xs font-bold text-green-600 bg-green-50 px-1.5 py-0.5 rounded">
                  {m.change}
                </span>
              )}
            </div>
            <p className="text-[10px] text-slate-400 mt-2">{m.subtitle}</p>
          </div>
        );
      })}
    </div>
  );
}
