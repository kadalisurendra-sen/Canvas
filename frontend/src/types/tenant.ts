export interface TenantDefaults {
  default_currency: string;
  standard_roi_period: string;
  min_feasibility_threshold: number;
  required_ethics_level: string;
}

export interface TenantSettings {
  id: string;
  name: string;
  slug: string;
  logo_url: string | null;
  timezone: string;
  default_language: string;
  default_template: string | null;
  is_active: boolean;
  primary_color: string;
  favicon_url: string | null;
  font_family: string;
  email_signature: string | null;
  defaults: TenantDefaults;
}

export interface UpdateGeneralRequest {
  name?: string;
  timezone?: string;
  default_language?: string;
  default_template?: string;
}

export interface UpdateBrandingRequest {
  primary_color?: string;
  font_family?: string;
  email_signature?: string;
}

export interface UpdateDefaultsRequest {
  default_currency?: string;
  standard_roi_period?: string;
  min_feasibility_threshold?: number;
  required_ethics_level?: string;
}
