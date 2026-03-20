import React, { useCallback, useEffect, useState } from 'react';
import type { User, UserListResponse } from '../types/user';
import type { UserRole } from '../types/user';
import { fetchUsers, updateUser, deactivateUser, deleteUser } from '../services/userService';
import { InviteUserModal } from '../components/users/InviteUserModal';

const PAGE_SIZE = 6;

function getInitials(name: string): string {
  return name
    .split(' ')
    .map((n) => n.charAt(0))
    .join('')
    .toUpperCase()
    .slice(0, 2);
}

function StatusBadge({ status }: { status: string }) {
  if (status === 'active') {
    return (
      <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-accent/20 text-green-800 border border-accent/50 uppercase">
        Active
      </span>
    );
  }
  return (
    <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-slate-200 text-slate-500 border border-slate-300 uppercase">
      Deactivated
    </span>
  );
}

function RoleBadge({ role }: { role: string }) {
  const colors: Record<string, string> = {
    admin: 'bg-purple-50 text-purple-700 border-purple-200',
    contributor: 'bg-blue-50 text-blue-700 border-blue-200',
    viewer: 'bg-slate-50 text-slate-600 border-slate-200',
  };
  const cls = colors[role] || colors.viewer;
  return (
    <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold border uppercase ${cls}`}>
      {role}
    </span>
  );
}

/* ── Toast ── */
interface Toast {
  id: number;
  message: string;
  type: 'success' | 'error';
}

function ToastContainer({ toasts, onDismiss }: { toasts: Toast[]; onDismiss: (id: number) => void }) {
  if (toasts.length === 0) return null;
  return (
    <div className="fixed top-6 right-6 z-[100] flex flex-col gap-2">
      {toasts.map((t) => (
        <div
          key={t.id}
          className={`flex items-center gap-3 px-4 py-3 rounded-lg shadow-lg text-sm font-medium animate-slide-in ${
            t.type === 'success'
              ? 'bg-green-600 text-white'
              : 'bg-red-600 text-white'
          }`}
        >
          <span className="material-symbols-outlined text-lg">
            {t.type === 'success' ? 'check_circle' : 'error'}
          </span>
          {t.message}
          <button onClick={() => onDismiss(t.id)} className="ml-2 opacity-70 hover:opacity-100">
            <span className="material-symbols-outlined text-base">close</span>
          </button>
        </div>
      ))}
    </div>
  );
}

/* ── Skeleton rows ── */
function SkeletonRows({ count }: { count: number }) {
  return (
    <>
      {Array.from({ length: count }).map((_, i) => (
        <tr key={i} className={i % 2 === 0 ? 'bg-white' : 'bg-slate-50'}>
          <td className="px-6 py-3"><div className="w-4 h-4 bg-slate-200 rounded animate-pulse" /></td>
          <td className="px-6 py-3">
            <div className="flex items-center gap-3">
              <div className="size-10 rounded-full bg-slate-200 animate-pulse" />
              <div className="w-28 h-4 bg-slate-200 rounded animate-pulse" />
            </div>
          </td>
          <td className="px-6 py-3"><div className="w-40 h-4 bg-slate-200 rounded animate-pulse" /></td>
          <td className="px-6 py-3"><div className="w-20 h-5 bg-slate-200 rounded-full animate-pulse" /></td>
          <td className="px-6 py-3"><div className="w-16 h-5 bg-slate-200 rounded-full animate-pulse" /></td>
          <td className="px-6 py-3"><div className="w-16 h-4 bg-slate-200 rounded animate-pulse ml-auto" /></td>
        </tr>
      ))}
    </>
  );
}

/* ── Confirm Modal (reusable) ── */
function ConfirmModal({
  icon,
  iconBg,
  title,
  message,
  confirmLabel,
  confirmColor,
  onClose,
  onConfirm,
}: {
  icon: string;
  iconBg: string;
  title: string;
  message: React.ReactNode;
  confirmLabel: string;
  confirmColor: string;
  onClose: () => void;
  onConfirm: () => void;
}) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <div className="bg-white rounded-xl shadow-xl w-full max-w-sm mx-4 p-6">
        <div className="flex items-center gap-3 mb-4">
          <div className={`size-10 rounded-full ${iconBg} flex items-center justify-center`}>
            <span className="material-symbols-outlined text-xl">{icon}</span>
          </div>
          <h3 className="text-lg font-bold text-slate-900">{title}</h3>
        </div>
        <div className="text-sm text-slate-600 mb-6">{message}</div>
        <div className="flex justify-end gap-3">
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm font-medium text-slate-600 hover:text-slate-800 transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={onConfirm}
            className={`px-5 py-2 text-white text-sm font-bold rounded-lg transition-all ${confirmColor}`}
          >
            {confirmLabel}
          </button>
        </div>
      </div>
    </div>
  );
}

/* ── Main Page ── */
export function UsersPage() {
  const [data, setData] = useState<UserListResponse | null>(null);
  const [search, setSearch] = useState('');
  const [roleFilter, setRoleFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [page, setPage] = useState(1);
  const [showInvite, setShowInvite] = useState(false);
  const [loading, setLoading] = useState(true);
  const [toasts, setToasts] = useState<Toast[]>([]);
  let toastId = 0;

  // Selection
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());

  // Modals
  const [deactivateTarget, setDeactivateTarget] = useState<User | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<User | null>(null);
  const [roleChangeTarget, setRoleChangeTarget] = useState<{ user: User; newRole: UserRole } | null>(null);
  const [reactivateTarget, setReactivateTarget] = useState<User | null>(null);
  const [bulkDeactivateConfirm, setBulkDeactivateConfirm] = useState(false);
  const [bulkDeleteConfirm, setBulkDeleteConfirm] = useState(false);
  const [bulkReactivateConfirm, setBulkReactivateConfirm] = useState(false);

  const addToast = useCallback((message: string, type: 'success' | 'error') => {
    const id = Date.now() + Math.random();
    setToasts((prev) => [...prev, { id, message, type }]);
    setTimeout(() => setToasts((prev) => prev.filter((t) => t.id !== id)), 4000);
  }, []);

  const dismissToast = useCallback((id: number) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

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
      setData({ users: [], total: 0, page: 1, page_size: PAGE_SIZE, total_pages: 1 });
    } finally {
      setLoading(false);
    }
  }, [search, roleFilter, statusFilter, page]);

  useEffect(() => {
    const timer = setTimeout(loadUsers, 300);
    return () => clearTimeout(timer);
  }, [loadUsers]);

  // Clear selection when filters/page change
  useEffect(() => {
    setSelectedIds(new Set());
  }, [search, roleFilter, statusFilter, page]);

  const users = data?.users ?? [];
  const total = data?.total ?? 0;
  const totalPages = data?.total_pages ?? 1;
  const startIdx = (page - 1) * PAGE_SIZE + 1;
  const endIdx = Math.min(page * PAGE_SIZE, total);

  // Summary counts (overall, from API)
  const activeCount = data?.active_count ?? 0;
  const deactivatedCount = data?.deactivated_count ?? 0;
  const totalOverall = activeCount + deactivatedCount;

  // Selection helpers
  const allSelected = users.length > 0 && users.every((u) => selectedIds.has(u.id));
  const someSelected = selectedIds.size > 0;
  const selectedUsers = users.filter((u) => selectedIds.has(u.id));
  const selectedActiveUsers = selectedUsers.filter((u) => u.status === 'active');
  const selectedDeactivatedUsers = selectedUsers.filter((u) => u.status !== 'active');

  const toggleAll = () => {
    if (allSelected) {
      setSelectedIds(new Set());
    } else {
      setSelectedIds(new Set(users.map((u) => u.id)));
    }
  };

  const toggleOne = (id: string) => {
    setSelectedIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  /* ── Handlers ── */
  const handleRoleChange = async () => {
    if (!roleChangeTarget) return;
    try {
      await updateUser(roleChangeTarget.user.id, { role: roleChangeTarget.newRole });
      addToast(`Role updated to ${roleChangeTarget.newRole}`, 'success');
      await loadUsers();
    } catch {
      addToast('Failed to update role', 'error');
    }
    setRoleChangeTarget(null);
  };

  const handleDeactivate = async () => {
    if (!deactivateTarget) return;
    try {
      await deactivateUser(deactivateTarget.id);
      addToast(`${deactivateTarget.name} deactivated`, 'success');
      setSelectedIds((prev) => { const n = new Set(prev); n.delete(deactivateTarget.id); return n; });
      await loadUsers();
    } catch {
      addToast('Failed to deactivate user', 'error');
    }
    setDeactivateTarget(null);
  };

  const handleReactivate = async () => {
    if (!reactivateTarget) return;
    try {
      await updateUser(reactivateTarget.id, { status: 'active' as any });
      addToast(`${reactivateTarget.name} reactivated`, 'success');
      await loadUsers();
    } catch {
      addToast('Failed to reactivate user', 'error');
    }
    setReactivateTarget(null);
  };

  const handleDelete = async () => {
    if (!deleteTarget) return;
    try {
      await deleteUser(deleteTarget.id);
      addToast(`${deleteTarget.name} deleted permanently`, 'success');
      setSelectedIds((prev) => { const n = new Set(prev); n.delete(deleteTarget.id); return n; });
      await loadUsers();
    } catch {
      addToast('Failed to delete user', 'error');
    }
    setDeleteTarget(null);
  };

  const handleBulkDeactivate = async () => {
    setBulkDeactivateConfirm(false);
    const results = await Promise.allSettled(selectedActiveUsers.map((u) => deactivateUser(u.id)));
    const count = results.filter((r) => r.status === 'fulfilled').length;
    addToast(`${count} user(s) deactivated`, count > 0 ? 'success' : 'error');
    setSelectedIds(new Set());
    await loadUsers();
  };

  const handleBulkDelete = async () => {
    setBulkDeleteConfirm(false);
    const results = await Promise.allSettled(selectedDeactivatedUsers.map((u) => deleteUser(u.id)));
    const count = results.filter((r) => r.status === 'fulfilled').length;
    if (count > 0) addToast(`${count} user(s) deleted permanently`, 'success');
    else addToast('Failed to delete users', 'error');
    setSelectedIds(new Set());
    await loadUsers();
  };

  const handleBulkReactivate = async () => {
    setBulkReactivateConfirm(false);
    const results = await Promise.allSettled(selectedDeactivatedUsers.map((u) => updateUser(u.id, { status: 'active' as any })));
    const count = results.filter((r) => r.status === 'fulfilled').length;
    if (count > 0) addToast(`${count} user(s) reactivated`, 'success');
    else addToast('Failed to reactivate users', 'error');
    setSelectedIds(new Set());
    await loadUsers();
  };

  return (
    <div className="max-w-7xl mx-auto">
      <ToastContainer toasts={toasts} onDismiss={dismissToast} />

      {/* Page Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-6">
        <div>
          <h2 className="text-2xl font-bold text-slate-900 tracking-tight">User Management</h2>
          <p className="text-slate-500 text-sm mt-1">
            Manage users, roles, and access across your organization.
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

      {/* Summary Cards */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="bg-white rounded-xl border border-slate-200 px-5 py-4 flex items-center gap-4">
          <div className="size-10 rounded-lg bg-primary/10 flex items-center justify-center">
            <span className="material-symbols-outlined text-primary">group</span>
          </div>
          <div>
            <p className="text-2xl font-bold text-slate-900">{totalOverall}</p>
            <p className="text-xs text-slate-500">Total Users</p>
          </div>
        </div>
        <div className="bg-white rounded-xl border border-slate-200 px-5 py-4 flex items-center gap-4">
          <div className="size-10 rounded-lg bg-green-50 flex items-center justify-center">
            <span className="material-symbols-outlined text-green-600">check_circle</span>
          </div>
          <div>
            <p className="text-2xl font-bold text-slate-900">{activeCount}</p>
            <p className="text-xs text-slate-500">Active</p>
          </div>
        </div>
        <div className="bg-white rounded-xl border border-slate-200 px-5 py-4 flex items-center gap-4">
          <div className="size-10 rounded-lg bg-slate-100 flex items-center justify-center">
            <span className="material-symbols-outlined text-slate-400">person_off</span>
          </div>
          <div>
            <p className="text-2xl font-bold text-slate-900">{deactivatedCount}</p>
            <p className="text-xs text-slate-500">Deactivated</p>
          </div>
        </div>
      </div>

      {/* Table Card */}
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
        {/* Filters + Bulk Actions */}
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
              {someSelected && (
                <div className="flex items-center gap-2 mr-2">
                  <span className="text-xs font-medium text-slate-500">{selectedIds.size} selected</span>
                  {selectedActiveUsers.length > 0 && (
                    <button
                      onClick={() => setBulkDeactivateConfirm(true)}
                      className="flex items-center gap-1 px-3 py-1.5 text-xs font-bold text-amber-700 bg-amber-50 border border-amber-200 rounded-lg hover:bg-amber-100 transition-colors"
                    >
                      <span className="material-symbols-outlined text-sm">person_off</span>
                      Deactivate ({selectedActiveUsers.length})
                    </button>
                  )}
                  {selectedDeactivatedUsers.length > 0 && (
                    <>
                      <button
                        onClick={() => setBulkReactivateConfirm(true)}
                        className="flex items-center gap-1 px-3 py-1.5 text-xs font-bold text-green-700 bg-green-50 border border-green-200 rounded-lg hover:bg-green-100 transition-colors"
                      >
                        <span className="material-symbols-outlined text-sm">person_add</span>
                        Reactivate ({selectedDeactivatedUsers.length})
                      </button>
                      <button
                        onClick={() => setBulkDeleteConfirm(true)}
                        className="flex items-center gap-1 px-3 py-1.5 text-xs font-bold text-red-700 bg-red-50 border border-red-200 rounded-lg hover:bg-red-100 transition-colors"
                      >
                        <span className="material-symbols-outlined text-sm">delete_forever</span>
                        Delete ({selectedDeactivatedUsers.length})
                      </button>
                    </>
                  )}
                </div>
              )}
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
                    className="rounded border-white/20 bg-white/10 text-primary focus:ring-primary cursor-pointer"
                    type="checkbox"
                    checked={allSelected}
                    onChange={toggleAll}
                  />
                </th>
                <th className="px-6 py-0">Name</th>
                <th className="px-6 py-0">Email</th>
                <th className="px-6 py-0">Role</th>
                <th className="px-6 py-0">Status</th>
                <th className="px-6 py-0 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {loading ? (
                <SkeletonRows count={PAGE_SIZE} />
              ) : users.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-6 py-16 text-center">
                    <div className="flex flex-col items-center gap-3">
                      <div className="size-16 rounded-full bg-slate-100 flex items-center justify-center">
                        <span className="material-symbols-outlined text-3xl text-slate-300">group_off</span>
                      </div>
                      <p className="text-slate-500 text-sm font-medium">No users found</p>
                      <p className="text-slate-400 text-xs">Try adjusting your search or filters</p>
                    </div>
                  </td>
                </tr>
              ) : (
                users.map((user, idx) => {
                  const isDeactivated = user.status !== 'active';
                  const isSelected = selectedIds.has(user.id);
                  const rowBg = isSelected
                    ? 'bg-primary/5'
                    : idx % 2 === 0 ? 'bg-white' : 'bg-slate-50';
                  const hoverBg = 'hover:bg-primary/5';
                  const avatarBg = isDeactivated
                    ? 'bg-slate-100'
                    : idx % 2 === 0 ? 'bg-slate-100' : 'bg-white';
                  return (
                    <tr key={user.id} className={`${rowBg} ${hoverBg} transition-colors h-12`}>
                      <td className="px-6 py-0">
                        <input
                          className="rounded border-slate-300 text-primary focus:ring-primary cursor-pointer"
                          type="checkbox"
                          checked={isSelected}
                          onChange={() => toggleOne(user.id)}
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
                      <td className={`px-6 py-0 text-sm ${isDeactivated ? 'text-slate-400' : 'text-slate-600'}`}>
                        {user.email}
                      </td>
                      <td className="px-6 py-0">
                        {isDeactivated ? (
                          <RoleBadge role={user.role} />
                        ) : (
                          <select
                            className="text-xs font-bold border-gray-200 bg-white rounded-lg px-2 py-1 focus:ring-primary focus:border-primary border cursor-pointer"
                            value={user.role}
                            onChange={(e) =>
                              setRoleChangeTarget({ user, newRole: e.target.value as UserRole })
                            }
                          >
                            <option value="admin">Admin</option>
                            <option value="contributor">Contributor</option>
                            <option value="viewer">Viewer</option>
                          </select>
                        )}
                      </td>
                      <td className="px-6 py-0">
                        <StatusBadge status={user.status} />
                      </td>
                      <td className="px-6 py-0 text-right">
                        <div className="flex justify-end gap-2">
                          {isDeactivated ? (
                            <>
                              <button
                                className="p-1.5 rounded-lg hover:bg-green-50 text-green-600 transition-colors"
                                title="Reactivate user"
                                onClick={() => setReactivateTarget(user)}
                              >
                                <span className="material-symbols-outlined text-[20px]">person_add</span>
                              </button>
                              <button
                                className="p-1.5 rounded-lg hover:bg-red-50 text-red-500 transition-colors"
                                title="Delete permanently"
                                onClick={() => setDeleteTarget(user)}
                              >
                                <span className="material-symbols-outlined text-[20px]">delete_forever</span>
                              </button>
                            </>
                          ) : (
                            <button
                              className="p-1.5 rounded-lg hover:bg-red-50 text-red-500 transition-colors"
                              title="Deactivate user"
                              onClick={() => setDeactivateTarget(user)}
                            >
                              <span className="material-symbols-outlined text-[20px]">person_off</span>
                            </button>
                          )}
                        </div>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        <div className="p-4 border-t border-slate-100 bg-white flex flex-col sm:flex-row items-center justify-between gap-4">
          <p className="text-sm text-slate-500">
            Showing <span className="font-semibold text-slate-900">{total > 0 ? startIdx : 0}–{endIdx}</span> of{' '}
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
            {Array.from({ length: Math.min(totalPages, 5) }, (_, i) => i + 1).map((p) => (
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

      {/* ── Modals ── */}
      {showInvite && (
        <InviteUserModal
          onClose={() => setShowInvite(false)}
          onSuccess={() => {
            setShowInvite(false);
            addToast('User invited successfully', 'success');
            loadUsers();
          }}
        />
      )}

      {deactivateTarget && (
        <ConfirmModal
          icon="person_off"
          iconBg="bg-amber-100 text-amber-600"
          title="Deactivate User"
          message={<>Are you sure you want to deactivate <strong>{deactivateTarget.name}</strong>? They will lose access immediately.</>}
          confirmLabel="Deactivate"
          confirmColor="bg-amber-600 hover:bg-amber-700"
          onClose={() => setDeactivateTarget(null)}
          onConfirm={handleDeactivate}
        />
      )}

      {reactivateTarget && (
        <ConfirmModal
          icon="person_add"
          iconBg="bg-green-100 text-green-600"
          title="Reactivate User"
          message={<>Reactivate <strong>{reactivateTarget.name}</strong>? They will regain access with their previous role.</>}
          confirmLabel="Reactivate"
          confirmColor="bg-green-600 hover:bg-green-700"
          onClose={() => setReactivateTarget(null)}
          onConfirm={handleReactivate}
        />
      )}

      {deleteTarget && (
        <ConfirmModal
          icon="delete_forever"
          iconBg="bg-red-100 text-red-600"
          title="Delete User Permanently"
          message={<>Are you sure you want to permanently delete <strong>{deleteTarget.name}</strong>? This action cannot be undone.</>}
          confirmLabel="Delete Permanently"
          confirmColor="bg-red-600 hover:bg-red-700"
          onClose={() => setDeleteTarget(null)}
          onConfirm={handleDelete}
        />
      )}

      {roleChangeTarget && (
        <ConfirmModal
          icon="swap_horiz"
          iconBg="bg-purple-100 text-purple-600"
          title="Change Role"
          message={
            <>
              Change <strong>{roleChangeTarget.user.name}</strong>'s role from{' '}
              <strong>{roleChangeTarget.user.role}</strong> to{' '}
              <strong>{roleChangeTarget.newRole}</strong>?
            </>
          }
          confirmLabel="Change Role"
          confirmColor="bg-primary hover:bg-primary/90"
          onClose={() => { setRoleChangeTarget(null); loadUsers(); }}
          onConfirm={handleRoleChange}
        />
      )}

      {bulkDeactivateConfirm && (
        <ConfirmModal
          icon="group_off"
          iconBg="bg-amber-100 text-amber-600"
          title="Bulk Deactivate"
          message={<>Deactivate <strong>{selectedActiveUsers.length}</strong> selected user(s)? They will lose access immediately.</>}
          confirmLabel={`Deactivate ${selectedActiveUsers.length} Users`}
          confirmColor="bg-amber-600 hover:bg-amber-700"
          onClose={() => setBulkDeactivateConfirm(false)}
          onConfirm={handleBulkDeactivate}
        />
      )}

      {bulkReactivateConfirm && (
        <ConfirmModal
          icon="group_add"
          iconBg="bg-green-100 text-green-600"
          title="Bulk Reactivate"
          message={<>Reactivate <strong>{selectedDeactivatedUsers.length}</strong> selected user(s)? They will regain access with their previous roles.</>}
          confirmLabel={`Reactivate ${selectedDeactivatedUsers.length} Users`}
          confirmColor="bg-green-600 hover:bg-green-700"
          onClose={() => setBulkReactivateConfirm(false)}
          onConfirm={handleBulkReactivate}
        />
      )}

      {bulkDeleteConfirm && (
        <ConfirmModal
          icon="delete_sweep"
          iconBg="bg-red-100 text-red-600"
          title="Bulk Delete"
          message={<>Permanently delete <strong>{selectedDeactivatedUsers.length}</strong> deactivated user(s)? This cannot be undone.</>}
          confirmLabel={`Delete ${selectedDeactivatedUsers.length} Users`}
          confirmColor="bg-red-600 hover:bg-red-700"
          onClose={() => setBulkDeleteConfirm(false)}
          onConfirm={handleBulkDelete}
        />
      )}
    </div>
  );
}
