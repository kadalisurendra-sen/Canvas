import { useCallback, useEffect, useState } from 'react';
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

/* Mock dashboard data matching the Stitch reference */
const MOCK_DASHBOARD: DashboardData = {
  metrics: [
    { label: 'Total Projects', value: '24', change: '+3', subtitle: 'v. last month' },
    { label: 'Total Use Cases', value: '156', change: '+12', subtitle: 'v. last month' },
    { label: 'Active Evaluations', value: '38', change: null, subtitle: 'Currently in progress' },
    { label: 'Completed Evaluations', value: '92', change: null, subtitle: 'Historical total' },
    { label: 'Average ROI', value: '127%', change: null, subtitle: 'Projected overall' },
  ],
  stage_distribution: [
    { stage: 'Desirable', count: 45, percentage: 80 },
    { stage: 'Feasible', count: 38, percentage: 65 },
    { stage: 'Viable', count: 32, percentage: 55 },
    { stage: 'Prioritized', count: 25, percentage: 45 },
    { stage: 'Not Started', count: 16, percentage: 25 },
  ],
  template_usage: [
    { category: 'AI/ML', percentage: 45, color: '#5F2CFF' },
    { category: 'RPA', percentage: 25, color: '#02F576' },
    { category: 'Agentic AI', percentage: 15, color: '#8A5EFF' },
    { category: 'Data Science', percentage: 10, color: '#5EEAD4' },
    { category: 'Custom', percentage: 5, color: '#99F6E4' },
  ],
  evaluations_timeline: [
    { month: 'Jan', count: 12 }, { month: 'Feb', count: 18 },
    { month: 'Mar', count: 25 }, { month: 'Apr', count: 30 },
    { month: 'May', count: 42 }, { month: 'Jun', count: 55 },
  ],
};

const MOCK_TOP_USERS: TopUser[] = [
  { name: 'Sarah Connor', avatar_url: null, evaluations: 28, last_active: 'Today' },
  { name: 'James Miller', avatar_url: null, evaluations: 24, last_active: '2h ago' },
  { name: 'Elena R.', avatar_url: null, evaluations: 19, last_active: 'Yesterday' },
  { name: 'Mark T.', avatar_url: null, evaluations: 15, last_active: '3d ago' },
];

const MOCK_LOGS: PaginatedAuditLogs = {
  items: [
    { id: 'al-1', created_at: '2026-03-17T10:30:00Z', user_name: 'Alex Rivera', event_type: 'MANAGEMENT', action: 'config_change', details: '{"setting": "timezone", "old": "UTC", "new": "EST"}', ip_address: '192.168.1.10' },
    { id: 'al-2', created_at: '2026-03-17T09:15:00Z', user_name: 'Sarah Connor', event_type: 'SECURITY', action: 'login', details: 'Successful login via SSO', ip_address: '10.0.0.1' },
    { id: 'al-3', created_at: '2026-03-16T16:45:00Z', user_name: null, event_type: 'SYSTEM', action: 'backup_complete', details: 'Automated daily backup completed', ip_address: null },
    { id: 'al-4', created_at: '2026-03-16T14:20:00Z', user_name: 'James Miller', event_type: 'MANAGEMENT', action: 'data_export', details: 'Exported analytics report', ip_address: '192.168.1.22' },
    { id: 'al-5', created_at: '2026-03-15T11:00:00Z', user_name: 'Elena Rodriguez', event_type: 'SECURITY', action: 'logout', details: 'User session ended', ip_address: '10.0.0.5' },
  ],
  total: 5, page: 1, page_size: 10,
};

export function AnalyticsPage() {
  const [activeTab, setActiveTab] = useState<'dashboard' | 'audit'>('dashboard');
  const [dateRange] = useState('Last 30 Days');
  const [dashboard, setDashboard] = useState<DashboardData>(MOCK_DASHBOARD);
  const [topUsers, setTopUsers] = useState<TopUser[]>(MOCK_TOP_USERS);
  const [auditLogs, setAuditLogs] = useState<PaginatedAuditLogs>(MOCK_LOGS);
  const [auditPage, setAuditPage] = useState(1);
  const [auditFilters, setAuditFilters] = useState<AuditFilters>({});

  useEffect(() => {
    fetchDashboard()
      .then(setDashboard)
      .catch(() => { /* use mock */ });
    apiFetchTopUsers()
      .then(setTopUsers)
      .catch(() => { /* use mock */ });
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
      /* keep mock data */
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

  const handleExportReport = useCallback(() => {
    window.open('/api/v1/analytics/export', '_blank');
  }, []);

  const handleExportAudit = useCallback(() => {
    window.open('/api/v1/analytics/audit-logs/export', '_blank');
  }, []);

  return (
    <div className="max-w-7xl mx-auto">
      <div className="flex flex-col gap-6 mb-8">
        <div className="flex justify-between items-end">
          <div>
            <h2 className="text-[32px] font-bold tracking-tight text-slate-900">Analytics &amp; Audit Logs</h2>
            <p className="text-slate-500 mt-1">Monitor platform engagement and system integrity.</p>
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
            Audit Log
          </button>
        </div>
      </div>

      {activeTab === 'dashboard' ? (
        <>
          <MetricCards metrics={dashboard.metrics} />
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
            <StageChart data={dashboard.stage_distribution} />
            <TemplateUsageChart data={dashboard.template_usage} />
          </div>
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <TimelineChart data={dashboard.evaluations_timeline} />
            <TopUsersTable users={topUsers} />
          </div>
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
