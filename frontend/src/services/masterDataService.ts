import { apiFetch } from './api';

const API_BASE = '/api/v1/master-data';

export interface Category {
  id: string;
  name: string;
  display_name: string;
  icon: string | null;
  sort_order: number;
  item_count: number;
}

export interface MasterDataValue {
  id: string;
  value: string;
  label: string;
  severity: string | null;
  description: string | null;
  is_active: boolean;
  sort_order: number;
}

export interface PaginatedValues {
  items: MasterDataValue[];
  total: number;
  page: number;
  page_size: number;
}

export interface ImportResult {
  imported: number;
  skipped: number;
  errors: Array<{ row: number; message: string }>;
}

export async function fetchCategories(): Promise<Category[]> {
  const res = await apiFetch(`${API_BASE}/categories`);
  if (!res.ok) throw new Error('Failed to fetch categories');
  return res.json();
}

export async function fetchValues(
  catId: string,
  search?: string,
  page: number = 1,
  pageSize: number = 10
): Promise<PaginatedValues> {
  const params = new URLSearchParams({ page: String(page), page_size: String(pageSize) });
  if (search) params.set('search', search);
  const res = await apiFetch(`${API_BASE}/categories/${catId}/values?${params}`);
  if (!res.ok) throw new Error('Failed to fetch values');
  return res.json();
}

export async function createValue(
  catId: string,
  data: { value: string; label: string; severity?: string; description?: string }
): Promise<MasterDataValue> {
  const res = await apiFetch(`${API_BASE}/categories/${catId}/values`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error('Failed to create value');
  return res.json();
}

export async function updateValue(
  valueId: string,
  data: Partial<MasterDataValue>
): Promise<MasterDataValue> {
  const res = await apiFetch(`${API_BASE}/values/${valueId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error('Failed to update value');
  return res.json();
}

export async function deleteValue(valueId: string): Promise<void> {
  const res = await apiFetch(`${API_BASE}/values/${valueId}`, {
    method: 'DELETE',
  });
  if (!res.ok) throw new Error('Failed to delete value');
}

export async function reorderValues(catId: string, valueIds: string[]): Promise<void> {
  const res = await apiFetch(`${API_BASE}/categories/${catId}/reorder`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ value_ids: valueIds }),
  });
  if (!res.ok) throw new Error('Failed to reorder');
}

export async function importCsv(catId: string, file: File): Promise<ImportResult> {
  const formData = new FormData();
  formData.append('file', file);
  const res = await apiFetch(`${API_BASE}/categories/${catId}/import`, {
    method: 'POST',
    body: formData,
  });
  if (!res.ok) throw new Error('Import failed');
  return res.json();
}
