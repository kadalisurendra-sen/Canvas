/* CategorySidebar component */
import type { Category } from '../../services/masterDataService';

interface CategorySidebarProps {
  categories: Category[];
  selectedId: string | null;
  onSelect: (id: string) => void;
}

const ICON_MAP: Record<string, string> = {
  organizational_taxonomy: 'account_tree',
  kpis: 'trending_up',
  solution_types: 'code',
  digital_platforms: 'devices',
  ml_models: 'memory',
  risk_categories: 'gpp_maybe',
};

export function CategorySidebar({ categories, selectedId, onSelect }: CategorySidebarProps) {
  return (
    <div className="w-80 border-r border-[#E7E8EB] flex flex-col bg-white shadow-[0px_4px_16px_rgba(21,28,40,0.08)] z-10">
      <div className="p-4 border-b border-[#E7E8EB]">
        <h2 className="text-lg font-bold text-slate-800">Data Categories</h2>
        <p className="text-xs text-slate-500">Select a category to manage values</p>
      </div>
      <div className="flex-1 overflow-y-auto p-2 space-y-1">
        {categories.map((cat) => {
          const isActive = cat.id === selectedId;
          const icon = ICON_MAP[cat.name] || cat.icon || 'folder';
          return (
            <button
              key={cat.id}
              onClick={() => onSelect(cat.id)}
              className={`w-full flex items-center justify-between px-3 py-3 rounded-[8px] transition-colors ${
                isActive
                  ? 'bg-[#5F2CFF]/15 text-[#5F2CFF] border-l-[3px] border-l-[#5F2CFF]'
                  : 'text-slate-600 hover:bg-slate-50'
              }`}
            >
              <div className="flex items-center gap-3">
                <span className={`material-symbols-outlined text-[20px] ${isActive ? '' : 'text-slate-400'}`}>
                  {icon}
                </span>
                <span className={`text-sm ${isActive ? 'font-semibold' : 'font-medium'}`}>
                  {cat.display_name}
                </span>
              </div>
              {cat.item_count > 0 && (
                isActive ? (
                  <span className="text-xs font-bold bg-[#5F2CFF] text-white px-2 py-0.5 rounded-full">
                    {cat.item_count}
                  </span>
                ) : (
                  <span className="text-xs font-medium text-slate-400">{cat.item_count}</span>
                )
              )}
            </button>
          );
        })}
      </div>
    </div>
  );
}
