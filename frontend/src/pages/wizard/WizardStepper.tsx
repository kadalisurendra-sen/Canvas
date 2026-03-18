import React from 'react';
import { useWizard } from '../../context/WizardContext';

const STEPS = [
  { num: 1, label: '1. General Info' },
  { num: 2, label: '2. Stage Config' },
  { num: 3, label: '3. Field and Sections' },
  { num: 4, label: '4. Scoring' },
  { num: 5, label: '5. Publish' },
];

export function WizardStepper() {
  const { state } = useWizard();
  const currentStep = state.step;

  return (
    <div className="mb-8">
      <h1 className="text-[32px] font-bold text-slate-900">
        {state.isEditing ? 'Edit Template' : 'Create New Template'}
      </h1>
      <p className="text-slate-500 text-sm mt-1">
        {_getSubtitle(currentStep)}
      </p>

      <div className="mt-8 flex items-center w-full relative">
        {/* Progress line background */}
        <div className="absolute top-5 left-[10%] right-[10%] h-[2px] bg-[#E7E8EB] z-0" />
        {/* Active progress line */}
        <div
          className="absolute top-5 left-[10%] h-[2px] bg-primary z-0 transition-all duration-300"
          style={{ width: `${((currentStep - 1) / (STEPS.length - 1)) * 80}%` }}
        />

        {STEPS.map((step) => {
          const isCompleted = step.num < currentStep;
          const isActive = step.num === currentStep;
          const isPending = step.num > currentStep;

          return (
            <div key={step.num} className="flex flex-col items-center flex-1 relative z-10">
              <div
                className={`w-10 h-10 rounded-full flex items-center justify-center font-bold text-sm transition-all ${
                  isCompleted
                    ? 'bg-primary text-white shadow-lg shadow-primary/20'
                    : isActive
                    ? 'bg-white border-2 border-primary text-primary ring-4 ring-primary/5'
                    : 'bg-[#E7E8EB] text-slate-400'
                }`}
              >
                {isCompleted ? (
                  <span className="material-symbols-outlined text-lg">check</span>
                ) : (
                  step.num
                )}
              </div>
              <span
                className={`text-[11px] mt-2 text-center whitespace-nowrap ${
                  isCompleted || isActive
                    ? 'font-semibold text-primary'
                    : 'font-medium text-slate-400'
                }`}
              >
                {step.label}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function _getSubtitle(step: number): string {
  switch (step) {
    case 1: return 'Configure the baseline metadata for your evaluation framework.';
    case 2: return 'Configure the evaluation stages for this template.';
    case 3: return 'Configure section fields and scoring logic.';
    case 4: return 'Define scoring weights and qualification thresholds.';
    case 5: return 'Review your template and publish when ready.';
    default: return '';
  }
}
