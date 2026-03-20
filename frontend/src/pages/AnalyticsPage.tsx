import { useCallback, useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { MetricCards } from '../components/analytics/MetricCards';
import { StageChart } from '../components/analytics/StageChart';
import { TemplateUsageChart } from '../components/analytics/TemplateUsageChart';
import { TimelineChart } from '../components/analytics/TimelineChart';
import { TopUsersTable } from '../components/analytics/TopUsersTable';
import { AuditLogTab } from '../components/analytics/AuditLogTab';
import type { AuditFilters } from '../components/analytics/AuditLogTab';
import type { DashboardData, TopUser, PaginatedAuditLogs } from '../services/analyticsService';
import {
  fetchDashboard,
  fetchTopUsers as apiFetchTopUsers,
  fetchAuditLogs,
} from '../services/analyticsService';
import { apiFetch } from '../services/api';

const EMPTY_DASHBOARD: DashboardData = {
  metrics: [],
  stage_distribution: [],
  template_usage: [],
  evaluations_timeline: [],
};

const EMPTY_LOGS: PaginatedAuditLogs = {
  items: [],
  total: 0,
  page: 1,
  page_size: 10,
};

export function AnalyticsPage() {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState<'dashboard' | 'audit'>('dashboard');
  const [dateRange] = useState('Last 30 Days');
  const [dashboard, setDashboard] = useState<DashboardData>(EMPTY_DASHBOARD);
  const [topUsers, setTopUsers] = useState<TopUser[]>([]);
  const [auditLogs, setAuditLogs] = useState<PaginatedAuditLogs>(EMPTY_LOGS);
  const [auditPage, setAuditPage] = useState(1);
  const [auditFilters, setAuditFilters] = useState<AuditFilters>({});
  const [loading, setLoading] = useState(true);

  const isSuperAdmin = user?.roles.includes('system_admin');

  useEffect(() => {
    setLoading(true);
    Promise.all([
      fetchDashboard().then(setDashboard).catch(() => {}),
      apiFetchTopUsers().then(setTopUsers).catch(() => {}),
    ]).finally(() => setLoading(false));
  }, []);

  const loadAuditLogs = useCallback(async (filters: AuditFilters, page: number) => {
    try {
      const result = await fetchAuditLogs({
        ...filters,
        page,
        page_size: 10,
      });
      setAuditLogs(result);
    } catch {
      /* keep empty */
    }
  }, []);

  useEffect(() => {
    loadAuditLogs(auditFilters, auditPage);
  }, [auditFilters, auditPage, loadAuditLogs]);

  const handleAuditFilter = useCallback((filters: AuditFilters) => {
    setAuditFilters(filters);
    setAuditPage(1);
  }, []);

  const handleAuditPage = useCallback((page: number) => {
    setAuditPage(page);
  }, []);

  const handleExportReport = useCallback(async () => {
    try {
      const res = await apiFetch('/api/v1/analytics/export');
      if (!res.ok) return;
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `analytics_report_${new Date().toISOString().slice(0, 10)}.csv`;
      a.click();
      URL.revokeObjectURL(url);
    } catch { /* download failed */ }
  }, []);

  const handleExportAudit = useCallback(async () => {
    try {
      const res = await apiFetch('/api/v1/analytics/audit-logs/export');
      if (!res.ok) return;
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `audit_log_${new Date().toISOString().slice(0, 10)}.csv`;
      a.click();
      URL.revokeObjectURL(url);
    } catch { /* download failed */ }
  }, []);

  return (
    <div className="max-w-7xl mx-auto">
      <div className="flex flex-col gap-6 mb-8">
        <div className="flex justify-between items-end">
          <div>
            <h2 className="text-[32px] font-bold tracking-tight text-slate-900">
              {isSuperAdmin ? 'Platform Analytics' : 'Analytics & Audit Logs'}
            </h2>
            <p className="text-slate-500 mt-1">
              {isSuperAdmin
                ? 'Platform-wide metrics across all tenants.'
                : 'Monitor tenant engagement and system integrity.'}
            </p>
          </div>
          <div className="flex gap-2">
            <button className="flex items-center gap-2 px-4 py-2 bg-white border border-slate-200 rounded-md text-sm font-semibold text-slate-700 hover:bg-slate-50 transition-colors shadow-sm">
              <span className="material-symbols-outlined text-lg">calendar_today</span>
              {dateRange}
            </button>
            {activeTab === 'dashboard' && (
              <button
                onClick={handleExportReport}
                className="flex items-center gap-2 px-4 py-2 bg-[#5F2CFF] text-white rounded-md text-sm font-semibold hover:bg-[#5F2CFF]/90 transition-colors shadow-sm"
              >
                <span className="material-symbols-outlined text-lg">download</span>
                Export Report
              </button>
            )}
          </div>
        </div>
        <div className="border-b border-slate-200 flex gap-8">
          <button
            onClick={() => setActiveTab('dashboard')}
            className={`pb-4 border-b-2 text-sm tracking-wide transition-colors ${
              activeTab === 'dashboard'
                ? 'border-[#5F2CFF] text-[#5F2CFF] font-bold'
                : 'border-transparent text-slate-500 font-medium hover:text-slate-800'
            }`}
          >
            Dashboard
          </button>
          <button
            onClick={() => setActiveTab('audit')}
            className={`pb-4 border-b-2 text-sm tracking-wide transition-colors ${
              activeTab === 'audit'
                ? 'border-[#5F2CFF] text-[#5F2CFF] font-bold'
                : 'border-transparent text-slate-500 font-medium hover:text-slate-800'
            }`}
          >
            {isSuperAdmin ? 'Platform Audit Log' : 'Audit Log'}
          </button>
        </div>
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-20">
          <span className="text-slate-400">Loading analytics...</span>
        </div>
      ) : activeTab === 'dashboard' ? (
        <>
          <MetricCards metrics={dashboard.metrics} />
          {dashboard.stage_distribution.length > 0 && dashboard.template_usage.length > 0 && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
              <StageChart data={dashboard.stage_distribution} />
              <TemplateUsageChart data={dashboard.template_usage} />
            </div>
          )}
          {dashboard.stage_distribution.length === 0 && dashboard.template_usage.length > 0 && (
            <div className="mb-8">
              <TemplateUsageChart data={dashboard.template_usage} />
            </div>
          )}
          {dashboard.stage_distribution.length > 0 && dashboard.template_usage.length === 0 && (
            <div className="mb-8">
              <StageChart data={dashboard.stage_distribution} />
            </div>
          )}
          {!isSuperAdmin && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              {dashboard.evaluations_timeline.length > 0 && (
                <TimelineChart data={dashboard.evaluations_timeline} />
              )}
              {topUsers.length > 0 && (
                <TopUsersTable users={topUsers} />
              )}
            </div>
          )}
          {dashboard.metrics.length === 0 && (
            <div className="text-center py-20 text-slate-400">
              <span className="material-symbols-outlined text-4xl mb-2 block">analytics</span>
              No data available yet. Start creating templates to see analytics.
            </div>
          )}
        </>
      ) : (
        <AuditLogTab
          logs={auditLogs}
          onFilter={handleAuditFilter}
          onPageChange={handleAuditPage}
          onExport={handleExportAudit}
        />
      )}
    </div>
  );
}
