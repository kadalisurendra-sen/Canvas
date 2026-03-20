import React, { useCallback, useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useParams, useNavigate } from 'react-router-dom';
import type { TenantSettings, UpdateBrandingRequest, UpdateDefaultsRequest, UpdateGeneralRequest } from '../types/tenant';
import { fetchTenant, updateBranding, updateDefaults, updateGeneral } from '../services/tenantService';
import { GeneralTab } from '../components/tenant/GeneralTab';
import { BrandingTab } from '../components/tenant/BrandingTab';
import { DefaultsTab } from '../components/tenant/DefaultsTab';
import { TenantListPage } from '../components/tenant/TenantListPage';
import { getTenantId } from '../services/api';

type TabName = 'general' | 'branding' | 'defaults';

const TABS: { key: TabName; label: string }[] = [
  { key: 'general', label: 'General' },
  { key: 'branding', label: 'Branding' },
  { key: 'defaults', label: 'Defaults' },
];

const DEFAULT_TENANT: TenantSettings = {
  id: '',
  name: '',
  slug: '',
  logo_url: null,
  timezone: 'UTC',
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
  const { tenantId } = useParams<{ tenantId: string }>();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState<TabName>('general');
  const [tenant, setTenant] = useState<TenantSettings>(DEFAULT_TENANT);
  const [loading, setLoading] = useState(false);

  const isSuperAdmin = user?.roles.includes('system_admin');

  // If super admin and no tenantId in URL, show tenant list
  const showList = isSuperAdmin && !tenantId;

  const [resolvedTenantId, setResolvedTenantId] = useState(tenantId || '');

  // Resolve tenant ID from slug if not provided via URL
  useEffect(() => {
    if (tenantId) {
      setResolvedTenantId(tenantId);
      return;
    }
    if (showList) return;

    // For non-super-admin users, resolve from localStorage slug
    const slug = getTenantId();
    if (slug) {
      fetch(`/api/v1/tenants/resolve?slug=${slug}`)
        .then((r) => r.ok ? r.json() : null)
        .then((data) => {
          if (data) {
            // Use slug to find tenant ID from /tenants/list
            fetch('/api/v1/tenants/list')
              .then((r) => r.json())
              .then((tenants) => {
                const match = tenants.find((t: { slug: string }) => t.slug === slug);
                if (match) setResolvedTenantId(match.id);
              })
              .catch(() => {});
          }
        })
        .catch(() => {});
    }
  }, [tenantId, showList]);

  const loadTenant = useCallback(async () => {
    if (!resolvedTenantId || showList) return;
    setLoading(true);
    try {
      const data = await fetchTenant(resolvedTenantId);
      setTenant(data);
    } catch {
      // Use default data if API unavailable
    } finally {
      setLoading(false);
    }
  }, [resolvedTenantId, showList]);

  useEffect(() => {
    loadTenant();
  }, [loadTenant]);

  const handleSaveGeneral = async (data: UpdateGeneralRequest) => {
    if (!resolvedTenantId) return;
    try {
      await updateGeneral(resolvedTenantId, data);
      await loadTenant();
    } catch {
      // handle error
    }
  };

  const handleSaveBranding = async (data: UpdateBrandingRequest) => {
    if (!resolvedTenantId) return;
    try {
      await updateBranding(resolvedTenantId, data);
      await loadTenant();
    } catch {
      // handle error
    }
  };

  const handleSaveDefaults = async (data: UpdateDefaultsRequest) => {
    if (!resolvedTenantId) return;
    try {
      await updateDefaults(resolvedTenantId, data);
      await loadTenant();
    } catch {
      // handle error
    }
  };

  // Super admin without tenantId → show tenant list
  if (showList) {
    return <TenantListPage />;
  }

  return (
    <div className="flex-1 flex flex-col">
      {/* Header area */}
      <div className="px-10 pt-10 pb-6">
        {isSuperAdmin && tenantId && (
          <div className="mb-4">
            <button
              onClick={() => navigate('/settings')}
              className="inline-flex items-center text-sm font-medium text-[#7D8494] hover:text-primary transition-colors"
            >
              <span className="material-symbols-outlined text-base mr-2">arrow_back</span>
              Back to All Tenants
            </button>
          </div>
        )}
        <h2 className="text-[32px] font-bold text-[#1E2345]">
          {tenant.name || 'Tenant Settings'}
        </h2>
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
