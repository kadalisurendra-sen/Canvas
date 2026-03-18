export type TemplateStatus = 'draft' | 'published' | 'archived';
export type FieldType = 'text_short' | 'text_long' | 'single_select' | 'multi_select' | 'number' | 'date';
export type FailAction = 'warn' | 'block' | 'allow';

export interface FieldOption {
  id?: string;
  label: string;
  value: string;
  score: number;
  sort_order: number;
}

export interface TemplateField {
  id?: string;
  field_key: string;
  label: string;
  field_type: FieldType;
  help_text?: string;
  is_mandatory: boolean;
  is_scoring: boolean;
  sort_order: number;
  options: FieldOption[];
}

export interface TemplateSection {
  id?: string;
  name: string;
  sort_order: number;
  fields: TemplateField[];
}

export interface TemplateStage {
  id?: string;
  name: string;
  sort_order: number;
  weight_pct: number;
  min_pass_score: number | null;
  fail_action: FailAction;
  sections: TemplateSection[];
}

export interface TemplateTag {
  id?: string;
  tag: string;
}

export interface Template {
  id: string;
  name: string;
  category: string;
  description?: string;
  icon?: string;
  theme_color?: string;
  status: TemplateStatus;
  version: number;
  created_by: string;
  created_at: string;
  updated_at: string;
  tags: TemplateTag[];
  stages: TemplateStage[];
}

export interface TemplateListItem {
  id: string;
  name: string;
  category: string;
  description?: string;
  icon?: string;
  theme_color?: string;
  status: TemplateStatus;
  version: number;
  created_by: string;
  created_at: string;
  updated_at: string;
  stage_count: number;
  field_count: number;
  tags: string[];
}

export interface TemplateListResponse {
  items: TemplateListItem[];
  total: number;
  page: number;
  page_size: number;
}

export interface TemplateCreatePayload {
  name: string;
  category: string;
  description?: string;
  icon?: string;
  theme_color?: string;
  tags: string[];
}

export interface StageInput {
  name: string;
  sort_order: number;
}

export interface ScoringStageInput {
  stage_id: string;
  weight_pct: number;
  min_pass_score: number | null;
  fail_action: FailAction;
}

export interface FieldsUpdateStage {
  stage_id: string;
  sections: TemplateSection[];
}
