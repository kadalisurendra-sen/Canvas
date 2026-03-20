import React, { useEffect, useState } from 'react';
import type { TenantSettings, UpdateGeneralRequest } from '../../types/tenant';

interface GeneralTabProps {
  tenant: TenantSettings;
  onSave: (data: UpdateGeneralRequest) => Promise<void>;
  onDiscard: () => void;
}

export function GeneralTab({ tenant, onSave, onDiscard }: GeneralTabProps) {
  const [name, setName] = useState(tenant.name);
  const [timezone, setTimezone] = useState(tenant.timezone);
  const [language, setLanguage] = useState(tenant.default_language);
  const [template, setTemplate] = useState(tenant.default_template || '');
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  // Sync when tenant data loads/changes
  useEffect(() => {
    setName(tenant.name);
    setTimezone(tenant.timezone);
    setLanguage(tenant.default_language);
    setTemplate(tenant.default_template || '');
  }, [tenant]);

  const handleSave = async () => {
    setSaving(true);
    setSaved(false);
    try {
      await onSave({ name, timezone, default_language: language });
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    } finally {
      setSaving(false);
    }
  };

  const handleDiscard = () => {
    setName(tenant.name);
    setTimezone(tenant.timezone);
    setLanguage(tenant.default_language);
    setTemplate(tenant.default_template || '');
    onDiscard();
  };

  const handleReset = () => {
    setName(tenant.name);
    setTimezone('UTC');
    setLanguage('en');
    setTemplate('');
  };

  return (
    <>
      <div className="bg-white rounded-[24px] shadow-[0px_4px_52px_rgba(0,0,0,0.04)] p-10 max-w-5xl">
        <div className="space-y-10">
          {/* Organization Name */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 items-start">
            <div>
              <label className="text-sm font-medium text-[#3D4353]">Organization Name</label>
              <p className="text-xs text-[#7D8494] mt-1">Visible to all users in the workspace.</p>
            </div>
            <div className="md:col-span-2">
              <input
                className="w-full h-12 rounded-[8px] border-[#CFD0D6] text-sm text-[#3D4353] focus:ring-primary focus:border-primary px-4"
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
              />
            </div>
          </div>

          {/* Logo Upload */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 items-start">
            <div>
              <label className="text-sm font-medium text-[#3D4353]">Organization Logo</label>
              <p className="text-xs text-[#7D8494] mt-1">Company branding for reports and dashboard headers.</p>
            </div>
            <div className="md:col-span-2">
              <div className="flex flex-col md:flex-row items-center gap-8 p-8 border-2 border-dashed border-[#CFD0D6] rounded-[24px] bg-gray-50/50">
                <div className="w-24 h-24 bg-white border border-[#CFD0D6] rounded-lg flex items-center justify-center p-3 shadow-sm shrink-0">
                  {tenant.logo_url ? (
                    <img alt="Current logo preview" className="max-w-full max-h-full object-contain" src={tenant.logo_url} />
                  ) : (
                    <span className="material-symbols-outlined text-4xl text-slate-300">image</span>
                  )}
                </div>
                <div className="flex-1 text-center md:text-left">
                  <button className="bg-white border border-primary text-primary px-5 py-2.5 rounded-[8px] text-sm font-semibold hover:bg-primary hover:text-white transition-all">
                    Upload New Logo
                  </button>
                  <p className="text-xs text-[#7D8494] mt-3">PNG, SVG (max 2MB)</p>
                </div>
              </div>
            </div>
          </div>

          {/* Localization */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 items-start pt-4">
            <div>
              <label className="text-sm font-medium text-[#3D4353]">Localization</label>
              <p className="text-xs text-[#7D8494] mt-1">Set the default regional settings for the organization.</p>
            </div>
            <div className="md:col-span-2 space-y-6">
              <div className="space-y-2">
                <span className="text-[14px] font-medium text-[#3D4353]">Timezone</span>
                <select
                  className="w-full h-12 rounded-[8px] border-[#CFD0D6] text-sm text-[#3D4353] focus:ring-primary focus:border-primary px-4"
                  value={timezone}
                  onChange={(e) => setTimezone(e.target.value)}
                >
                  <option value="US/Eastern">UTC-5 (Eastern Time)</option>
                  <option value="US/Pacific">UTC-8 (Pacific Time)</option>
                  <option value="Europe/London">UTC+0 (London)</option>
                  <option value="Asia/Kolkata">UTC+5:30 (India)</option>
                  <option value="UTC">UTC</option>
                </select>
              </div>
              <div className="space-y-2">
                <span className="text-[14px] font-medium text-[#3D4353]">Default Language</span>
                <select
                  className="w-full h-12 rounded-[8px] border-[#CFD0D6] text-sm text-[#3D4353] focus:ring-primary focus:border-primary px-4"
                  value={language}
                  onChange={(e) => setLanguage(e.target.value)}
                >
                  <option value="en">English</option>
                  <option value="es">Spanish</option>
                  <option value="fr">French</option>
                </select>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="mt-auto border-t border-[#CFD0D6] bg-white p-6 flex justify-between items-center -mx-10 px-10">
        <button
          onClick={handleReset}
          className="px-6 py-2.5 rounded-[8px] border border-primary text-primary font-semibold hover:bg-primary/5 transition-colors"
        >
          Reset to Defaults
        </button>
        <div className="flex gap-4 items-center">
          {saved && (
            <span className="text-sm text-emerald-600 font-medium flex items-center gap-1">
              <span className="material-symbols-outlined text-base">check_circle</span>
              Saved
            </span>
          )}
          <button
            onClick={handleDiscard}
            className="px-6 py-2.5 rounded-[8px] text-[#7D8494] font-semibold hover:text-[#3D4353] transition-colors"
          >
            Discard
          </button>
          <button
            onClick={handleSave}
            disabled={saving}
            className="px-10 py-2.5 rounded-[8px] bg-primary text-white font-bold shadow-lg hover:shadow-xl hover:translate-y-[-1px] transition-all active:translate-y-0 disabled:opacity-50"
          >
            {saving ? 'Saving...' : 'Save Changes'}
          </button>
        </div>
      </footer>
    </>
  );
}
