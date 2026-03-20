import React from 'react';
import type { TemplateListItem } from '../../types/template';

interface TemplateCardProps {
  template: TemplateListItem;
  onEdit?: (id: string) => void;
  onDelete?: (template: TemplateListItem) => void;
}

const CATEGORY_COLORS: Record<string, { bg: string; text: string; border: string }> = {
  'AI/ML': { bg: 'bg-blue-50', text: 'text-blue-700', border: 'border-blue-100' },
  'RPA': { bg: 'bg-purple-50', text: 'text-purple-700', border: 'border-purple-100' },
  'Agentic AI': { bg: 'bg-teal-50', text: 'text-teal-700', border: 'border-teal-100' },
  'Data Science': { bg: 'bg-orange-50', text: 'text-orange-700', border: 'border-orange-100' },
  'Digital': { bg: 'bg-green-50', text: 'text-green-700', border: 'border-green-100' },
  'Custom': { bg: 'bg-slate-100', text: 'text-slate-700', border: 'border-slate-200' },
};

function getStatusBadge(status: string) {
  switch (status) {
    case 'published':
      return (
        <span className="px-2.5 py-1 bg-[#02F576] text-[#151C28] text-[12px] font-medium rounded uppercase tracking-wider">
          Published
        </span>
      );
    case 'draft':
      return (
        <span className="px-2.5 py-1 bg-slate-200 text-slate-700 text-[12px] font-medium rounded uppercase tracking-wider">
          Draft
        </span>
      );
    default:
      return null;
  }
}

export function TemplateCard({ template, onEdit, onDelete }: TemplateCardProps) {
  const catColor = CATEGORY_COLORS[template.category] || CATEGORY_COLORS['Custom'];
  const themeColor = template.theme_color || '#5F2CFF';

  return (
    <div
      className="bg-white rounded-[24px] shadow-sm border border-[#E7E8EB] hover:shadow-md transition-shadow overflow-hidden flex flex-col h-full"
      style={{ borderTopColor: themeColor, borderTopWidth: '3px' }}
    >
      <div className="p-6 flex-1">
        <div className="flex justify-between items-start mb-4">
          <div
            className="w-12 h-12 rounded-lg flex items-center justify-center"
            style={{ backgroundColor: `${themeColor}15`, color: themeColor }}
          >
            <span className="material-symbols-outlined text-[28px]">
              {template.icon || 'description'}
            </span>
          </div>
          <div className="flex flex-wrap gap-2 justify-end">
            <span className={`px-2.5 py-1 ${catColor.bg} ${catColor.text} text-[12px] font-medium rounded uppercase tracking-wider border ${catColor.border}`}>
              {template.category}
            </span>
            {getStatusBadge(template.status)}
          </div>
        </div>

        <h3 className="text-[24px] font-semibold text-slate-900 mb-2">{template.name}</h3>
        <p className="text-sm text-slate-500 line-clamp-2">{template.description}</p>

        {/* Tags */}
        {template.tags && template.tags.length > 0 && (
          <div className="flex flex-wrap gap-1.5 mt-3">
            {template.tags.slice(0, 4).map((tag, i) => (
              <span
                key={i}
                className="px-2 py-0.5 text-[10px] font-medium rounded-full border"
                style={{
                  color: themeColor,
                  borderColor: `${themeColor}30`,
                  backgroundColor: `${themeColor}08`,
                }}
              >
                {tag}
              </span>
            ))}
            {template.tags.length > 4 && (
              <span className="px-2 py-0.5 text-[10px] font-medium text-slate-400 bg-slate-50 rounded-full">
                +{template.tags.length - 4}
              </span>
            )}
          </div>
        )}

        <div className="mt-6 grid grid-cols-3 gap-4 border-t border-slate-100 pt-6">
          <div className="text-center">
            <p className="text-xs text-slate-500 mb-1 font-medium">Stages</p>
            <p className="font-bold text-2xl text-slate-800">{template.stage_count}</p>
          </div>
          <div className="text-center border-x border-slate-100">
            <p className="text-xs text-slate-500 mb-1 font-medium">Data Points</p>
            <p className="font-bold text-2xl text-slate-800">{template.field_count}</p>
          </div>
          <div className="text-center">
            <p className="text-xs text-slate-500 mb-1 font-medium">Projects</p>
            <p className="font-bold text-2xl text-slate-800">0</p>
          </div>
        </div>
      </div>

      <div className="bg-slate-50 px-6 py-4 border-t border-slate-100 flex justify-between items-center mt-auto">
        <span className="text-xs text-slate-500 font-medium">
          {_formatDate(template.updated_at)}
        </span>
        <div className="flex gap-2">
          {onEdit && (
            <button
              onClick={() => onEdit(template.id)}
              className="p-2 text-primary hover:bg-primary/10 rounded-full transition-colors"
            >
              <span className="material-symbols-outlined text-[20px]">edit</span>
            </button>
          )}
          {onDelete && (
            <button
              onClick={() => onDelete(template)}
              className="p-2 text-rose-500 hover:bg-rose-50 rounded-full transition-colors"
            >
              <span className="material-symbols-outlined text-[20px]">delete</span>
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

function _formatDate(dateStr: string): string {
  const date = new Date(dateStr);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
  if (diffDays < 1) return 'Modified today';
  if (diffDays < 7) return `Modified ${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
  if (diffDays < 30) return `Modified ${Math.floor(diffDays / 7)} week${Math.floor(diffDays / 7) > 1 ? 's' : ''} ago`;
  if (diffDays < 365) return `Modified ${Math.floor(diffDays / 30)} month${Math.floor(diffDays / 30) > 1 ? 's' : ''} ago`;
  return `Modified on ${date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}`;
}
