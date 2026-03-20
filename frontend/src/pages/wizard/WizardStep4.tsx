import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useWizard } from '../../context/WizardContext';
import { StageWeightsPanel } from './step4/StageWeightsPanel';
import { QualificationTable } from './step4/QualificationTable';
import type { FailAction, TemplateStage } from '../../types/template';

export function WizardStep4() {
  const navigate = useNavigate();
  const { state, setStages, setStep } = useWizard();
  const [localStages, setLocalStages] = useState<TemplateStage[]>(state.stages);

  useEffect(() => { setStep(4); }, [setStep]);

  // Sync when context updates (template loaded from API)
  useEffect(() => {
    if (state.stages.length > 0) {
      setLocalStages(state.stages);
    }
  }, [state.stages]);

  const handleWeightChange = (idx: number, weight: number) => {
    const updated = [...localStages];
    updated[idx] = { ...updated[idx], weight_pct: weight };
    setLocalStages(updated);
  };

  const handleScoreChange = (idx: number, score: number | null) => {
    const updated = [...localStages];
    updated[idx] = { ...updated[idx], min_pass_score: score };
    setLocalStages(updated);
  };

  const handleFailActionChange = (idx: number, action: FailAction) => {
    const updated = [...localStages];
    updated[idx] = { ...updated[idx], fail_action: action };
    setLocalStages(updated);
  };

  const totalWeight = localStages.reduce((sum, s) => sum + s.weight_pct, 0);
  const weightValid = Math.abs(totalWeight - 100) < 0.01;

  const basePath = state.isEditing && state.templateId
    ? `/templates/${state.templateId}/edit`
    : '/templates/new';

  const handleBack = () => navigate(`${basePath}/step3`);
  const handleNext = () => {
    setStages(localStages);
    navigate(`${basePath}/step5`);
  };

  return (
    <div className="space-y-8">
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-8">
        <StageWeightsPanel
          stages={localStages}
          onWeightChange={handleWeightChange}
          totalWeight={totalWeight}
          weightValid={weightValid}
        />
        <QualificationTable
          stages={localStages}
          onScoreChange={handleScoreChange}
          onFailActionChange={handleFailActionChange}
        />
      </div>

      <div className="flex items-center justify-between pt-6 mt-8 pb-4">
        <button
          onClick={handleBack}
          className="px-6 py-2.5 text-[#6D7283] font-semibold hover:text-[#1E2345] transition-all flex items-center gap-2"
        >
          <span className="material-symbols-outlined text-sm">arrow_back</span> Back
        </button>
        <div className="flex gap-4">
          <button
            onClick={handleNext}
            disabled={!weightValid}
            className="px-8 py-2.5 rounded-lg bg-primary text-white font-bold hover:shadow-lg hover:bg-primary/90 transition-all flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Next: Publish
            <span className="material-symbols-outlined text-sm font-bold">arrow_forward</span>
          </button>
        </div>
      </div>
    </div>
  );
}
