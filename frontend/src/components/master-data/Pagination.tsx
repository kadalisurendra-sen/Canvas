/* Pagination component */

interface PaginationProps {
  page: number;
  pageSize: number;
  total: number;
  onPageChange: (page: number) => void;
}

export function Pagination({ page, pageSize, total, onPageChange }: PaginationProps) {
  const showing = Math.min(page * pageSize, total);
  const hasPrev = page > 1;
  const hasNext = page * pageSize < total;

  return (
    <div className="mt-auto border-t border-[#E7E8EB] p-4 bg-slate-50 flex items-center justify-between">
      <span className="text-xs text-slate-500 font-medium">
        Showing {Math.min((page - 1) * pageSize + 1, total)}-{showing} of {total} values
      </span>
      <div className="flex items-center gap-2">
        <button
          onClick={() => onPageChange(page - 1)}
          disabled={!hasPrev}
          className={`p-1 rounded border border-[#E7E8EB] bg-white ${
            hasPrev ? 'text-slate-600 hover:bg-slate-50' : 'text-slate-400 cursor-not-allowed'
          }`}
        >
          <span className="material-symbols-outlined text-[18px]">chevron_left</span>
        </button>
        <span className="text-xs font-bold px-2">{page}</span>
        <button
          onClick={() => onPageChange(page + 1)}
          disabled={!hasNext}
          className={`p-1 rounded border border-[#E7E8EB] bg-white ${
            hasNext ? 'text-slate-600 hover:bg-slate-50' : 'text-slate-400 cursor-not-allowed'
          }`}
        >
          <span className="material-symbols-outlined text-[18px]">chevron_right</span>
        </button>
      </div>
    </div>
  );
}
