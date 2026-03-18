import React from 'react';
import { FieldRow } from './FieldRow';
import type { TemplateField, TemplateSection, FieldType } from '../../../types/template';

interface SectionEditorProps {
  section: TemplateSection | undefined;
  sectionIdx: number;
  onUpdateSection: (section: TemplateSection) => void;
  onAddSection: () => void;
}

export function SectionEditor({
  section, sectionIdx, onUpdateSection, onAddSection,
}: SectionEditorProps) {
  if (!section) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center p-8 text-slate-400">
        <span className="material-symbols-outlined text-4xl mb-2">layers</span>
        <p className="text-sm font-medium">Select a section or add one to begin</p>
        <button
          onClick={onAddSection}
          className="mt-4 flex items-center gap-2 px-4 py-2 border border-[#CFD0D6] text-slate-600 text-xs font-bold rounded hover:bg-slate-50 transition-colors"
        >
          <span className="material-symbols-outlined text-lg">layers</span>
          Add Section
        </button>
      </div>
    );
  }

  const handleAddField = () => {
    const newField: TemplateField = {
      field_key: '',
      label: '',
      field_type: 'text_short',
      help_text: '',
      is_mandatory: false,
      is_scoring: false,
      sort_order: section.fields.length + 1,
      options: [],
    };
    onUpdateSection({ ...section, fields: [...section.fields, newField] });
  };

  const handleUpdateField = (fieldIdx: number, field: TemplateField) => {
    const updated = [...section.fields];
    updated[fieldIdx] = field;
    onUpdateSection({ ...section, fields: updated });
  };

  const handleRemoveField = (fieldIdx: number) => {
    const updated = section.fields.filter((_, i) => i !== fieldIdx);
    onUpdateSection({ ...section, fields: updated });
  };

  return (
    <>
      <div className="p-5 border-b border-[#CFD0D6] flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-[#1E2345]">{section.name}</h2>
          <p className="text-xs text-slate-400 mt-1">Configure section fields and scoring logic</p>
        </div>
        <button className="w-8 h-8 flex items-center justify-center text-slate-400 hover:text-[#1E2345] rounded-full hover:bg-slate-50 transition-colors">
          <span className="material-symbols-outlined">more_vert</span>
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-6 bg-slate-50/50">
        <div className="space-y-4">
          {section.fields.map((field, fieldIdx) => (
            <FieldRow
              key={fieldIdx}
              field={field}
              onUpdate={(f) => handleUpdateField(fieldIdx, f)}
              onRemove={() => handleRemoveField(fieldIdx)}
            />
          ))}

          <div className="border-2 border-dashed border-[#CFD0D6] rounded-xl py-6 flex flex-col items-center justify-center text-slate-400 gap-2 hover:bg-white transition-all cursor-pointer">
            <span className="material-symbols-outlined text-3xl">add_circle</span>
            <span className="text-xs font-semibold">Drop components here to add fields</span>
          </div>
        </div>

        <div className="mt-8 flex gap-3">
          <button
            onClick={handleAddField}
            className="flex items-center gap-2 px-4 py-2 border border-primary text-primary text-xs font-bold rounded hover:bg-primary/5 transition-colors"
          >
            <span className="material-symbols-outlined text-lg">add</span> Add Field
          </button>
          <button
            onClick={onAddSection}
            className="flex items-center gap-2 px-4 py-2 border border-[#CFD0D6] text-slate-600 text-xs font-bold rounded hover:bg-slate-50 transition-colors"
          >
            <span className="material-symbols-outlined text-lg">layers</span> Add Section
          </button>
        </div>
      </div>
    </>
  );
}
