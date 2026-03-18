import { apiFetch } from './api';

const API_BASE = '/api/v1/analytics';

export interface MetricCard {
  label: string;
  value: string;
  change: string | null;
  subtitle: string;
}

export interface StageDistribution {
  stage: string;
  count: number;
  percentage: number;
}

export interface TemplateUsage {
  category: string;
  percentage: number;
  color: string;
}

export interface TimelinePoint {
  month: string;
  count: number;
}

export interface DashboardData {
  metrics: MetricCard[];
  stage_distribution: StageDistribution[];
  template_usage: TemplateUsage[];
  evaluations_timeline: TimelinePoint[];
}

export interface TopUser {
  name: string;
  avatar_url: string | null;
  evaluations: number;
  last_active: string;
}

export interface AuditLogEntry {
  id: string;
  created_at: string;
  user_name: string | null;
  event_type: string;
  action: string;
  details: string | null;
  ip_address: string | null;
}

export interface PaginatedAuditLogs {
  items: AuditLogEntry[];
  total: number;
  page: number;
  page_size: number;
}

export async function fetchDashboard(from?: string, to?: string): Promise<DashboardData> {
  const params = new URLSearchParams();
  if (from) params.set('from', from);
  if (to) params.set('to', to);
  const res = await apiFetch(`${API_BASE}/dashboard?${params}`);
  if (!res.ok) throw new Error('Failed to fetch dashboard');
  return res.json();
}

export async function fetchTopUsers(): Promise<TopUser[]> {
  const res = await apiFetch(`${API_BASE}/top-users`);
  if (!res.ok) throw new Error('Failed to fetch top users');
  return res.json();
}

export async function fetchAuditLogs(params: {
  user_id?: string;
  action?: string;
  event_type?: string;
  from_date?: string;
  to_date?: string;
  page?: number;
  page_size?: number;
}): Promise<PaginatedAuditLogs> {
  const searchParams = new URLSearchParams();
  if (params.user_id) searchParams.set('user_id', params.user_id);
  if (params.action) searchParams.set('action', params.action);
  if (params.event_type) searchParams.set('event_type', params.event_type);
  if (params.from_date) searchParams.set('from_date', params.from_date);
  if (params.to_date) searchParams.set('to_date', params.to_date);
  searchParams.set('page', String(params.page || 1));
  searchParams.set('page_size', String(params.page_size || 10));
  const res = await apiFetch(`${API_BASE}/audit-logs?${searchParams}`);
  if (!res.ok) throw new Error('Failed to fetch audit logs');
  return res.json();
}

export function exportDashboardUrl(from?: string, to?: string): string {
  const params = new URLSearchParams();
  if (from) params.set('from', from);
  if (to) params.set('to', to);
  return `${API_BASE}/export?${params}`;
}

export function exportAuditLogsUrl(params: {
  user_id?: string;
  action?: string;
  event_type?: string;
  from_date?: string;
  to_date?: string;
}): string {
  const searchParams = new URLSearchParams();
  if (params.user_id) searchParams.set('user_id', params.user_id);
  if (params.action) searchParams.set('action', params.action);
  if (params.event_type) searchParams.set('event_type', params.event_type);
  if (params.from_date) searchParams.set('from_date', params.from_date);
  if (params.to_date) searchParams.set('to_date', params.to_date);
  return `${API_BASE}/audit-logs/export?${searchParams}`;
}
