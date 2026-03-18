import React, { useState } from 'react';
import type { TenantSettings, UpdateBrandingRequest } from '../../types/tenant';

interface BrandingTabProps {
  tenant: TenantSettings;
  onSave: (data: UpdateBrandingRequest) => Promise<void>;
  onDiscard: () => void;
}

const FONT_OPTIONS = [
  { value: 'Montserrat', label: 'Montserrat' },
  { value: 'Inter', label: 'Inter' },
  { value: 'Roboto', label: 'Roboto' },
  { value: 'Open Sans', label: 'Open Sans' },
];

export function BrandingTab({ tenant, onSave, onDiscard }: BrandingTabProps) {
  const [color, setColor] = useState(tenant.primary_color);
  const [font, setFont] = useState(tenant.font_family);
  const [signature, setSignature] = useState(tenant.email_signature || '');
  const [saving, setSaving] = useState(false);

  const handleSave = async () => {
    setSaving(true);
    try {
      await onSave({ primary_color: color, font_family: font, email_signature: signature });
    } finally {
      setSaving(false);
    }
  };

  const handleDiscard = () => {
    setColor(tenant.primary_color);
    setFont(tenant.font_family);
    setSignature(tenant.email_signature || '');
    onDiscard();
  };

  const handleReset = () => {
    setColor('#5F2CFF');
    setFont('Montserrat');
    setSignature('');
  };

  return (
    <>
      <div className="bg-white rounded-[24px] shadow-[0px_4px_52px_rgba(0,0,0,0.04)] p-10 max-w-5xl">
        <div className="space-y-10">
          {/* Primary Color */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 items-start">
            <div>
              <label className="text-sm font-medium text-[#3D4353]">Primary Brand Color</label>
              <p className="text-xs text-[#7D8494] mt-1">Used for buttons, links, and accents.</p>
            </div>
            <div className="md:col-span-2">
              <div className="flex items-center gap-4">
                <input
                  type="color"
                  value={color}
                  onChange={(e) => setColor(e.target.value)}
                  className="w-12 h-12 rounded-lg border border-[#CFD0D6] cursor-pointer p-1"
                />
                <input
                  type="text"
                  value={color}
                  onChange={(e) => setColor(e.target.value)}
                  className="w-32 h-12 rounded-[8px] border-[#CFD0D6] text-sm text-[#3D4353] focus:ring-primary focus:border-primary px-4 uppercase"
                  maxLength={7}
                />
                <div
                  className="h-12 flex-1 rounded-[8px] border border-[#CFD0D6]"
                  style={{ backgroundColor: color }}
                />
              </div>
            </div>
          </div>

          {/* Favicon */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 items-start">
            <div>
              <label className="text-sm font-medium text-[#3D4353]">Favicon</label>
              <p className="text-xs text-[#7D8494] mt-1">Shown in browser tabs (SVG/PNG/ICO, max 512x512).</p>
            </div>
            <div className="md:col-span-2">
              <div className="flex items-center gap-6 p-6 border-2 border-dashed border-[#CFD0D6] rounded-[24px] bg-gray-50/50">
                <div className="w-16 h-16 bg-white border border-[#CFD0D6] rounded-lg flex items-center justify-center shadow-sm shrink-0">
                  {tenant.favicon_url ? (
                    <img alt="Favicon preview" className="w-8 h-8 object-contain" src={tenant.favicon_url} />
                  ) : (
                    <span className="material-symbols-outlined text-2xl text-slate-300">image</span>
                  )}
                </div>
                <div>
                  <button className="bg-white border border-primary text-primary px-5 py-2.5 rounded-[8px] text-sm font-semibold hover:bg-primary hover:text-white transition-all">
                    Upload Favicon
                  </button>
                  <p className="text-xs text-[#7D8494] mt-2">SVG, PNG, ICO (max 512x512)</p>
                </div>
              </div>
            </div>
          </div>

          {/* Font Family */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 items-start">
            <div>
              <label className="text-sm font-medium text-[#3D4353]">Font Family</label>
              <p className="text-xs text-[#7D8494] mt-1">Primary font used throughout the platform.</p>
            </div>
            <div className="md:col-span-2">
              <div className="space-y-3">
                {FONT_OPTIONS.map((opt) => (
                  <label
                    key={opt.value}
                    className={`flex items-center gap-3 p-3 rounded-lg border cursor-pointer transition-all ${
                      font === opt.value
                        ? 'border-primary bg-primary/5'
                        : 'border-[#CFD0D6] hover:border-primary/50'
                    }`}
                  >
                    <input
                      type="radio"
                      name="font"
                      value={opt.value}
                      checked={font === opt.value}
                      onChange={() => setFont(opt.value)}
                      className="text-primary focus:ring-primary"
                    />
                    <span className="text-sm font-medium text-[#3D4353]" style={{ fontFamily: opt.value }}>
                      {opt.label}
                    </span>
                    <span className="text-xs text-[#7D8494] ml-auto" style={{ fontFamily: opt.value }}>
                      The quick brown fox
                    </span>
                  </label>
                ))}
              </div>
            </div>
          </div>

          {/* Email Signature */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 items-start">
            <div>
              <label className="text-sm font-medium text-[#3D4353]">Email Signature</label>
              <p className="text-xs text-[#7D8494] mt-1">Appended to all automated emails.</p>
            </div>
            <div className="md:col-span-2">
              <textarea
                className="w-full h-32 rounded-[8px] border-[#CFD0D6] text-sm text-[#3D4353] focus:ring-primary focus:border-primary px-4 py-3 resize-none"
                placeholder="Enter your organization's email signature..."
                value={signature}
                onChange={(e) => setSignature(e.target.value)}
              />
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
        <div className="flex gap-4">
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
