import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useWizard } from '../../context/WizardContext';
import { StageRow } from './step2/StageRow';
import { updateStages } from '../../services/templateService';
import type { TemplateStage } from '../../types/template';

export function WizardStep2() {
  const navigate = useNavigate();
  const { state, setStages, setStep } = useWizard();
  const [localStages, setLocalStages] = useState<TemplateStage[]>(state.stages);
  const [error, setError] = useState('');

  useEffect(() => { setStep(2); }, [setStep]);

  const handleAddStage = () => {
    const newStage: TemplateStage = {
      name: '',
      sort_order: localStages.length + 1,
      weight_pct: 0,
      min_pass_score: null,
      fail_action: 'warn',
      sections: [],
    };
    setLocalStages([...localStages, newStage]);
  };

  const handleRemoveStage = (index: number) => {
    if (localStages.length <= 1) {
      setError('At least one stage is required');
      return;
    }
    const updated = localStages.filter((_, i) => i !== index)
      .map((s, i) => ({ ...s, sort_order: i + 1 }));
    setLocalStages(updated);
    setError('');
  };

  const handleNameChange = (index: number, name: string) => {
    const updated = [...localStages];
    updated[index] = { ...updated[index], name };
    setLocalStages(updated);
  };

  const handleMoveUp = (index: number) => {
    if (index <= 0) return;
    const updated = [...localStages];
    [updated[index - 1], updated[index]] = [updated[index], updated[index - 1]];
    setLocalStages(updated.map((s, i) => ({ ...s, sort_order: i + 1 })));
  };

  const handleMoveDown = (index: number) => {
    if (index >= localStages.length - 1) return;
    const updated = [...localStages];
    [updated[index], updated[index + 1]] = [updated[index + 1], updated[index]];
    setLocalStages(updated.map((s, i) => ({ ...s, sort_order: i + 1 })));
  };

  const basePath = state.isEditing && state.templateId
    ? `/templates/${state.templateId}/edit`
    : '/templates/new';

  const handleBack = () => navigate(basePath);
  const [saving, setSaving] = useState(false);

  const handleNext = async () => {
    const names = localStages.map((s) => s.name.trim());
    if (names.some((n) => !n)) {
      setError('All stage names must be non-empty');
      return;
    }
    if (new Set(names).size !== names.length) {
      setError('Stage names must be unique');
      return;
    }

    // Save stages to backend
    if (state.templateId) {
      setSaving(true);
      try {
        await updateStages(state.templateId, localStages.map((s) => ({
          name: s.name,
          sort_order: s.sort_order,
        })));
      } catch (err) {
        setError('Failed to save stages');
        setSaving(false);
        return;
      }
      setSaving(false);
    }

    setStages(localStages);
    navigate(`${basePath}/step3`);
  };

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-[#E7E8EB] overflow-hidden p-8">
      <div className="pb-4 mb-4 border-b border-[#E7E8EB] flex items-center justify-between">
        <h3 className="font-bold text-[#151C28] text-lg">Evaluation Stages</h3>
        <span className="text-xs bg-slate-100 text-slate-600 px-3 py-1.5 rounded font-bold uppercase tracking-wider">
          Drag to Reorder
        </span>
      </div>

      <div className="space-y-3">
        {localStages.map((stage, index) => (
          <StageRow
            key={index}
            index={index}
            name={stage.name}
            onNameChange={(name) => handleNameChange(index, name)}
            onRemove={() => handleRemoveStage(index)}
            onMoveUp={() => handleMoveUp(index)}
            onMoveDown={() => handleMoveDown(index)}
          />
        ))}
      </div>

      {error && (
        <p className="mt-3 text-sm text-rose-500 font-medium">{error}</p>
      )}

      <div className="mt-6 flex justify-center">
        <button
          onClick={handleAddStage}
          className="flex items-center gap-2 px-6 py-2.5 rounded-xl border-2 border-dashed border-[#E7E8EB] text-slate-500 font-bold hover:border-primary hover:text-primary transition-all group w-full justify-center"
        >
          <span className="material-symbols-outlined text-xl transition-transform group-hover:scale-110">
            add_circle
          </span>
          Add New Evaluation Stage
        </button>
      </div>

      <div className="mt-6 p-4 bg-slate-50 rounded-lg border border-[#E7E8EB]">
        <p className="text-xs text-slate-500 flex items-center gap-2">
          <span className="material-symbols-outlined text-sm text-primary">info</span>
          Tip: The stages defined here will establish the default evaluation path for this template.
          You can customize field requirements for each stage in step 3.
        </p>
      </div>

      <div className="mt-8 flex items-center justify-between border-t border-[#E7E8EB] pt-4">
        <button
          onClick={handleBack}
          className="flex items-center gap-2 px-6 py-2 text-[#6D7283] font-bold hover:text-[#151C28] transition-colors"
        >
          <span className="material-symbols-outlined text-lg">arrow_back</span>
          Back
        </button>
        <div className="flex items-center gap-3">
          <button className="px-6 py-2 rounded-lg text-slate-500 font-bold hover:bg-slate-50 transition-colors">
            Save as Draft
          </button>
          <button
            onClick={handleNext}
            disabled={saving}
            className="flex items-center gap-2 px-8 py-2 rounded-lg bg-primary text-white font-bold hover:bg-primary/90 shadow-sm transition-all active:scale-95 disabled:opacity-50"
          >
            {saving ? 'Saving...' : 'Next'}
            <span className="material-symbols-outlined text-lg">arrow_forward</span>
          </button>
        </div>
      </div>
    </div>
  );
}
