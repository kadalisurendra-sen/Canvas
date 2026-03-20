import React, { useCallback, useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { TemplateGrid } from '../components/templates/TemplateGrid';
import { TemplateFilters } from '../components/templates/TemplateFilters';
import { TemplatePagination } from '../components/templates/TemplatePagination';
import { DeleteTemplateModal } from '../components/templates/DeleteTemplateModal';
import { CreateTemplateModal } from '../components/templates/CreateTemplateModal';
import type { TemplateListItem } from '../types/template';
import {
  fetchTemplates,
  deleteTemplate,
  cloneTemplate,
} from '../services/templateService';

const PAGE_SIZE = 6;

export function TemplateManagementPage() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const canEdit = user?.roles.includes('system_admin') || user?.roles.includes('admin');
  const [templates, setTemplates] = useState<TemplateListItem[]>([]);
  const [total, setTotal] = useState(0);
  const [search, setSearch] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [sortMode, setSortMode] = useState('modified');
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [page, setPage] = useState(1);
  const [deleteTarget, setDeleteTarget] = useState<TemplateListItem | null>(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [loading, setLoading] = useState(false);

  const loadTemplates = useCallback(async () => {
    setLoading(true);
    try {
      const result = await fetchTemplates({
        status: statusFilter || undefined,
        category: categoryFilter || undefined,
        search: search || undefined,
        page,
        page_size: PAGE_SIZE,
      });
      // Sort client-side
      let sorted = [...result.items];
      if (sortMode === 'newest') {
        sorted.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());
      } else if (sortMode === 'oldest') {
        sorted.sort((a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime());
      } else {
        sorted.sort((a, b) => new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime());
      }
      setTemplates(sorted);
      setTotal(result.total);
    } catch {
      setTemplates([]);
      setTotal(0);
    } finally {
      setLoading(false);
    }
  }, [search, categoryFilter, statusFilter, sortMode, page]);

  useEffect(() => {
    const timer = setTimeout(loadTemplates, 300);
    return () => clearTimeout(timer);
  }, [loadTemplates]);

  const handleCreate = () => setShowCreateModal(true);

  const handleCreateFromScratch = () => {
    setShowCreateModal(false);
    navigate('/templates/new');
  };

  const handleCloneTemplate = async (templateId: string) => {
    setShowCreateModal(false);
    try {
      const result = await cloneTemplate(templateId);
      navigate(`/templates/${result.id}/edit`);
    } catch {
      navigate('/templates/new');
    }
  };

  const handleEdit = (id: string) => navigate(`/templates/${id}/edit`);
  const handleDelete = (t: TemplateListItem) => setDeleteTarget(t);

  const handleConfirmDelete = async () => {
    if (!deleteTarget) return;
    try {
      await deleteTemplate(deleteTarget.id);
      setDeleteTarget(null);
      await loadTemplates();
    } catch {
      setDeleteTarget(null);
    }
  };

  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE));
  const isViewer = !canEdit;

  if (isViewer) {
    return (
      <div className="flex-1 flex items-center justify-center min-h-[60vh]">
        <div className="text-center max-w-md">
          <div className="w-24 h-24 rounded-full bg-primary/10 flex items-center justify-center mx-auto mb-6">
            <span className="material-symbols-outlined text-5xl text-primary">construction</span>
          </div>
          <h2 className="text-2xl font-bold text-slate-800 mb-3">Under Construction</h2>
          <p className="text-slate-500 text-sm leading-relaxed">
            The contributor and viewer experience is currently being built.
            Please check back soon for access to templates and evaluations.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div>
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-8">
        <div>
          <h1 className="text-[32px] font-bold text-slate-900 tracking-tight">
            Template Management
          </h1>
          <p className="text-slate-500 mt-1">
            Create and manage evaluation templates for the organization
          </p>
        </div>
        {canEdit && (
          <div className="flex gap-3">
            <button
              onClick={handleCreate}
              className="flex items-center gap-2 px-4 py-2 bg-primary text-white font-semibold text-sm rounded-lg hover:shadow-lg hover:bg-primary/90 transition-all"
            >
              <span className="material-symbols-outlined text-sm">add</span>
              Create New Template
            </button>
          </div>
        )}
      </div>

      <TemplateFilters
        search={search}
        onSearchChange={(v) => { setSearch(v); setPage(1); }}
        category={categoryFilter}
        onCategoryChange={(v) => { setCategoryFilter(v); setPage(1); }}
        status={statusFilter}
        onStatusChange={(v) => { setStatusFilter(v); setPage(1); }}
        sort={sortMode}
        onSortChange={(v) => { setSortMode(v); setPage(1); }}
        viewMode={viewMode}
        onViewModeChange={setViewMode}
      />

      {loading ? (
        <div className="text-center py-12 text-slate-400">Loading templates...</div>
      ) : viewMode === 'grid' ? (
        <TemplateGrid
          templates={templates}
          onEdit={canEdit ? handleEdit : undefined}
          onDelete={canEdit ? handleDelete : undefined}
        />
      ) : (
        /* List view */
        <div className="bg-white rounded-xl shadow-sm border border-[#E7E8EB] overflow-hidden">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-100">
                <th className="text-left px-6 py-3 text-xs font-semibold text-gray-500 uppercase">Name</th>
                <th className="text-left px-6 py-3 text-xs font-semibold text-gray-500 uppercase">Category</th>
                <th className="text-left px-6 py-3 text-xs font-semibold text-gray-500 uppercase">Status</th>
                <th className="text-left px-6 py-3 text-xs font-semibold text-gray-500 uppercase">Stages</th>
                <th className="text-left px-6 py-3 text-xs font-semibold text-gray-500 uppercase">Modified</th>
                {canEdit && <th className="text-right px-6 py-3 text-xs font-semibold text-gray-500 uppercase">Actions</th>}
              </tr>
            </thead>
            <tbody>
              {templates.map((t) => (
                <tr key={t.id} className="border-b border-gray-50 hover:bg-gray-50/50">
                  <td className="px-6 py-3">
                    <div className="flex items-center gap-3">
                      <span className="material-symbols-outlined text-primary text-lg">{t.icon || 'description'}</span>
                      <span className="text-sm font-semibold text-slate-800">{t.name}</span>
                    </div>
                  </td>
                  <td className="px-6 py-3">
                    <span className="text-sm text-slate-600">{t.category}</span>
                    {t.tags && t.tags.length > 0 && (
                      <div className="flex flex-wrap gap-1 mt-1">
                        {t.tags.slice(0, 3).map((tag, i) => (
                          <span key={i} className="text-[9px] px-1.5 py-0.5 bg-slate-100 text-slate-500 rounded-full">{tag}</span>
                        ))}
                      </div>
                    )}
                  </td>
                  <td className="px-6 py-3">
                    <span className={`px-2 py-0.5 text-[11px] font-medium rounded uppercase ${
                      t.status === 'published' ? 'bg-emerald-50 text-emerald-700' :
                      t.status === 'draft' ? 'bg-slate-100 text-slate-600' :
                      'bg-gray-100 text-gray-500'
                    }`}>{t.status}</span>
                  </td>
                  <td className="px-6 py-3 text-sm text-slate-600">{t.stage_count}</td>
                  <td className="px-6 py-3 text-sm text-slate-400">
                    {new Date(t.updated_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}
                  </td>
                  {canEdit && (
                    <td className="px-6 py-3 text-right">
                      <button onClick={() => handleEdit(t.id)} className="p-1 text-primary hover:bg-primary/10 rounded">
                        <span className="material-symbols-outlined text-lg">edit</span>
                      </button>
                      <button onClick={() => handleDelete(t)} className="p-1 text-red-400 hover:bg-red-50 rounded ml-1">
                        <span className="material-symbols-outlined text-lg">delete</span>
                      </button>
                    </td>
                  )}
                </tr>
              ))}
              {templates.length === 0 && (
                <tr><td colSpan={6} className="px-6 py-12 text-center text-slate-400 text-sm">No templates found.</td></tr>
              )}
            </tbody>
          </table>
        </div>
      )}

      <TemplatePagination
        page={page}
        totalPages={totalPages}
        totalItems={total}
        pageSize={PAGE_SIZE}
        onPageChange={setPage}
      />

      {deleteTarget && (
        <DeleteTemplateModal
          templateName={deleteTarget.name}
          onConfirm={handleConfirmDelete}
          onCancel={() => setDeleteTarget(null)}
        />
      )}

      {showCreateModal && (
        <CreateTemplateModal
          onCreateFromScratch={handleCreateFromScratch}
          onCloneTemplate={handleCloneTemplate}
          onCancel={() => setShowCreateModal(false)}
        />
      )}
    </div>
  );
}
