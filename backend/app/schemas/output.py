from datetime import datetime
from typing import Any

from pydantic import BaseModel

from app.schemas.enums import FinalStatus
from app.schemas.evidence import LegalBasis


class ModuleResult(BaseModel):
    module: str
    status: FinalStatus
    result: dict[str, Any] = {}
    legal_basis: list[LegalBasis] = []
    review_required: bool = False
    notes: list[str] = []


class OverlayRisk(BaseModel):
    risk_type: str
    description: str
    status: FinalStatus
    legal_basis: list[LegalBasis] = []


class ChecklistItem(BaseModel):
    point_number: int
    title: str
    v1_scope: bool
    status: FinalStatus | None = None
    status_text: str = ""
    notes: list[str] = []


class EvaluationReport(BaseModel):
    project_id: str
    site_identity: dict[str, Any]
    module_results: dict[str, ModuleResult] = {}  # 所有模組結果，key = module_name
    overlay_risks: list[OverlayRisk]
    blockers: list[str] = []           # AUTO_FAIL 項目
    high_risk_items: list[str] = []     # HIGH_RISK 項目
    manual_review_items: list[str]      # REVIEW_REQUIRED 項目（真正需人工介入）
    final_status: FinalStatus
    final_status_text: str
    legal_basis: list[LegalBasis]
    source_evidence: list[LegalBasis]
    checklist_19: list[ChecklistItem]
    data_mode: str = "mock"  # "mock" | "live" — 標示資料來源模式
    generated_at: datetime
    rule_version: str
