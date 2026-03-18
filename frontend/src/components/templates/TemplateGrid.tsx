import React from 'react';
import { TemplateCard } from './TemplateCard';
import type { TemplateListItem } from '../../types/template';

interface TemplateGridProps {
  templates: TemplateListItem[];
  onEdit: (id: string) => void;
  onDelete: (template: TemplateListItem) => void;
}

export function TemplateGrid({ templates, onEdit, onDelete }: TemplateGridProps) {
  if (templates.length === 0) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-[#E7E8EB] p-12 text-center">
        <span className="material-symbols-outlined text-4xl text-slate-300 mb-4 block">
          description
        </span>
        <p className="text-slate-500 text-sm">No templates found.</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
      {templates.map((template) => (
        <TemplateCard
          key={template.id}
          template={template}
          onEdit={onEdit}
          onDelete={onDelete}
        />
      ))}
    </div>
  );
}
