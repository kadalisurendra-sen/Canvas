import React, { useState } from 'react';
import type { TenantSettings, UpdateDefaultsRequest } from '../../types/tenant';

interface DefaultsTabProps {
  tenant: TenantSettings;
  onSave: (data: UpdateDefaultsRequest) => Promise<void>;
  onDiscard: () => void;
}

export function DefaultsTab({ tenant, onSave, onDiscard }: DefaultsTabProps) {
  const defaults = tenant.defaults;
  const [currency, setCurrency] = useState(defaults.default_currency);
  const [roiPeriod, setRoiPeriod] = useState(defaults.standard_roi_period);
  const [threshold, setThreshold] = useState(defaults.min_feasibility_threshold);
  const [ethicsLevel, setEthicsLevel] = useState(defaults.required_ethics_level);
  const [saving, setSaving] = useState(false);

  const handleSave = async () => {
    setSaving(true);
    try {
      await onSave({
        default_currency: currency,
        standard_roi_period: roiPeriod,
        min_feasibility_threshold: threshold,
        required_ethics_level: ethicsLevel,
      });
    } finally {
      setSaving(false);
    }
  };

  const handleDiscard = () => {
    setCurrency(defaults.default_currency);
    setRoiPeriod(defaults.standard_roi_period);
    setThreshold(defaults.min_feasibility_threshold);
    setEthicsLevel(defaults.required_ethics_level);
    onDiscard();
  };

  const handleReset = () => {
    setCurrency('USD');
    setRoiPeriod('3 Years');
    setThreshold(65);
    setEthicsLevel('Level 3 - Enterprise Standard');
  };

  return (
    <>
      <div className="bg-white rounded-bl-[48px] shadow-[0px_4px_52px_rgba(0,0,0,0.04)] p-10 max-w-5xl">
        <div className="space-y-10">
          {/* Default Currency */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 items-center">
            <div>
              <label className="text-sm font-medium text-[#3D4353]">Default Currency</label>
              <p className="text-xs text-[#6D7283] mt-1">Primary currency for calculations.</p>
            </div>
            <div className="md:col-span-2">
              <select
                className="w-full max-w-sm rounded-[8px] border-[#CFD0D6] text-sm text-[#3D4353] focus:ring-primary focus:border-primary py-3 px-4"
                value={currency}
                onChange={(e) => setCurrency(e.target.value)}
              >
                <option value="USD">USD - US Dollar</option>
                <option value="EUR">EUR - Euro</option>
                <option value="GBP">GBP - British Pound</option>
              </select>
            </div>
          </div>

          {/* Standard ROI Period */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 items-center">
            <div>
              <label className="text-sm font-medium text-[#3D4353]">Standard ROI Period</label>
              <p className="text-xs text-[#6D7283] mt-1">Default calculation timeline.</p>
            </div>
            <div className="md:col-span-2">
              <select
                className="w-full max-w-sm rounded-[8px] border-[#CFD0D6] text-sm text-[#3D4353] focus:ring-primary focus:border-primary py-3 px-4"
                value={roiPeriod}
                onChange={(e) => setRoiPeriod(e.target.value)}
              >
                <option>1 Year</option>
                <option>2 Years</option>
                <option>3 Years</option>
                <option>5 Years</option>
              </select>
            </div>
          </div>

          {/* Minimum Feasibility Threshold */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 items-center">
            <div>
              <label className="text-sm font-medium text-[#3D4353]">Minimum Feasibility Threshold</label>
              <p className="text-xs text-[#6D7283] mt-1">Score required for viability.</p>
            </div>
            <div className="md:col-span-2">
              <div className="flex items-center gap-6 max-w-md">
                <input
                  className="flex-1 accent-primary"
                  type="range"
                  min="0"
                  max="100"
                  value={threshold}
                  onChange={(e) => setThreshold(Number(e.target.value))}
                />
                <div className="relative w-24">
                  <input
                    className="w-full rounded-[8px] border-[#CFD0D6] text-[#3D4353] text-right focus:ring-primary focus:border-primary py-2 px-3 pr-8 font-semibold text-sm"
                    type="number"
                    min={0}
                    max={100}
                    value={threshold}
                    onChange={(e) => setThreshold(Number(e.target.value))}
                  />
                  <span className="absolute right-3 top-1/2 -translate-y-1/2 text-xs font-medium text-[#6D7283]">
                    %
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Required Ethics Level */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 items-center">
            <div>
              <label className="text-sm font-medium text-[#3D4353]">Required Ethics Level</label>
              <p className="text-xs text-[#6D7283] mt-1">Minimum compliance standards.</p>
            </div>
            <div className="md:col-span-2">
              <select
                className="w-full max-w-sm rounded-[8px] border-[#CFD0D6] text-sm text-[#3D4353] focus:ring-primary focus:border-primary py-3 px-4"
                value={ethicsLevel}
                onChange={(e) => setEthicsLevel(e.target.value)}
              >
                <option>Level 1 - Minimal Risk</option>
                <option>Level 2 - Balanced</option>
                <option>Level 3 - Enterprise Standard</option>
                <option>Level 4 - High Oversight</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="mt-auto bg-white border-t border-[#E2E8F0] p-6 flex justify-between items-center -mx-10 px-10">
        <button
          onClick={handleReset}
          className="px-6 py-2.5 rounded-[8px] border border-primary text-primary font-bold text-sm hover:bg-primary/5 transition-colors"
        >
          Reset to Defaults
        </button>
        <div className="flex items-center gap-6">
          <button
            onClick={handleDiscard}
            className="text-[#6D7283] font-bold text-sm hover:text-[#151C28] transition-colors"
          >
            Discard
          </button>
          <button
            onClick={handleSave}
            disabled={saving}
            className="px-8 py-3 rounded-[8px] bg-primary text-white font-bold text-sm shadow-lg shadow-primary/20 hover:bg-[#4a22cc] transition-all disabled:opacity-50"
          >
            {saving ? 'Saving...' : 'Save Configuration'}
          </button>
        </div>
      </div>
    </>
  );
}
