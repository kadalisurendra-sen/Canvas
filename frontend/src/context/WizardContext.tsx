import React, { createContext, useCallback, useContext, useState } from 'react';
import type {
  FailAction,
  FieldType,
  TemplateCreatePayload,
  TemplateField,
  TemplateSection,
  TemplateStage,
} from '../types/template';

interface WizardState {
  templateId: string | null;
  step: number;
  generalInfo: TemplateCreatePayload;
  stages: TemplateStage[];
  isEditing: boolean;
}

interface WizardContextValue {
  state: WizardState;
  setTemplateId: (id: string) => void;
  setStep: (step: number) => void;
  setGeneralInfo: (info: TemplateCreatePayload) => void;
  setStages: (stages: TemplateStage[]) => void;
  setIsEditing: (editing: boolean) => void;
  resetWizard: () => void;
}

const DEFAULT_STAGES: TemplateStage[] = [
  {
    name: 'Desirable', sort_order: 1, weight_pct: 34, min_pass_score: null,
    fail_action: 'warn', sections: [],
  },
  {
    name: 'Feasible', sort_order: 2, weight_pct: 33, min_pass_score: null,
    fail_action: 'warn', sections: [],
  },
  {
    name: 'Viable', sort_order: 3, weight_pct: 33, min_pass_score: null,
    fail_action: 'warn', sections: [],
  },
];

const INITIAL_STATE: WizardState = {
  templateId: null,
  step: 1,
  generalInfo: {
    name: '',
    category: '',
    description: '',
    icon: 'psychology',
    theme_color: '#02F576',
    tags: [],
  },
  stages: DEFAULT_STAGES,
  isEditing: false,
};

const WizardContext = createContext<WizardContextValue | undefined>(undefined);

export function WizardProvider({ children }: { children: React.ReactNode }) {
  const [state, setState] = useState<WizardState>(INITIAL_STATE);

  const setTemplateId = useCallback((id: string) => {
    setState((prev) => ({ ...prev, templateId: id }));
  }, []);

  const setStep = useCallback((step: number) => {
    setState((prev) => ({ ...prev, step }));
  }, []);

  const setGeneralInfo = useCallback((info: TemplateCreatePayload) => {
    setState((prev) => ({ ...prev, generalInfo: info }));
  }, []);

  const setStages = useCallback((stages: TemplateStage[]) => {
    setState((prev) => ({ ...prev, stages }));
  }, []);

  const setIsEditing = useCallback((editing: boolean) => {
    setState((prev) => ({ ...prev, isEditing: editing }));
  }, []);

  const resetWizard = useCallback(() => {
    setState(INITIAL_STATE);
  }, []);

  return (
    <WizardContext.Provider
      value={{
        state,
        setTemplateId,
        setStep,
        setGeneralInfo,
        setStages,
        setIsEditing,
        resetWizard,
      }}
    >
      {children}
    </WizardContext.Provider>
  );
}

export function useWizard(): WizardContextValue {
  const context = useContext(WizardContext);
  if (!context) {
    throw new Error('useWizard must be used within a WizardProvider');
  }
  return context;
}
