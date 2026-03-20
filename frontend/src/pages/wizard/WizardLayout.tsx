import React, { useEffect } from 'react';
import { Outlet, useParams } from 'react-router-dom';
import { WizardProvider, useWizard } from '../../context/WizardContext';
import { WizardStepper } from './WizardStepper';
import { fetchTemplate } from '../../services/templateService';
import type { TemplateStage } from '../../types/template';

/** Normalize API stage data — convert string numerics to numbers */
function normalizeStages(stages: TemplateStage[]): TemplateStage[] {
  return stages.map((s) => ({
    ...s,
    weight_pct: Number(s.weight_pct) || 0,
    min_pass_score: s.min_pass_score != null ? Number(s.min_pass_score) : null,
    sections: (s.sections || []).map((sec) => ({
      ...sec,
      fields: (sec.fields || []).map((f) => ({
        ...f,
        options: (f.options || []).map((o) => ({
          ...o,
          score: Number(o.score) || 0,
        })),
      })),
    })),
  }));
}

function WizardDataLoader({ children }: { children: React.ReactNode }) {
  const { id } = useParams<{ id: string }>();
  const { state, setTemplateId, setGeneralInfo, setStages, setIsEditing } = useWizard();

  useEffect(() => {
    if (!id) return;
    if (state.templateId === id) return; // already loaded
    let cancelled = false;

    async function loadTemplate() {
      try {
        const tpl = await fetchTemplate(id as string);
        if (cancelled) return;
        setTemplateId(tpl.id);
        setIsEditing(true);
        setGeneralInfo({
          name: tpl.name,
          category: tpl.category,
          description: tpl.description,
          icon: tpl.icon,
          theme_color: tpl.theme_color,
          tags: tpl.tags?.map((t) =>
            typeof t === 'string' ? t : t.tag
          ) || [],
        });
        if (tpl.stages && tpl.stages.length > 0) {
          const normalized = normalizeStages(tpl.stages);
          console.log('[WizardLoader] Loaded template:', tpl.id, tpl.name);
          console.log('[WizardLoader] Stages:', normalized.map(s => ({
            name: s.name, id: s.id,
            sections: s.sections.map(sec => ({
              name: sec.name,
              fields: sec.fields.map(f => ({ label: f.label, options: f.options.length }))
            }))
          })));
          setStages(normalized);
        }
      } catch {
        // Template load failed
      }
    }

    loadTemplate();
    return () => { cancelled = true; };
  }, [id, setTemplateId, setGeneralInfo, setStages, setIsEditing, state.templateId]);

  return <>{children}</>;
}

export function WizardLayout() {
  return (
    <WizardProvider>
      <WizardDataLoader>
        <div className="max-w-5xl mx-auto">
          <WizardStepper />
          <Outlet />
        </div>
      </WizardDataLoader>
    </WizardProvider>
  );
}
