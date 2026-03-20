import React, { useState } from 'react';
import type { PaginatedAuditLogs } from '../../services/analyticsService';

interface AuditLogTabProps {
  logs: PaginatedAuditLogs;
  onFilter: (filters: AuditFilters) => void;
  onPageChange: (page: number) => void;
  onExport: () => void;
}

export interface AuditFilters {
  user_id?: string;
  action?: string;
  event_type?: string;
  from_date?: string;
  to_date?: string;
}

const EVENT_COLORS: Record<string, string> = {
  MANAGEMENT: 'bg-blue-100 text-blue-700',
  TEMPLATE: 'bg-purple-100 text-purple-700',
  DATA: 'bg-emerald-100 text-emerald-700',
  AUTH: 'bg-amber-100 text-amber-700',
  SETTINGS: 'bg-cyan-100 text-cyan-700',
  SYSTEM: 'bg-slate-100 text-slate-600',
  SECURITY: 'bg-orange-100 text-orange-700',
};

export function AuditLogTab({ logs, onFilter, onPageChange, onExport }: AuditLogTabProps) {
  const [actionType, setActionType] = useState('');
  const [eventType, setEventType] = useState('');
  const [expandedId, setExpandedId] = useState<string | null>(null);

  const handleApply = () => {
    onFilter({ action: actionType || undefined, event_type: eventType || undefined });
  };

  const handleClear = () => {
    setActionType('');
    setEventType('');
    onFilter({});
  };

  const hasNext = logs.page * logs.page_size < logs.total;
  const hasPrev = logs.page > 1;

  return (
    <div className="space-y-6">
      {/* Filters */}
      <div className="flex flex-wrap items-end gap-4">
        <div>
          <label className="block text-xs font-semibold text-slate-500 mb-1">Action Type</label>
          <select
            value={actionType}
            onChange={(e) => setActionType(e.target.value)}
            className="px-3 py-2 border border-slate-200 rounded-md text-sm min-w-[180px]"
          >
            <option value="">All Actions</option>
            <option value="user_login">Login</option>
            <option value="user_logout">Logout</option>
            <option value="user_invited">User Invited</option>
            <option value="template_created">Template Created</option>
            <option value="template_published">Template Published</option>
            <option value="csv_imported">CSV Import</option>
          </select>
        </div>
        <div>
          <label className="block text-xs font-semibold text-slate-500 mb-1">Event Type</label>
          <select
            value={eventType}
            onChange={(e) => setEventType(e.target.value)}
            className="px-3 py-2 border border-slate-200 rounded-md text-sm min-w-[180px]"
          >
            <option value="">All Events</option>
            <option value="MANAGEMENT">Management</option>
            <option value="TEMPLATE">Template</option>
            <option value="DATA">Data</option>
            <option value="AUTH">Auth</option>
            <option value="SETTINGS">Settings</option>
            <option value="SYSTEM">System</option>
            <option value="SECURITY">Security</option>
          </select>
        </div>
        <button onClick={handleApply} className="px-4 py-2 bg-[#5F2CFF] text-white rounded-md text-sm font-semibold hover:bg-[#5F2CFF]/90">
          Apply Filters
        </button>
        <button onClick={handleClear} className="px-4 py-2 border border-slate-200 text-slate-600 rounded-md text-sm font-semibold hover:bg-slate-50">
          Clear
        </button>
        <div className="ml-auto">
          <button onClick={onExport} className="flex items-center gap-2 px-4 py-2 border border-slate-200 text-slate-700 rounded-md text-sm font-semibold hover:bg-slate-50">
            <span className="material-symbols-outlined text-lg">download</span>Export Log
          </button>
        </div>
      </div>

      {/* Table */}
      <div className="bg-white rounded-xl border border-slate-200 overflow-hidden shadow-sm">
        <table className="w-full text-left">
          <thead className="bg-[#1E2345] text-white">
            <tr className="text-sm font-semibold tracking-wide">
              <th className="py-3 px-4">Date/Time</th>
              <th className="py-3 px-4">Actor</th>
              <th className="py-3 px-4">Event</th>
              <th className="py-3 px-4">Details</th>
            </tr>
          </thead>
          <tbody>
            {logs.items.map((entry, idx) => (
              <React.Fragment key={entry.id}>
                <tr
                  className={`cursor-pointer hover:bg-slate-50 ${idx % 2 === 0 ? 'bg-white' : 'bg-[#F9FAFB]'}`}
                  onClick={() => setExpandedId(expandedId === entry.id ? null : entry.id)}
                >
                  <td className="py-3 px-4 text-sm text-slate-600 border-b border-slate-100">
                    {new Date(entry.created_at).toLocaleString()}
                  </td>
                  <td className="py-3 px-4 border-b border-slate-100">
                    <div className="flex items-center gap-2">
                      <div className="w-7 h-7 rounded-full bg-slate-200 flex items-center justify-center">
                        <span className="text-[10px] font-bold text-slate-600">
                          {(entry.user_name || 'S')[0].toUpperCase()}
                        </span>
                      </div>
                      <span className="text-sm font-medium text-slate-700">{entry.user_name || 'System'}</span>
                    </div>
                  </td>
                  <td className="py-3 px-4 border-b border-slate-100">
                    <span className={`px-2 py-1 rounded text-xs font-bold ${EVENT_COLORS[entry.event_type] || 'bg-slate-100 text-slate-600'}`}>
                      {entry.event_type}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-sm text-slate-600 border-b border-slate-100 truncate max-w-xs">
                    {entry.action}{entry.details ? ` - ${entry.details.substring(0, 60)}...` : ''}
                  </td>
                </tr>
                {expandedId === entry.id && entry.details && (
                  <tr className="bg-slate-50">
                    <td colSpan={4} className="px-4 py-3 border-b border-slate-100">
                      <pre className="text-xs text-slate-600 whitespace-pre-wrap">{entry.details}</pre>
                    </td>
                  </tr>
                )}
              </React.Fragment>
            ))}
            {logs.items.length === 0 && (
              <tr><td colSpan={4} className="py-8 text-center text-sm text-slate-400">No audit log entries found.</td></tr>
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      <div className="flex items-center justify-between">
        <span className="text-xs text-slate-500">
          Showing {Math.min((logs.page - 1) * logs.page_size + 1, logs.total)}-{Math.min(logs.page * logs.page_size, logs.total)} of {logs.total} results
        </span>
        <div className="flex items-center gap-2">
          <button disabled={!hasPrev} onClick={() => onPageChange(logs.page - 1)} className={`p-1 rounded border border-slate-200 bg-white ${hasPrev ? 'text-slate-600 hover:bg-slate-50' : 'text-slate-300 cursor-not-allowed'}`}>
            <span className="material-symbols-outlined text-[18px]">chevron_left</span>
          </button>
          <span className="text-xs font-bold px-2">{logs.page}</span>
          <button disabled={!hasNext} onClick={() => onPageChange(logs.page + 1)} className={`p-1 rounded border border-slate-200 bg-white ${hasNext ? 'text-slate-600 hover:bg-slate-50' : 'text-slate-300 cursor-not-allowed'}`}>
            <span className="material-symbols-outlined text-[18px]">chevron_right</span>
          </button>
        </div>
      </div>
    </div>
  );
}
