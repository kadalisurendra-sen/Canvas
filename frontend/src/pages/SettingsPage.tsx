import React, { useCallback, useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import type { TenantSettings, UpdateBrandingRequest, UpdateDefaultsRequest, UpdateGeneralRequest } from '../types/tenant';
import { fetchTenant, updateBranding, updateDefaults, updateGeneral } from '../services/tenantService';
import { GeneralTab } from '../components/tenant/GeneralTab';
import { BrandingTab } from '../components/tenant/BrandingTab';
import { DefaultsTab } from '../components/tenant/DefaultsTab';

type TabName = 'general' | 'branding' | 'defaults';

const TABS: { key: TabName; label: string }[] = [
  { key: 'general', label: 'General' },
  { key: 'branding', label: 'Branding' },
  { key: 'defaults', label: 'Defaults' },
];

const DEFAULT_TENANT: TenantSettings = {
  id: '',
  name: 'Acme Corporation',
  slug: 'acme',
  logo_url: null,
  timezone: 'US/Eastern',
  default_language: 'en',
  default_template: null,
  is_active: true,
  primary_color: '#5F2CFF',
  favicon_url: null,
  font_family: 'Montserrat',
  email_signature: null,
  defaults: {
    default_currency: 'USD',
    standard_roi_period: '3 Years',
    min_feasibility_threshold: 65,
    required_ethics_level: 'Level 3 - Enterprise Standard',
  },
};

export function SettingsPage() {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState<TabName>('general');
  const [tenant, setTenant] = useState<TenantSettings>(DEFAULT_TENANT);
  const [loading, setLoading] = useState(false);

  const loadTenant = useCallback(async () => {
    if (!user?.tenant_id) return;
    setLoading(true);
    try {
      const data = await fetchTenant(user.tenant_id);
      setTenant(data);
    } catch {
      // Use default data if API unavailable
    } finally {
      setLoading(false);
    }
  }, [user?.tenant_id]);

  useEffect(() => {
    loadTenant();
  }, [loadTenant]);

  const handleSaveGeneral = async (data: UpdateGeneralRequest) => {
    if (!user?.tenant_id) return;
    try {
      await updateGeneral(user.tenant_id, data);
      await loadTenant();
    } catch {
      // handle error
    }
  };

  const handleSaveBranding = async (data: UpdateBrandingRequest) => {
    if (!user?.tenant_id) return;
    try {
      await updateBranding(user.tenant_id, data);
      await loadTenant();
    } catch {
      // handle error
    }
  };

  const handleSaveDefaults = async (data: UpdateDefaultsRequest) => {
    if (!user?.tenant_id) return;
    try {
      await updateDefaults(user.tenant_id, data);
      await loadTenant();
    } catch {
      // handle error
    }
  };

  const isSystemAdmin = user?.roles.includes('system_admin');

  return (
    <div className="flex-1 flex flex-col">
      {/* Header area */}
      <div className="px-10 pt-10 pb-6">
        {isSystemAdmin && (
          <div className="mb-4">
            <a
              className="inline-flex items-center text-sm font-medium text-[#7D8494] hover:text-primary transition-colors cursor-pointer"
              href="#"
            >
              <span className="material-symbols-outlined text-base mr-2">arrow_back</span>
              Back to All Tenants
            </a>
          </div>
        )}
        <h2 className="text-[32px] font-bold text-[#1E2345]">{tenant.name}</h2>
      </div>

      {/* Tabs */}
      <div className="px-10 flex gap-1">
        {TABS.map((tab) => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key)}
            className={`px-8 py-3 text-sm font-bold rounded-t-lg transition-all ${
              activeTab === tab.key
                ? 'bg-primary text-white shadow-lg'
                : 'bg-[#38369A] text-white/70 hover:text-white'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div className="px-10 pb-10 flex flex-col flex-1">
        {loading ? (
          <div className="bg-white rounded-[24px] shadow-sm p-10 max-w-5xl flex items-center justify-center">
            <span className="text-slate-400">Loading settings...</span>
          </div>
        ) : (
          <>
            {activeTab === 'general' && (
              <GeneralTab
                tenant={tenant}
                onSave={handleSaveGeneral}
                onDiscard={loadTenant}
              />
            )}
            {activeTab === 'branding' && (
              <BrandingTab
                tenant={tenant}
                onSave={handleSaveBranding}
                onDiscard={loadTenant}
              />
            )}
            {activeTab === 'defaults' && (
              <DefaultsTab
                tenant={tenant}
                onSave={handleSaveDefaults}
                onDiscard={loadTenant}
              />
            )}
          </>
        )}
      </div>
    </div>
  );
}
