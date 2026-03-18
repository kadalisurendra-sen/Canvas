import React, { useEffect } from 'react';
import { Outlet, useParams } from 'react-router-dom';
import { WizardProvider, useWizard } from '../../context/WizardContext';
import { WizardStepper } from './WizardStepper';
import { fetchTemplate } from '../../services/templateService';

function WizardDataLoader({ children }: { children: React.ReactNode }) {
  const { id } = useParams<{ id: string }>();
  const { setTemplateId, setGeneralInfo, setStages, setIsEditing } = useWizard();

  useEffect(() => {
    if (!id) return;
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
          setStages(tpl.stages);
        }
      } catch {
        // Template load failed - user can still create from scratch
      }
    }

    loadTemplate();
    return () => { cancelled = true; };
  }, [id, setTemplateId, setGeneralInfo, setStages, setIsEditing]);

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
