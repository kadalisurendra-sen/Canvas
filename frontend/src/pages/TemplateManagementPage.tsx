import React, { useCallback, useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
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
  const [templates, setTemplates] = useState<TemplateListItem[]>([]);
  const [total, setTotal] = useState(0);
  const [search, setSearch] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
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
      setTemplates(result.items);
      setTotal(result.total);
    } catch {
      setTemplates([]);
      setTotal(0);
    } finally {
      setLoading(false);
    }
  }, [search, categoryFilter, statusFilter, page]);

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
        <div className="flex gap-3">
          <button
            onClick={handleCreate}
            className="flex items-center gap-2 px-4 py-2 bg-primary text-white font-semibold text-sm rounded-lg hover:shadow-lg hover:bg-primary/90 transition-all"
          >
            <span className="material-symbols-outlined text-sm">add</span>
            Create New Template
          </button>
        </div>
      </div>

      <TemplateFilters
        search={search}
        onSearchChange={(v) => { setSearch(v); setPage(1); }}
        category={categoryFilter}
        onCategoryChange={(v) => { setCategoryFilter(v); setPage(1); }}
        status={statusFilter}
        onStatusChange={(v) => { setStatusFilter(v); setPage(1); }}
        viewMode={viewMode}
        onViewModeChange={setViewMode}
      />

      {loading ? (
        <div className="text-center py-12 text-slate-400">Loading templates...</div>
      ) : (
        <TemplateGrid
          templates={templates}
          onEdit={handleEdit}
          onDelete={handleDelete}
        />
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
