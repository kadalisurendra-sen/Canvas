import React, { useEffect, useState } from 'react';
import type { TemplateListItem } from '../../types/template';
import { fetchTemplates } from '../../services/templateService';

interface CreateTemplateModalProps {
  onCreateFromScratch: () => void;
  onCloneTemplate: (templateId: string) => void;
  onCancel: () => void;
}

export function CreateTemplateModal({
  onCreateFromScratch,
  onCloneTemplate,
  onCancel,
}: CreateTemplateModalProps) {
  const [mode, setMode] = useState<'scratch' | 'existing'>('scratch');
  const [selectedTemplateId, setSelectedTemplateId] = useState('');
  const [templates, setTemplates] = useState<TemplateListItem[]>([]);

  useEffect(() => {
    fetchTemplates({ status: 'published', page_size: 50 })
      .then((res) => setTemplates(res.items))
      .catch(() => {});
  }, []);

  const handleContinue = () => {
    if (mode === 'scratch') {
      onCreateFromScratch();
    } else if (selectedTemplateId) {
      onCloneTemplate(selectedTemplateId);
    }
  };

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
      <div className="bg-white w-full max-w-[600px] rounded-[16px] shadow-2xl flex flex-col overflow-hidden">
        <div className="px-8 pt-8 pb-4 flex items-center justify-between">
          <h2 className="text-[24px] font-semibold text-slate-900 leading-tight">
            Create New Template
          </h2>
          <button
            onClick={onCancel}
            className="text-slate-400 hover:text-slate-700 transition-colors"
          >
            <span className="material-symbols-outlined text-[24px]">close</span>
          </button>
        </div>

        <div className="px-8 py-4 space-y-4">
          <label
            className={`relative flex items-start p-5 border-2 rounded-[12px] cursor-pointer transition-all group hover:bg-slate-50 ${
              mode === 'scratch'
                ? 'border-primary bg-primary/5'
                : 'border-slate-200'
            }`}
            onClick={() => setMode('scratch')}
          >
            <div className="flex items-center h-6 mr-4">
              <input
                type="radio"
                name="template_type"
                checked={mode === 'scratch'}
                onChange={() => setMode('scratch')}
                className="size-5 text-primary border-slate-300 focus:ring-primary focus:ring-offset-0"
              />
            </div>
            <div className="flex flex-col">
              <span className="font-bold text-[16px] text-slate-900 mb-1">
                Create from scratch
              </span>
              <span className="text-[14px] text-slate-500 leading-[20px]">
                Start with a blank slate and define your own evaluation stages, fields, and scoring mechanisms.
              </span>
            </div>
          </label>

          <label
            className={`relative flex items-start p-5 border-2 rounded-[12px] cursor-pointer transition-all group hover:bg-slate-50 ${
              mode === 'existing'
                ? 'border-primary bg-primary/5'
                : 'border-slate-200'
            }`}
            onClick={() => setMode('existing')}
          >
            <div className="flex items-center h-6 mr-4">
              <input
                type="radio"
                name="template_type"
                checked={mode === 'existing'}
                onChange={() => setMode('existing')}
                className="size-5 text-primary border-slate-300 focus:ring-primary focus:ring-offset-0"
              />
            </div>
            <div className="flex flex-col w-full">
              <span className="font-bold text-[16px] text-slate-900 mb-1">
                Copy existing
              </span>
              <span className="text-[14px] text-slate-500 leading-[20px]">
                Clone a pre-built or existing template to save time and maintain organizational consistency.
              </span>
            </div>
          </label>

          {mode === 'existing' && (
            <div className="mt-2">
              <label
                className="block text-[14px] font-medium text-slate-900 mb-2"
                htmlFor="template-copy"
              >
                Select Template to Copy
              </label>
              <div className="relative">
                <select
                  id="template-copy"
                  className="w-full h-[48px] bg-white border border-slate-300 rounded-[8px] px-4 text-[14px] font-medium text-slate-900 appearance-none focus:ring-2 focus:ring-primary/20 focus:border-primary"
                  value={selectedTemplateId}
                  onChange={(e) => setSelectedTemplateId(e.target.value)}
                >
                  <option disabled value="">
                    Choose a template...
                  </option>
                  {templates.map((t) => (
                    <option key={t.id} value={t.id}>
                      {t.name}
                    </option>
                  ))}
                </select>
                <span className="material-symbols-outlined absolute right-4 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none">
                  expand_more
                </span>
              </div>
            </div>
          )}
        </div>

        <div className="px-8 py-8 flex items-center justify-end gap-6">
          <button
            onClick={onCancel}
            className="text-[16px] font-medium text-slate-500 hover:text-slate-800 transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={handleContinue}
            disabled={mode === 'existing' && !selectedTemplateId}
            className="h-[48px] px-8 bg-primary text-white text-[16px] font-semibold rounded-[8px] hover:bg-primary/90 transition-all shadow-lg disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Continue
          </button>
        </div>
      </div>
    </div>
  );
}
