import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useWizard } from '../../context/WizardContext';
import { TemplatePreview } from './step5/TemplatePreview';
import { TemplateSummary } from './step5/TemplateSummary';
import { publishTemplate, updateTemplate } from '../../services/templateService';

export function WizardStep5() {
  const navigate = useNavigate();
  const { state, setStep, resetWizard } = useWizard();
  const [publishing, setPublishing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => { setStep(5); }, [setStep]);

  const totalFields = state.stages.reduce((sum, stage) =>
    sum + stage.sections.reduce((sSum, sec) => sSum + sec.fields.length, 0), 0);

  const handleBack = () => {
    const base = state.isEditing
      ? `/templates/${state.templateId}/edit`
      : '/templates/new';
    navigate(`${base}/step4`);
  };

  const handleSaveDraft = async () => {
    if (state.templateId) {
      try {
        await updateTemplate(state.templateId, {
          name: state.generalInfo.name,
          category: state.generalInfo.category,
          description: state.generalInfo.description,
          icon: state.generalInfo.icon,
          theme_color: state.generalInfo.theme_color,
          tags: state.generalInfo.tags,
        });
      } catch {
        // draft save failed, still navigate away
      }
    }
    resetWizard();
    navigate('/templates');
  };

  const handlePublish = async () => {
    if (!state.templateId) {
      setError('Template must be saved before publishing.');
      return;
    }
    setPublishing(true);
    setError(null);
    try {
      await publishTemplate(state.templateId);
      resetWizard();
      navigate('/templates');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to publish template');
    } finally {
      setPublishing(false);
    }
  };

  return (
    <div className="pb-24">
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        <div className="lg:col-span-8 space-y-4">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-2xl font-bold">Template Preview</h2>
            <span className="text-sm text-[#6D7283] flex items-center gap-1">
              <span className="material-symbols-outlined text-sm">devices</span>
              Desktop View
            </span>
          </div>
          <TemplatePreview stages={state.stages} />
        </div>

        <div className="lg:col-span-4">
          <h2 className="text-2xl font-bold mb-4 invisible">Summary</h2>
          <TemplateSummary
            stageCount={state.stages.length}
            fieldCount={totalFields}
            hasScoring={state.stages.some((s) => s.weight_pct > 0)}
          />
        </div>
      </div>

      {error && (
        <div className="mt-4 p-3 bg-rose-50 border border-rose-200 text-rose-700 text-sm rounded-lg">
          {error}
        </div>
      )}

      <div className="fixed bottom-0 left-60 right-0 bg-white border-t border-slate-200 p-4 z-40">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <button
            onClick={handleBack}
            className="flex items-center gap-2 px-6 py-2.5 text-[#6D7283] font-bold text-sm hover:text-slate-800 transition-colors"
          >
            <span className="material-symbols-outlined text-sm">arrow_back</span>
            Back
          </button>
          <div className="flex items-center gap-4">
            <button
              onClick={handleSaveDraft}
              className="px-6 py-2.5 rounded-lg border border-primary text-primary font-bold text-sm hover:bg-primary/5 transition-colors"
            >
              Save as Draft
            </button>
            <button
              onClick={handlePublish}
              disabled={publishing || !state.templateId}
              className="px-8 py-2.5 rounded-lg bg-primary text-white font-bold text-sm hover:bg-primary/90 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {publishing ? 'Publishing...' : 'Publish Template'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
