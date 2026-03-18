import React from 'react';

interface TemplateFiltersProps {
  search: string;
  onSearchChange: (value: string) => void;
  category: string;
  onCategoryChange: (value: string) => void;
  status: string;
  onStatusChange: (value: string) => void;
  viewMode: 'grid' | 'list';
  onViewModeChange: (mode: 'grid' | 'list') => void;
}

export function TemplateFilters({
  search, onSearchChange, category, onCategoryChange,
  status, onStatusChange, viewMode, onViewModeChange,
}: TemplateFiltersProps) {
  return (
    <div className="bg-white p-4 rounded-xl shadow-sm border border-[#E7E8EB] flex flex-wrap gap-4 items-center mb-8">
      <div className="relative flex-1 min-w-[240px]">
        <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-slate-400">
          search
        </span>
        <input
          className="w-full pl-10 pr-4 py-2 bg-slate-50 border border-slate-200 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary text-sm outline-none"
          placeholder="Search templates..."
          type="text"
          value={search}
          onChange={(e) => onSearchChange(e.target.value)}
        />
      </div>
      <div className="flex items-center gap-3">
        <select
          className="bg-slate-50 border border-slate-200 rounded-lg py-2 pl-3 pr-8 text-sm focus:ring-2 focus:ring-primary focus:border-primary outline-none"
          value={category}
          onChange={(e) => onCategoryChange(e.target.value)}
        >
          <option value="">All Categories</option>
          <option value="AI/ML">AI/ML</option>
          <option value="RPA">RPA</option>
          <option value="Agentic AI">Agentic AI</option>
          <option value="Data Science">Data Science</option>
        </select>
        <select
          className="bg-slate-50 border border-slate-200 rounded-lg py-2 pl-3 pr-8 text-sm focus:ring-2 focus:ring-primary focus:border-primary outline-none"
          value={status}
          onChange={(e) => onStatusChange(e.target.value)}
        >
          <option value="">All Status</option>
          <option value="published">Published</option>
          <option value="draft">Draft</option>
          <option value="archived">Archived</option>
        </select>
        <select className="bg-slate-50 border border-slate-200 rounded-lg py-2 pl-3 pr-8 text-sm focus:ring-2 focus:ring-primary focus:border-primary outline-none">
          <option>Last Modified</option>
          <option>Newest First</option>
          <option>Oldest First</option>
        </select>
      </div>
      <div className="flex bg-slate-100 p-1 rounded-lg">
        <button
          onClick={() => onViewModeChange('grid')}
          className={`p-1.5 rounded shadow-sm ${
            viewMode === 'grid' ? 'bg-white text-primary' : 'text-slate-500 hover:text-slate-700'
          }`}
        >
          <span className="material-symbols-outlined text-[20px]">grid_view</span>
        </button>
        <button
          onClick={() => onViewModeChange('list')}
          className={`p-1.5 rounded ${
            viewMode === 'list' ? 'bg-white text-primary shadow-sm' : 'text-slate-500 hover:text-slate-700'
          }`}
        >
          <span className="material-symbols-outlined text-[20px]">view_list</span>
        </button>
      </div>
    </div>
  );
}
