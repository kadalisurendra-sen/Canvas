import { useCallback, useEffect, useState } from 'react';
import { CategorySidebar } from '../components/master-data/CategorySidebar';
import { AddValueForm } from '../components/master-data/AddValueForm';
import { EditValueRow } from '../components/master-data/EditValueRow';
import { ImportModal } from '../components/master-data/ImportModal';
import { Pagination } from '../components/master-data/Pagination';
import type { Category, MasterDataValue } from '../services/masterDataService';
import {
  fetchCategories,
  fetchValues,
  createValue as apiCreateValue,
  updateValue as apiUpdateValue,
  importCsv,
} from '../services/masterDataService';

/* ---------- mock seed data (used until real API) ---------- */
const SEED_CATEGORIES: Category[] = [
  { id: 'cat-1', name: 'organizational_taxonomy', display_name: 'Organizational Taxonomy', icon: 'account_tree', sort_order: 1, item_count: 128 },
  { id: 'cat-2', name: 'kpis', display_name: 'KPIs', icon: 'trending_up', sort_order: 2, item_count: 42 },
  { id: 'cat-3', name: 'solution_types', display_name: 'Solution Types', icon: 'code', sort_order: 3, item_count: 0 },
  { id: 'cat-4', name: 'digital_platforms', display_name: 'Digital Platforms', icon: 'devices', sort_order: 4, item_count: 0 },
  { id: 'cat-5', name: 'ml_models', display_name: 'ML Models', icon: 'memory', sort_order: 5, item_count: 0 },
  { id: 'cat-6', name: 'risk_categories', display_name: 'Risk Categories', icon: 'gpp_maybe', sort_order: 6, item_count: 14 },
];

const SEED_VALUES: MasterDataValue[] = [
  { id: 'v1', value: 'data_privacy', label: 'Data Privacy', severity: 'high', description: 'Compliance with GDPR, CCPA, and data handling laws.', is_active: true, sort_order: 1 },
  { id: 'v2', value: 'implementation', label: 'Implementation', severity: 'medium', description: 'Risks related to technical complexity and integration.', is_active: true, sort_order: 2 },
  { id: 'v3', value: 'operational', label: 'Operational', severity: 'low', description: 'Potential impact on business-as-usual operations.', is_active: true, sort_order: 3 },
  { id: 'v4', value: 'biased_data', label: 'Bias and Fairness', severity: 'high', description: 'Risks of unethical model outputs due to biased training data.', is_active: true, sort_order: 4 },
];

const CATEGORY_DESCRIPTIONS: Record<string, string> = {
  risk_categories: 'Manage the categories used for assessing project and technical risks.',
  organizational_taxonomy: 'Manage organizational structures and hierarchies.',
  kpis: 'Manage key performance indicators used in evaluations.',
  solution_types: 'Manage solution type classifications.',
  digital_platforms: 'Manage digital platform categories.',
  ml_models: 'Manage ML model type classifications.',
};

export function MasterDataPage() {
  const [categories, setCategories] = useState<Category[]>(SEED_CATEGORIES);
  const [selectedCatId, setSelectedCatId] = useState<string>(SEED_CATEGORIES[5].id);
  const [values, setValues] = useState<MasterDataValue[]>(SEED_VALUES);
  const [total, setTotal] = useState(14);
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [showAdd, setShowAdd] = useState(false);
  const [editId, setEditId] = useState<string | null>(null);
  const [showImport, setShowImport] = useState(false);

  useEffect(() => {
    fetchCategories()
      .then((cats) => {
        if (cats.length > 0) {
          setCategories(cats);
          setSelectedCatId(cats[0].id);
        }
      })
      .catch(() => { /* use seed data */ });
  }, []);

  const loadValues = useCallback(async () => {
    try {
      const result = await fetchValues(selectedCatId, search || undefined, page, 10);
      setValues(result.items);
      setTotal(result.total);
    } catch {
      /* keep current values if API unavailable */
    }
  }, [selectedCatId, search, page]);

  useEffect(() => {
    const timer = setTimeout(loadValues, 200);
    return () => clearTimeout(timer);
  }, [loadValues]);

  const selectedCat = categories.find((c) => c.id === selectedCatId);
  const searchActive = search.trim().length > 0;
  const pageSize = 10;

  const filteredValues = searchActive
    ? values.filter((v) => v.label.toLowerCase().includes(search.toLowerCase()) || v.value.toLowerCase().includes(search.toLowerCase()))
    : values;

  const handleAddValue = useCallback(async (data: { value: string; label: string; severity?: string; description?: string }) => {
    try {
      await apiCreateValue(selectedCatId, data);
      await loadValues();
    } catch {
      const newVal: MasterDataValue = {
        id: `v-${Date.now()}`, value: data.value, label: data.label,
        severity: data.severity || null, description: data.description || null,
        is_active: true, sort_order: values.length + 1,
      };
      setValues((prev) => [newVal, ...prev]);
      setTotal((t) => t + 1);
    }
    setShowAdd(false);
  }, [selectedCatId, values.length, loadValues]);

  const handleEdit = useCallback((v: MasterDataValue) => { setEditId(v.id); }, []);

  const handleSaveEdit = useCallback(async (data: Partial<MasterDataValue>) => {
    if (editId) {
      try {
        await apiUpdateValue(editId, data);
        await loadValues();
      } catch {
        setValues((prev) => prev.map((v) => v.id === editId ? { ...v, ...data } : v));
      }
    }
    setEditId(null);
  }, [editId, loadValues]);

  const handleToggle = useCallback((v: MasterDataValue) => {
    setValues((prev) => prev.map((item) => item.id === v.id ? { ...item, is_active: !item.is_active } : item));
  }, []);

  const handleReorder = useCallback((from: number, to: number) => {
    setValues((prev) => {
      const next = [...prev];
      const [moved] = next.splice(from, 1);
      next.splice(to, 0, moved);
      return next.map((v, i) => ({ ...v, sort_order: i + 1 }));
    });
  }, []);

  const handleImport = async (file: File) => {
    try {
      const result = await importCsv(selectedCatId, file);
      await loadValues();
      return result;
    } catch {
      return { imported: 0, skipped: 0, errors: [] as Array<{ row: number; message: string }> };
    }
  };

  return (
    <div className="flex flex-1 overflow-hidden -m-6 -mt-6">
      <CategorySidebar categories={categories} selectedId={selectedCatId} onSelect={setSelectedCatId} />
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden p-6 gap-6 bg-white">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <h3 className="text-[32px] font-bold text-slate-900 leading-tight">{selectedCat?.display_name || 'Category'}</h3>
            <p className="text-slate-500 text-sm mt-1">{CATEGORY_DESCRIPTIONS[selectedCat?.name || ''] || ''}</p>
          </div>
          <div className="flex items-center gap-3">
            <button onClick={() => setShowImport(true)} className="flex items-center gap-2 px-4 py-2 border border-slate-300 text-slate-700 font-semibold rounded-[8px] hover:bg-slate-50 transition-colors text-sm">
              <span className="material-symbols-outlined text-[18px]">upload_file</span>Import from CSV
            </button>
            <button onClick={() => setShowAdd(true)} className="flex items-center gap-2 px-4 py-2 bg-[#5F2CFF] text-white font-semibold rounded-[8px] hover:bg-[#5F2CFF]/90 transition-colors text-sm shadow-sm">
              <span className="material-symbols-outlined text-[18px]">add</span>Add Value
            </button>
          </div>
        </div>
        <div className="flex items-center relative max-w-md">
          <span className="material-symbols-outlined absolute left-3 text-slate-400 text-[20px]">search</span>
          <input value={search} onChange={(e) => setSearch(e.target.value)} className="w-full pl-10 pr-4 py-2 border border-[#E7E8EB] rounded-[8px] focus:outline-none focus:ring-2 focus:ring-[#5F2CFF]/20 focus:border-[#5F2CFF] text-sm shadow-sm" placeholder={`Search ${selectedCat?.display_name || ''}...`} type="text" />
        </div>
        <div className="flex-1 overflow-hidden bg-white rounded-xl shadow-[0px_4px_16px_rgba(21,28,40,0.08)] flex flex-col border border-[#E7E8EB]">
          <div className="overflow-x-auto flex-1">
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
                {showAdd && <AddValueForm onSubmit={handleAddValue} onCancel={() => setShowAdd(false)} />}
              </thead>
              <tbody className="text-slate-700 bg-white">
                {filteredValues.map((v, idx) =>
                  editId === v.id ? (
                    <EditValueRow key={v.id} item={v} onSave={handleSaveEdit} onCancel={() => setEditId(null)} />
                  ) : (
                    <ValuesTableRow key={v.id} v={v} idx={idx} searchActive={searchActive} onEdit={handleEdit} onToggle={handleToggle} onReorder={handleReorder} />
                  )
                )}
              </tbody>
            </table>
          </div>
          <Pagination page={page} pageSize={pageSize} total={total} onPageChange={setPage} />
        </div>
      </div>
      {showImport && <ImportModal onImport={handleImport} onClose={() => setShowImport(false)} />}
    </div>
  );
}

/* Inline row component to keep main component under line limit */
function ValuesTableRow({ v, idx, searchActive, onEdit, onToggle, onReorder }: {
  v: MasterDataValue; idx: number; searchActive: boolean;
  onEdit: (v: MasterDataValue) => void; onToggle: (v: MasterDataValue) => void;
  onReorder: (from: number, to: number) => void;
}) {
  const [dragOver, setDragOver] = useState(false);
  return (
    <tr
      className={`hover:bg-slate-50 transition-colors group border-b border-[#E7E8EB] ${dragOver ? 'bg-[#5F2CFF]/5' : ''}`}
      draggable={!searchActive}
      onDragStart={(e) => e.dataTransfer.setData('text/plain', String(idx))}
      onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
      onDragLeave={() => setDragOver(false)}
      onDrop={(e) => { e.preventDefault(); setDragOver(false); const from = parseInt(e.dataTransfer.getData('text/plain')); onReorder(from, idx); }}
    >
      <td className="px-4 py-4 text-center cursor-move text-slate-300 group-hover:text-slate-500">
        {!searchActive && <span className="material-symbols-outlined">drag_indicator</span>}
      </td>
      <td className="px-6 py-4 font-mono text-[16px] text-slate-500 font-normal">{v.value}</td>
      <td className="px-6 py-4 text-[16px] text-slate-900 font-normal">{v.label}</td>
      <td className="px-6 py-4 text-[16px] font-normal">
        {v.severity ? (
          <span className={`px-2 py-1 border rounded-[4px] text-xs font-semibold ${
            v.severity === 'high' ? 'bg-[#FF4D4D]/10 border-[#FF4D4D]/20 text-[#FF4D4D]' :
            v.severity === 'medium' ? 'bg-[#FFB020]/10 border-[#FFB020]/20 text-[#FFB020]' :
            'bg-[#02F576]/10 border-[#02F576]/20 text-[#02F576]'
          }`}>{v.severity.charAt(0).toUpperCase() + v.severity.slice(1)}</span>
        ) : <span className="text-slate-300">-</span>}
      </td>
      <td className="px-6 py-4 text-[16px] font-normal">{v.description || ''}</td>
      <td className="px-6 py-4">
        <span className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded-[4px] text-xs font-bold ${
          v.is_active ? 'bg-[#5F2CFF]/10 text-[#5F2CFF]' : 'bg-slate-100 text-slate-400'
        }`}>
          <span className={`w-1.5 h-1.5 rounded-full ${v.is_active ? 'bg-[#5F2CFF]' : 'bg-slate-400'}`} />
          {v.is_active ? 'Active' : 'Inactive'}
        </span>
      </td>
      <td className="px-6 py-4">
        <div className="flex items-center gap-2">
          <button onClick={() => onEdit(v)} className="p-1.5 text-slate-400 hover:text-[#5F2CFF] hover:bg-[#5F2CFF]/5 rounded">
            <span className="material-symbols-outlined text-[20px]">edit</span>
          </button>
          <button onClick={() => onToggle(v)} className="p-1.5 text-slate-400 hover:text-red-500 hover:bg-red-50 rounded">
            <span className="material-symbols-outlined text-[20px]">{v.is_active ? 'toggle_on' : 'toggle_off'}</span>
          </button>
        </div>
      </td>
    </tr>
  );
}
