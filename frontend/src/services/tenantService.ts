import type {
  TenantSettings,
  UpdateBrandingRequest,
  UpdateDefaultsRequest,
  UpdateGeneralRequest,
} from '../types/tenant';
import { apiFetch } from './api';

const API_BASE = '/api/v1/tenants';

export interface TenantListItem {
  id: string;
  name: string;
  slug: string;
  schema_name: string;
  keycloak_realm: string;
  is_active: boolean;
  plan_name: string;
  user_count: number;
  created_at: string;
}

export async function fetchAllTenants(): Promise<TenantListItem[]> {
  const response = await apiFetch(`${API_BASE}/all`);
  if (!response.ok) {
    throw new Error('Failed to fetch tenants');
  }
  return response.json() as Promise<TenantListItem[]>;
}

export async function deleteTenant(tenantId: string): Promise<void> {
  const response = await apiFetch(`${API_BASE}/delete/${tenantId}`, {
    method: 'DELETE',
  });
  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to delete tenant');
  }
}

export async function fetchTenant(
  tenantId: string
): Promise<TenantSettings> {
  const response = await apiFetch(`${API_BASE}/${tenantId}`);
  if (!response.ok) {
    throw new Error('Failed to fetch tenant settings');
  }
  return response.json() as Promise<TenantSettings>;
}

export async function updateGeneral(
  tenantId: string,
  data: UpdateGeneralRequest
): Promise<void> {
  const response = await apiFetch(`${API_BASE}/${tenantId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!response.ok) {
    throw new Error('Failed to update general settings');
  }
}

export async function updateBranding(
  tenantId: string,
  data: UpdateBrandingRequest
): Promise<void> {
  const response = await apiFetch(`${API_BASE}/${tenantId}/branding`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!response.ok) {
    throw new Error('Failed to update branding');
  }
}

export async function updateDefaults(
  tenantId: string,
  data: UpdateDefaultsRequest
): Promise<void> {
  const response = await apiFetch(`${API_BASE}/${tenantId}/defaults`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!response.ok) {
    throw new Error('Failed to update defaults');
  }
}
