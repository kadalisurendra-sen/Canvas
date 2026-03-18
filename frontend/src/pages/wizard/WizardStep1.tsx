import React, { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useWizard } from '../../context/WizardContext';
import { IconPicker } from './step1/IconPicker';
import { ColorPicker } from './step1/ColorPicker';
import { TagInput } from './step1/TagInput';
import { createTemplate, updateTemplate } from '../../services/templateService';

const CATEGORIES = [
  { value: 'ai', label: 'AI/ML Solutions' },
  { value: 'rpa', label: 'RPA Automation' },
  { value: 'cloud', label: 'Cloud Migration' },
  { value: 'finops', label: 'FinOps Optimization' },
];

export function WizardStep1() {
  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>();
  const { state, setGeneralInfo, setStep, setTemplateId } = useWizard();
  const info = state.generalInfo;

  const [name, setName] = useState(info.name);
  const [category, setCategory] = useState(info.category);
  const [description, setDescription] = useState(info.description || '');
  const [icon, setIcon] = useState(info.icon || 'psychology');
  const [themeColor, setThemeColor] = useState(info.theme_color || '#02F576');
  const [tags, setTags] = useState<string[]>(info.tags);

  useEffect(() => { setStep(1); }, [setStep]);

  // Sync local state when wizard context updates (e.g., template loaded for editing)
  useEffect(() => {
    if (info.name && info.name !== name) setName(info.name);
    if (info.category && info.category !== category) setCategory(info.category);
    if (info.description !== undefined) setDescription(info.description || '');
    if (info.icon) setIcon(info.icon);
    if (info.theme_color) setThemeColor(info.theme_color);
    if (info.tags) setTags(info.tags);
  }, [info]); // eslint-disable-line react-hooks/exhaustive-deps

  const [saving, setSaving] = useState(false);
  const isValid = name.trim().length > 0 && category.trim().length > 0;

  const handleNext = async () => {
    const payload = { name, category, description, icon, theme_color: themeColor, tags };
    setGeneralInfo(payload);
    setSaving(true);
    let templateId = state.templateId || id || null;
    try {
      if (templateId) {
        await updateTemplate(templateId, payload);
      } else {
        const result = await createTemplate(payload);
        templateId = result.id;
        setTemplateId(result.id);
      }
    } catch {
      // continue even if save fails
    } finally {
      setSaving(false);
    }
    const base = templateId
      ? `/templates/${templateId}/edit`
      : '/templates/new';
    navigate(`${base}/step2`);
  };

  const handleCancel = () => {
    navigate('/templates');
  };

  return (
    <div className="bg-[#F3F4F4] rounded-[24px] shadow-[0px_4px_16px_rgba(21,28,40,0.08)] p-8">
      <form className="space-y-6" onSubmit={(e) => e.preventDefault()}>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="flex flex-col gap-2">
            <label className="text-[14px] font-medium text-[#3D4353]">
              Template Name <span className="text-red-500">*</span>
            </label>
            <input
              className="w-full rounded-[8px] border-[#CFD0D6] bg-white focus:border-primary focus:ring-primary h-11 text-sm transition-all"
              placeholder="e.g. AI Readiness Framework"
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
            />
          </div>
          <div className="flex flex-col gap-2">
            <label className="text-[14px] font-medium text-[#3D4353]">
              Category/Domain <span className="text-red-500">*</span>
            </label>
            <select
              className="w-full rounded-[8px] border-[#CFD0D6] bg-white focus:border-primary focus:ring-primary h-11 text-sm"
              value={category}
              onChange={(e) => setCategory(e.target.value)}
            >
              <option value="">Select Domain</option>
              {CATEGORIES.map((c) => (
                <option key={c.value} value={c.value}>{c.label}</option>
              ))}
            </select>
          </div>
        </div>

        <div className="flex flex-col gap-2">
          <div className="flex justify-between items-center">
            <label className="text-[14px] font-medium text-[#3D4353]">
              Description <span className="text-red-500">*</span>
            </label>
            <span className="text-[10px] text-slate-400 font-medium">
              {description.length}/500 characters
            </span>
          </div>
          <textarea
            className="w-full rounded-[8px] border-[#CFD0D6] bg-white focus:border-primary focus:ring-primary text-sm transition-all resize-none"
            placeholder="Briefly describe the purpose of this evaluation template..."
            rows={4}
            maxLength={500}
            value={description}
            onChange={(e) => setDescription(e.target.value)}
          />
        </div>

        <IconPicker selected={icon} onSelect={setIcon} />
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <ColorPicker selected={themeColor} onSelect={setThemeColor} />
          <TagInput tags={tags} onChange={setTags} />
        </div>
      </form>

      <div className="mt-8 flex items-center justify-between">
        <button
          onClick={handleCancel}
          className="text-[#6D7283] font-medium text-sm hover:text-slate-900 transition-colors"
        >
          Cancel
        </button>
        <button
          onClick={handleNext}
          disabled={!isValid || saving}
          className="flex items-center gap-2 px-8 py-2.5 rounded-[8px] bg-primary text-white font-medium text-sm hover:bg-primary/90 shadow-lg shadow-primary/20 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {saving ? 'Saving...' : 'Next: Stage Config'}
          <span className="material-symbols-outlined text-lg">arrow_forward</span>
        </button>
      </div>
    </div>
  );
}
