import React from 'react';

interface TemplatePaginationProps {
  page: number;
  totalPages: number;
  totalItems: number;
  pageSize: number;
  onPageChange: (page: number) => void;
}

export function TemplatePagination({
  page, totalPages, totalItems, pageSize, onPageChange,
}: TemplatePaginationProps) {
  const start = (page - 1) * pageSize + 1;
  const end = Math.min(page * pageSize, totalItems);

  const pages = _getPageNumbers(page, totalPages);

  return (
    <div className="mt-12 flex flex-col sm:flex-row items-center justify-between gap-4 py-4">
      <p className="text-sm text-slate-500 font-medium">
        Showing {start} to {end} of {totalItems} templates
      </p>
      <div className="flex items-center gap-1">
        <button
          className="p-2 rounded-lg hover:bg-white border border-transparent hover:border-slate-200 text-slate-400 disabled:opacity-30 transition-all"
          disabled={page <= 1}
          onClick={() => onPageChange(page - 1)}
        >
          <span className="material-symbols-outlined">chevron_left</span>
        </button>

        {pages.map((p, idx) =>
          p === '...' ? (
            <span key={`ellipsis-${idx}`} className="px-2 text-slate-400">...</span>
          ) : (
            <button
              key={p}
              onClick={() => onPageChange(p as number)}
              className={`w-8 h-8 rounded-lg font-medium text-sm transition-all ${
                p === page
                  ? 'bg-primary text-white font-bold'
                  : 'hover:bg-white border border-transparent hover:border-slate-200 text-slate-600'
              }`}
            >
              {p}
            </button>
          ),
        )}

        <button
          className="p-2 rounded-lg hover:bg-white border border-transparent hover:border-slate-200 text-slate-500 transition-all"
          disabled={page >= totalPages}
          onClick={() => onPageChange(page + 1)}
        >
          <span className="material-symbols-outlined">chevron_right</span>
        </button>
      </div>
    </div>
  );
}

function _getPageNumbers(current: number, total: number): (number | string)[] {
  if (total <= 5) return Array.from({ length: total }, (_, i) => i + 1);
  const pages: (number | string)[] = [];
  pages.push(1);
  if (current > 3) pages.push('...');
  const start = Math.max(2, current - 1);
  const end = Math.min(total - 1, current + 1);
  for (let i = start; i <= end; i++) pages.push(i);
  if (current < total - 2) pages.push('...');
  pages.push(total);
  return pages;
}
