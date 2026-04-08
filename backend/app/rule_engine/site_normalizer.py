"""Step 1: 基地正規化 — 地址/地號標準化、建立基地識別碼。"""

import hashlib
import re

from app.rule_engine.base import EvaluationContext, RuleModule
from app.schemas.enums import FinalStatus, SourceType
from app.schemas.evidence import LegalBasis
from app.schemas.output import ModuleResult


class SiteNormalizer(RuleModule):
    module_name = "site_normalizer"

    def evaluate(self, ctx: EvaluationContext) -> ModuleResult:
        raw = ctx.raw_input["address_or_lot"]
        area = ctx.raw_input.get("site_area_sqm")

        if ctx.raw_input.get("_area_missing"):
            area_source = "查無資料"
        elif ctx.raw_input.get("_area_auto"):
            area_source = "系統自動查詢"
        else:
            area_source = "使用者輸入"

        # 判斷是地號還是地址
        is_lot = bool(re.search(r"[段小]段|地號", raw))
        normalized = raw.strip().replace("　", "").replace(" ", "")

        # 產生唯一識別碼
        site_hash = hashlib.md5(normalized.encode()).hexdigest()[:12]
        project_id = f"TPE-{site_hash}"

        ctx.site_identity = {
            "raw_input": raw,
            "normalized": normalized,
            "input_type": "lot_number" if is_lot else "address",
            "site_area_sqm": area,
            "area_source": area_source,
            "project_id": project_id,
        }

        notes = [
            f"識別碼: {project_id}",
            f"輸入類型: {'地號' if is_lot else '地址'}",
            f"基地面積: {area} m²（{area_source}）",
        ]

        result = ModuleResult(
            module=self.module_name,
            status=FinalStatus.AUTO_PASS,
            result=ctx.site_identity,
            legal_basis=[
                LegalBasis(
                    law_name="基地正規化（系統內部）",
                    article="N/A",
                    source_url="",
                    source_type=SourceType.SYSTEM_QUERY,
                )
            ],
            notes=notes,
        )
        ctx.set_result(self.module_name, result)
        return result
