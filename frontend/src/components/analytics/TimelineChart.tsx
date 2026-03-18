/* TimelineChart component */
import type { TimelinePoint } from '../../services/analyticsService';

interface TimelineChartProps {
  data: TimelinePoint[];
}

export function TimelineChart({ data }: TimelineChartProps) {
  if (data.length === 0) {
    return (
      <div className="bg-white p-8 rounded-[24px] border border-slate-100 shadow-card flex items-center justify-center h-64">
        <p className="text-slate-400 text-sm">No data available</p>
      </div>
    );
  }

  return (
    <div className="lg:col-span-2 bg-white p-8 rounded-[24px] border border-slate-100 shadow-[0_4px_6px_-1px_rgba(0,0,0,0.05),0_2px_4px_-1px_rgba(0,0,0,0.03)]">
      <div className="flex justify-between items-center mb-8">
        <h3 className="font-bold text-slate-800 text-xl">Evaluations Over Time</h3>
        <div className="flex gap-4">
          <div className="flex items-center gap-2">
            <div className="w-3 h-0.5 bg-[#5F2CFF]" />
            <span className="text-xs text-slate-500">Evaluations</span>
          </div>
        </div>
      </div>
      <div className="h-64 relative">
        <svg className="w-full h-full" viewBox="0 0 1000 200" preserveAspectRatio="none">
          <defs>
            <linearGradient id="chartGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#5F2CFF" stopOpacity="0.2" />
              <stop offset="100%" stopColor="#5F2CFF" stopOpacity="0" />
            </linearGradient>
          </defs>
          <path
            d="M0,180 Q100,160 200,140 T400,120 T600,80 T800,60 T1000,30 L1000,200 L0,200 Z"
            fill="url(#chartGradient)"
          />
          <path
            d="M0,180 Q100,160 200,140 T400,120 T600,80 T800,60 T1000,30"
            fill="none" stroke="#5F2CFF" strokeWidth="4" strokeLinecap="round"
          />
          <circle cx="200" cy="140" r="4" fill="white" stroke="#5F2CFF" strokeWidth="2" />
          <circle cx="400" cy="120" r="4" fill="white" stroke="#5F2CFF" strokeWidth="2" />
          <circle cx="600" cy="80" r="4" fill="white" stroke="#5F2CFF" strokeWidth="2" />
          <circle cx="800" cy="60" r="4" fill="white" stroke="#5F2CFF" strokeWidth="2" />
        </svg>
        <div className="flex justify-between mt-4 text-[10px] text-slate-400 font-bold uppercase tracking-wider">
          {data.map((d) => (
            <span key={d.month}>{d.month}</span>
          ))}
        </div>
      </div>
    </div>
  );
}
