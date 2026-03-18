import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useWizard } from '../../context/WizardContext';
import { StageTree } from './step3/StageTree';
import { SectionEditor } from './step3/SectionEditor';
import { FieldPreviewPanel } from './step3/FieldPreviewPanel';
import type { TemplateSection, TemplateStage } from '../../types/template';

export function WizardStep3() {
  const navigate = useNavigate();
  const { state, setStages, setStep } = useWizard();
  const [localStages, setLocalStages] = useState<TemplateStage[]>(state.stages);
  const [activeStageIdx, setActiveStageIdx] = useState(0);
  const [activeSectionIdx, setActiveSectionIdx] = useState(0);

  useEffect(() => { setStep(3); }, [setStep]);

  const activeStage = localStages[activeStageIdx];
  const activeSection = activeStage?.sections?.[activeSectionIdx];

  const handleAddSection = () => {
    const updated = [...localStages];
    const stage = { ...updated[activeStageIdx] };
    const newSection: TemplateSection = {
      name: 'New Section',
      sort_order: (stage.sections?.length || 0) + 1,
      fields: [],
    };
    stage.sections = [...(stage.sections || []), newSection];
    updated[activeStageIdx] = stage;
    setLocalStages(updated);
  };

  const handleUpdateSection = (sectionIdx: number, section: TemplateSection) => {
    const updated = [...localStages];
    const stage = { ...updated[activeStageIdx] };
    const sections = [...(stage.sections || [])];
    sections[sectionIdx] = section;
    stage.sections = sections;
    updated[activeStageIdx] = stage;
    setLocalStages(updated);
  };

  const basePath = state.isEditing && state.templateId
    ? `/templates/${state.templateId}/edit`
    : '/templates/new';

  const handleBack = () => navigate(`${basePath}/step2`);
  const handleNext = () => {
    setStages(localStages);
    navigate(`${basePath}/step4`);
  };

  return (
    <div className="flex gap-6 -mx-6" style={{ minHeight: '500px' }}>
      {/* Left sidebar - Structure tree */}
      <div className="w-1/4 bg-white rounded-lg shadow-sm overflow-hidden flex flex-col border border-[#CFD0D6]">
        <div className="p-4 border-b border-[#CFD0D6]">
          <h3 className="text-[11px] font-bold text-[#9EA1AE] uppercase tracking-widest">
            Structure
          </h3>
        </div>
        <StageTree
          stages={localStages}
          activeStageIdx={activeStageIdx}
          activeSectionIdx={activeSectionIdx}
          onSelectStage={setActiveStageIdx}
          onSelectSection={(stageIdx, sectionIdx) => {
            setActiveStageIdx(stageIdx);
            setActiveSectionIdx(sectionIdx);
          }}
        />
      </div>

      {/* Center - Section/Field editor */}
      <div className="w-1/2 bg-white rounded-lg shadow-sm overflow-hidden flex flex-col border border-[#CFD0D6]">
        <SectionEditor
          section={activeSection}
          sectionIdx={activeSectionIdx}
          onUpdateSection={(section) => handleUpdateSection(activeSectionIdx, section)}
          onAddSection={handleAddSection}
        />
      </div>

      {/* Right - Live preview */}
      <div className="w-1/4 flex flex-col gap-4">
        <div className="flex items-center gap-2 text-slate-400 px-1">
          <span className="material-symbols-outlined text-lg">visibility</span>
          <span className="text-[10px] font-bold uppercase tracking-widest">Live Preview</span>
        </div>
        <FieldPreviewPanel section={activeSection} />
      </div>

      {/* Footer is inside the main flow as an absolute bottom bar */}
      <div className="fixed bottom-0 left-60 right-0 bg-white border-t border-[#CFD0D6] px-8 py-4 flex items-center justify-between z-40 shadow-[0_-4px_16px_rgba(21,28,40,0.03)]">
        <button
          onClick={handleBack}
          className="px-6 py-2 text-slate-600 font-bold text-sm hover:bg-slate-50 transition-colors flex items-center gap-2"
        >
          <span className="material-symbols-outlined text-lg">arrow_back</span> Back
        </button>
        <div className="flex gap-4 items-center">
          <button className="px-6 py-2 text-slate-500 font-bold text-sm hover:text-[#1E2345] transition-colors">
            Save Draft
          </button>
          <button
            onClick={handleNext}
            className="px-8 py-2.5 bg-primary text-white font-bold text-sm rounded shadow-lg shadow-primary/25 hover:bg-primary/90 transition-all flex items-center gap-2"
          >
            Next: Scoring
            <span className="material-symbols-outlined text-lg">arrow_forward</span>
          </button>
        </div>
      </div>
    </div>
  );
}
