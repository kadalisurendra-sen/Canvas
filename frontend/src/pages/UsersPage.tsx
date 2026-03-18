import React, { useCallback, useEffect, useState } from 'react';
import type { User, UserListResponse } from '../types/user';
import type { UserRole, UserStatusType } from '../types/user';
import { fetchUsers, updateUser, deactivateUser } from '../services/userService';
import { InviteUserModal } from '../components/users/InviteUserModal';
import { DeactivateModal } from '../components/users/DeactivateModal';

const PAGE_SIZE = 6;

function getInitials(name: string): string {
  return name
    .split(' ')
    .map((n) => n.charAt(0))
    .join('')
    .toUpperCase()
    .slice(0, 2);
}

function StatusBadge({ status }: { status: UserStatusType }) {
  if (status === 'active') {
    return (
      <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-accent/20 text-green-800 border border-accent/50 uppercase">
        Active
      </span>
    );
  }
  if (status === 'invited') {
    return (
      <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-gray-200 text-slate-600 border border-slate-300 uppercase">
        Invited
      </span>
    );
  }
  return (
    <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-slate-200 text-slate-500 border border-slate-300 uppercase">
      Deactivated
    </span>
  );
}

export function UsersPage() {
  const [data, setData] = useState<UserListResponse | null>(null);
  const [search, setSearch] = useState('');
  const [roleFilter, setRoleFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [page, setPage] = useState(1);
  const [showInvite, setShowInvite] = useState(false);
  const [deactivateTarget, setDeactivateTarget] = useState<User | null>(null);
  const [loading, setLoading] = useState(false);

  const loadUsers = useCallback(async () => {
    setLoading(true);
    try {
      const result = await fetchUsers({
        search,
        role: roleFilter,
        status: statusFilter,
        page,
        page_size: PAGE_SIZE,
      });
      setData(result);
    } catch {
      // API not available, use empty data
      setData({
        users: [], total: 0, page: 1, page_size: PAGE_SIZE, total_pages: 1,
      });
    } finally {
      setLoading(false);
    }
  }, [search, roleFilter, statusFilter, page]);

  useEffect(() => {
    const timer = setTimeout(loadUsers, 300);
    return () => clearTimeout(timer);
  }, [loadUsers]);

  const handleRoleChange = async (userId: string, newRole: UserRole) => {
    try {
      await updateUser(userId, { role: newRole });
      await loadUsers();
    } catch {
      // handle error
    }
  };

  const handleDeactivate = async () => {
    if (!deactivateTarget) return;
    try {
      await deactivateUser(deactivateTarget.id);
      setDeactivateTarget(null);
      await loadUsers();
    } catch {
      // handle error
    }
  };

  const users = data?.users ?? [];
  const total = data?.total ?? 0;
  const totalPages = data?.total_pages ?? 1;
  const startIdx = (page - 1) * PAGE_SIZE + 1;
  const endIdx = Math.min(page * PAGE_SIZE, total);

  return (
    <div className="max-w-7xl mx-auto">
      {/* Page Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-8">
        <div>
          <h2 className="text-2xl font-bold text-slate-900 tracking-tight">User Management</h2>
          <p className="text-slate-500 text-sm mt-1">
            Manage users and roles, and monitor user activity across all tenants.
          </p>
        </div>
        <button
          onClick={() => setShowInvite(true)}
          className="flex items-center gap-2 bg-primary hover:bg-primary/90 text-white font-bold px-5 py-2.5 rounded-lg shadow-sm transition-all active:scale-95"
        >
          <span className="material-symbols-outlined">person_add</span>
          Invite User
        </button>
      </div>

      {/* Table Card */}
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
        {/* Filters */}
        <div className="p-4 border-b border-slate-100 bg-white">
          <div className="flex flex-wrap items-center gap-3">
            <div className="flex-1 min-w-[280px]">
              <div className="relative">
                <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 text-lg">
                  search
                </span>
                <input
                  className="w-full pl-10 pr-4 py-2 bg-slate-50 border border-slate-200 rounded-lg focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all text-sm outline-none"
                  placeholder="Search by name or email..."
                  type="text"
                  value={search}
                  onChange={(e) => { setSearch(e.target.value); setPage(1); }}
                />
              </div>
            </div>
            <div className="flex items-center gap-2">
              <select
                className="text-sm border-gray-300 bg-white rounded-lg px-3 py-2 pr-8 focus:ring-primary focus:border-primary border"
                value={roleFilter}
                onChange={(e) => { setRoleFilter(e.target.value); setPage(1); }}
              >
                <option value="">All Roles</option>
                <option value="admin">Admin</option>
                <option value="contributor">Contributor</option>
                <option value="viewer">Viewer</option>
              </select>
              <select
                className="text-sm border-gray-300 bg-white rounded-lg px-3 py-2 pr-8 focus:ring-primary focus:border-primary border"
                value={statusFilter}
                onChange={(e) => { setStatusFilter(e.target.value); setPage(1); }}
              >
                <option value="">All Status</option>
                <option value="active">Active</option>
                <option value="invited">Invited</option>
                <option value="deactivated">Deactivated</option>
              </select>
            </div>
          </div>
        </div>

        {/* Table */}
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-sidebar text-white uppercase text-[11px] font-bold tracking-widest h-12">
                <th className="px-6 py-0 w-12">
                  <input
                    className="rounded border-white/20 bg-white/10 text-primary focus:ring-primary"
                    type="checkbox"
                  />
                </th>
                <th className="px-6 py-0">Name</th>
                <th className="px-6 py-0">Email</th>
                <th className="px-6 py-0">Role</th>
                <th className="px-6 py-0">Status</th>
                <th className="px-6 py-0">Last Login</th>
                <th className="px-6 py-0 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {users.map((user, idx) => {
                const isDeactivated = user.status === 'deactivated';
                const rowBg = idx % 2 === 0 ? 'bg-white' : 'bg-slate-50';
                const hoverBg = idx % 2 === 0 ? 'hover:bg-slate-50' : 'hover:bg-slate-100';
                const textColor = isDeactivated ? 'text-slate-400' : '';
                const avatarBg = idx % 2 === 0 ? 'bg-slate-100' : 'bg-white';
                return (
                  <tr key={user.id} className={`${rowBg} ${hoverBg} transition-colors h-12`}>
                    <td className="px-6 py-0">
                      <input
                        className="rounded border-slate-300 text-primary focus:ring-primary"
                        type="checkbox"
                      />
                    </td>
                    <td className="px-6 py-0">
                      <div className="flex items-center gap-3">
                        <div
                          className={`size-10 rounded-full ${avatarBg} flex items-center justify-center font-bold text-xs border border-slate-200 ${
                            isDeactivated ? 'text-slate-400' : 'text-sidebar'
                          }`}
                        >
                          {getInitials(user.name)}
                        </div>
                        <span className={`font-semibold ${isDeactivated ? 'text-slate-400' : 'text-slate-800'}`}>
                          {user.name}
                        </span>
                      </div>
                    </td>
                    <td className={`px-6 py-0 text-sm ${isDeactivated ? 'text-slate-400 italic' : 'text-slate-600'}`}>
                      {user.email}
                    </td>
                    <td className="px-6 py-0">
                      <div className={`flex items-center gap-1.5 text-sm ${textColor || 'text-slate-700'}`}>
                        <select
                          className="text-sm border-gray-300 bg-white rounded-lg px-2 py-1 focus:ring-primary focus:border-primary border"
                          value={user.role}
                          disabled={isDeactivated}
                          onChange={(e) => handleRoleChange(user.id, e.target.value as UserRole)}
                        >
                          <option value="admin">Admin</option>
                          <option value="contributor">Contributor</option>
                          <option value="viewer">Viewer</option>
                        </select>
                      </div>
                    </td>
                    <td className="px-6 py-0">
                      <StatusBadge status={user.status} />
                    </td>
                    <td className={`px-6 py-0 text-sm ${
                      user.status === 'invited'
                        ? 'text-slate-400 italic'
                        : isDeactivated
                          ? 'text-slate-400'
                          : 'text-slate-500'
                    }`}>
                      {user.status === 'invited' ? 'Pending...' : user.last_login || '-'}
                    </td>
                    <td className="px-6 py-0 text-right">
                      <div className="flex justify-end gap-3 text-primary">
                        <button className="hover:opacity-80 transition-colors">
                          <span className="material-symbols-outlined text-[20px]">edit</span>
                        </button>
                        <button
                          className="hover:opacity-80 transition-colors text-red-500"
                          onClick={() => setDeactivateTarget(user)}
                        >
                          <span className="material-symbols-outlined text-[20px]">delete</span>
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })}
              {users.length === 0 && !loading && (
                <tr>
                  <td colSpan={7} className="px-6 py-8 text-center text-slate-400 text-sm">
                    No users found.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        <div className="p-4 border-t border-slate-100 bg-white flex flex-col sm:flex-row items-center justify-between gap-4">
          <p className="text-sm text-slate-500">
            Showing <span className="font-semibold text-slate-900">{total > 0 ? startIdx : 0}-{endIdx}</span> of{' '}
            <span className="font-semibold text-slate-900">{total}</span> users
          </p>
          <div className="flex items-center gap-1">
            <button
              className="p-2 rounded hover:bg-slate-100 text-slate-400 disabled:opacity-30"
              disabled={page <= 1}
              onClick={() => setPage(page - 1)}
            >
              <span className="material-symbols-outlined text-xl">chevron_left</span>
            </button>
            {Array.from({ length: Math.min(totalPages, 4) }, (_, i) => i + 1).map((p) => (
              <button
                key={p}
                className={`w-8 h-8 flex items-center justify-center rounded text-sm ${
                  p === page
                    ? 'bg-sidebar text-white font-bold'
                    : 'hover:bg-slate-100 text-slate-600'
                }`}
                onClick={() => setPage(p)}
              >
                {p}
              </button>
            ))}
            <button
              className="p-2 rounded hover:bg-slate-100 text-slate-600 disabled:opacity-30"
              disabled={page >= totalPages}
              onClick={() => setPage(page + 1)}
            >
              <span className="material-symbols-outlined text-xl">chevron_right</span>
            </button>
          </div>
        </div>
      </div>

      {/* Modals */}
      {showInvite && (
        <InviteUserModal
          onClose={() => setShowInvite(false)}
          onSuccess={() => { setShowInvite(false); loadUsers(); }}
        />
      )}
      {deactivateTarget && (
        <DeactivateModal
          userName={deactivateTarget.name}
          onClose={() => setDeactivateTarget(null)}
          onConfirm={handleDeactivate}
        />
      )}
    </div>
  );
}
