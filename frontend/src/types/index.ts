export type FinalStatus = 'AUTO_PASS' | 'AUTO_FAIL' | 'REVIEW_REQUIRED' | 'HIGH_RISK'

export type IntendedUse = 'residential' | 'office' | 'commercial' | 'hotel' | 'industrial_office'

export type DevelopmentScheme = 'general' | 'urban_renewal' | 'dangerous_old'

export interface SiteInput {
  address_or_lot: string
  site_area_sqm?: number | null
  intended_use: IntendedUse
  single_owner?: boolean | null
  can_merge_adjacent?: boolean | null
  has_existing_building?: boolean | null
  has_permit?: boolean | null
  development_scheme?: DevelopmentScheme | null
}

export interface LegalBasis {
  law_name: string
  article: string
  source_url: string
  source_type: string
  is_official_proof: boolean
  review_required: boolean
  notes: string[]
}

export interface ModuleResult {
  module: string
  status: FinalStatus
  result: Record<string, unknown>
  legal_basis: LegalBasis[]
  review_required: boolean
  notes: string[]
}

export interface OverlayRisk {
  risk_type: string
  description: string
  status: FinalStatus
  legal_basis: LegalBasis[]
}

export interface ChecklistItem {
  point_number: number
  title: string
  v1_scope: boolean
  status: FinalStatus | null
  status_text: string
  notes: string[]
}

export interface EvaluationReport {
  project_id: string
  site_identity: Record<string, unknown>
  module_results: Record<string, ModuleResult>
  overlay_risks: OverlayRisk[]
  blockers: string[]
  high_risk_items: string[]
  manual_review_items: string[]
  final_status: FinalStatus
  final_status_text: string
  legal_basis: LegalBasis[]
  source_evidence: LegalBasis[]
  checklist_19: ChecklistItem[]
  data_mode: string
  generated_at: string
  rule_version: string
}
