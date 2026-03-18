import type {
  FieldsUpdateStage,
  ScoringStageInput,
  StageInput,
  Template,
  TemplateCreatePayload,
  TemplateListResponse,
} from '../types/template';
import { apiFetch } from './api';

const API_BASE = '/api/v1/templates';

export async function fetchTemplates(params: {
  status?: string;
  category?: string;
  search?: string;
  page?: number;
  page_size?: number;
}): Promise<TemplateListResponse> {
  const query = new URLSearchParams();
  if (params.status) query.set('status', params.status);
  if (params.category) query.set('category', params.category);
  if (params.search) query.set('search', params.search);
  if (params.page) query.set('page', String(params.page));
  if (params.page_size) query.set('page_size', String(params.page_size));
  const response = await apiFetch(`${API_BASE}?${query.toString()}`);
  if (!response.ok) throw new Error('Failed to fetch templates');
  return response.json() as Promise<TemplateListResponse>;
}

export async function fetchTemplate(id: string): Promise<Template> {
  const response = await apiFetch(`${API_BASE}/${id}`);
  if (!response.ok) throw new Error('Failed to fetch template');
  return response.json() as Promise<Template>;
}

export async function createTemplate(
  data: TemplateCreatePayload,
): Promise<{ id: string; status: string }> {
  const response = await apiFetch(API_BASE, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!response.ok) throw new Error('Failed to create template');
  return response.json();
}

export async function updateTemplate(
  id: string,
  data: Partial<TemplateCreatePayload>,
): Promise<{ id: string; status: string }> {
  const response = await apiFetch(`${API_BASE}/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!response.ok) throw new Error('Failed to update template');
  return response.json();
}

export async function updateStages(
  id: string,
  stages: StageInput[],
): Promise<{ template_id: string; stage_count: string }> {
  const response = await apiFetch(`${API_BASE}/${id}/stages`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ stages }),
  });
  if (!response.ok) throw new Error('Failed to update stages');
  return response.json();
}

export async function updateFields(
  id: string,
  stages: FieldsUpdateStage[],
): Promise<{ id: string; status: string }> {
  const response = await apiFetch(`${API_BASE}/${id}/fields`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ stages }),
  });
  if (!response.ok) throw new Error('Failed to update fields');
  return response.json();
}

export async function updateScoring(
  id: string,
  stages: ScoringStageInput[],
): Promise<{ id: string; status: string }> {
  const response = await apiFetch(`${API_BASE}/${id}/scoring`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ stages }),
  });
  if (!response.ok) throw new Error('Failed to update scoring');
  return response.json();
}

export async function publishTemplate(
  id: string,
): Promise<{ id: string; status: string; version: string }> {
  const response = await apiFetch(`${API_BASE}/${id}/publish`, {
    method: 'POST',
  });
  if (!response.ok) throw new Error('Failed to publish template');
  return response.json();
}

export async function deleteTemplate(id: string): Promise<void> {
  const response = await apiFetch(`${API_BASE}/${id}`, {
    method: 'DELETE',
  });
  if (!response.ok) throw new Error('Failed to delete template');
}

export async function cloneTemplate(
  id: string,
): Promise<{ id: string; status: string }> {
  const response = await apiFetch(`${API_BASE}/${id}/clone`, {
    method: 'POST',
  });
  if (!response.ok) throw new Error('Failed to clone template');
  return response.json();
}
