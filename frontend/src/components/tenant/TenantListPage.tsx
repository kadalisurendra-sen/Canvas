import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { fetchAllTenants, deleteTenant, type TenantListItem } from '../../services/tenantService';

const PLATFORM_SLUG = 'platform';

export function TenantListPage() {
  const [tenants, setTenants] = useState<TenantListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [deleteTarget, setDeleteTarget] = useState<TenantListItem | null>(null);
  const [deleting, setDeleting] = useState(false);
  const [deleteError, setDeleteError] = useState('');
  const navigate = useNavigate();

  const loadTenants = () => {
    setLoading(true);
    fetchAllTenants()
      .then(setTenants)
      .catch(() => {})
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadTenants();
  }, []);

  const handleDelete = async () => {
    if (!deleteTarget) return;
    setDeleting(true);
    setDeleteError('');
    try {
      await deleteTenant(deleteTarget.id);
      setDeleteTarget(null);
      loadTenants();
    } catch (err: unknown) {
      setDeleteError(err instanceof Error ? err.message : 'Delete failed');
    } finally {
      setDeleting(false);
    }
  };

  const filtered = tenants.filter(
    (t) =>
      t.name.toLowerCase().includes(search.toLowerCase()) ||
      t.slug.toLowerCase().includes(search.toLowerCase())
  );

  const statusBadge = (isActive: boolean) => {
    if (isActive) {
      return (
        <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
          Active
        </span>
      );
    }
    return (
      <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-red-50 text-red-600">
        <span className="w-1.5 h-1.5 rounded-full bg-red-500" />
        Suspended
      </span>
    );
  };

  return (
    <div className="flex-1 flex flex-col">
      <div className="px-10 pt-10 pb-6 flex items-center justify-between">
        <div>
          <h2 className="text-[32px] font-bold text-[#1E2345]">Tenant Settings</h2>
          <p className="text-sm text-[#7D8494] mt-1">
            Manage all tenant organizations on the platform
          </p>
        </div>
        <button className="h-10 px-5 bg-primary text-white text-sm font-semibold rounded-lg hover:bg-primary-600 transition-colors flex items-center gap-2">
          <span className="material-symbols-outlined text-lg">add</span>
          Add New Tenant
        </button>
      </div>

      {/* Search and filters */}
      <div className="px-10 pb-4 flex items-center gap-3">
        <div className="relative flex-1 max-w-md">
          <span className="absolute left-3 top-1/2 -translate-y-1/2 material-symbols-outlined text-gray-400 text-lg">
            search
          </span>
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search tenants..."
            className="w-full h-10 pl-10 pr-4 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary/50"
          />
        </div>
        <button className="h-10 px-4 border border-gray-200 rounded-lg text-sm text-gray-600 hover:bg-gray-50 flex items-center gap-2">
          <span className="material-symbols-outlined text-lg">filter_list</span>
          Filter
        </button>
        <button className="h-10 px-4 border border-gray-200 rounded-lg text-sm text-gray-600 hover:bg-gray-50 flex items-center gap-2">
          <span className="material-symbols-outlined text-lg">download</span>
          Export
        </button>
      </div>

      {/* Table */}
      <div className="px-10 pb-10 flex-1">
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
          {loading ? (
            <div className="p-10 text-center text-gray-400">Loading tenants...</div>
          ) : (
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-100">
                  <th className="text-left px-6 py-4 text-xs font-semibold text-[#7D8494] uppercase tracking-wider">
                    Tenant Name
                  </th>
                  <th className="text-left px-6 py-4 text-xs font-semibold text-[#7D8494] uppercase tracking-wider">
                    Realm
                  </th>
                  <th className="text-left px-6 py-4 text-xs font-semibold text-[#7D8494] uppercase tracking-wider">
                    Status
                  </th>
                  <th className="text-left px-6 py-4 text-xs font-semibold text-[#7D8494] uppercase tracking-wider">
                    Created
                  </th>
                  <th className="text-right px-6 py-4 text-xs font-semibold text-[#7D8494] uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody>
                {filtered.map((t) => (
                  <tr
                    key={t.id}
                    className="border-b border-gray-50 hover:bg-gray-50/50 transition-colors"
                  >
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center">
                          <span className="text-primary font-bold text-sm">
                            {t.name.substring(0, 2).toUpperCase()}
                          </span>
                        </div>
                        <div>
                          <p className="text-sm font-semibold text-[#1E2345]">{t.name}</p>
                          <p className="text-xs text-[#7D8494]">{t.slug}</p>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <span className="text-sm text-[#7D8494]">{t.keycloak_realm}</span>
                    </td>
                    <td className="px-6 py-4">{statusBadge(t.is_active)}</td>
                    <td className="px-6 py-4">
                      <span className="text-sm text-[#7D8494]">
                        {new Date(t.created_at).toLocaleDateString('en-US', {
                          month: 'short',
                          day: 'numeric',
                          year: 'numeric',
                        })}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-right">
                      <div className="inline-flex items-center gap-1">
                        <button
                          onClick={() => navigate(`/settings/${t.id}`)}
                          className="inline-flex items-center gap-1.5 px-4 py-2 text-sm font-semibold text-primary hover:bg-primary/5 rounded-lg transition-colors"
                        >
                          Manage
                          <span className="material-symbols-outlined text-base">chevron_right</span>
                        </button>
                        {t.slug !== PLATFORM_SLUG && (
                          <button
                            onClick={() => setDeleteTarget(t)}
                            className="inline-flex items-center gap-1 px-3 py-2 text-sm font-semibold text-red-500 hover:bg-red-50 rounded-lg transition-colors"
                            title="Delete tenant"
                          >
                            <span className="material-symbols-outlined text-lg">delete</span>
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
                {filtered.length === 0 && !loading && (
                  <tr>
                    <td colSpan={5} className="px-6 py-10 text-center text-gray-400 text-sm">
                      No tenants found
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          )}

          {/* Footer */}
          <div className="px-6 py-4 border-t border-gray-100 flex items-center justify-between text-sm text-[#7D8494]">
            <span>
              Showing {filtered.length} of {tenants.length} tenants
            </span>
          </div>
        </div>
      </div>

      {/* Delete Confirmation Modal */}
      {deleteTarget && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
          <div className="bg-white rounded-2xl shadow-xl p-8 max-w-md w-full mx-4">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-12 h-12 rounded-full bg-red-50 flex items-center justify-center">
                <span className="material-symbols-outlined text-red-500 text-2xl">warning</span>
              </div>
              <div>
                <h3 className="text-lg font-bold text-[#1E2345]">Delete Tenant</h3>
                <p className="text-sm text-[#7D8494]">This action cannot be undone</p>
              </div>
            </div>

            <p className="text-sm text-gray-600 mb-2">
              Are you sure you want to delete <strong>{deleteTarget.name}</strong>?
            </p>
            <p className="text-sm text-gray-500 mb-6">
              This will permanently remove the tenant, all its data (templates, master data, audit logs),
              and the database schema <code className="bg-gray-100 px-1 rounded">{deleteTarget.schema_name}</code>.
            </p>

            {deleteError && (
              <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-600 text-sm">
                {deleteError}
              </div>
            )}

            <div className="flex justify-end gap-3">
              <button
                onClick={() => { setDeleteTarget(null); setDeleteError(''); }}
                className="px-5 py-2.5 text-sm font-semibold text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
                disabled={deleting}
              >
                Cancel
              </button>
              <button
                onClick={handleDelete}
                disabled={deleting}
                className="px-5 py-2.5 text-sm font-semibold text-white bg-red-500 hover:bg-red-600 rounded-lg transition-colors disabled:opacity-50"
              >
                {deleting ? 'Deleting...' : 'Delete Tenant'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
