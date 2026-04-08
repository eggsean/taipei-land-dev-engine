"""第9點：容積移轉可行性初判。

自動化邏輯：
- 依分區判定是否可接受容積移轉
- 計算移入上限（法定容積之 30%）
- 工業區不適用 → AUTO_FAIL
- 可接受移轉 → AUTO_PASS（標示上限）
"""

from app.rule_engine.base import EvaluationContext, RuleModule
from app.schemas.enums import FinalStatus, SourceType
from app.schemas.evidence import LegalBasis
from app.schemas.output import ModuleResult

# 不適用容積移轉的分區
NO_TRANSFER_ZONES = ["工二", "工三"]

# 容積移轉上限
TRANSFER_CAP_PCT = 30  # 法定容積之 30%


class FarTransferModule(RuleModule):
    module_name = "far_transfer"

    def evaluate(self, ctx: EvaluationContext) -> ModuleResult:
        zoning = ctx.zoning_data or {}
        zone_code = zoning.get("zone_code", "")
        base_far = zoning.get("base_far", 0)
        area = ctx.raw_input.get("site_area_sqm", 0)

        max_transfer_far = base_far * TRANSFER_CAP_PCT / 100
        max_transfer_area = area * max_transfer_far / 100

        basis = LegalBasis(
            law_name="都市計畫容積移轉實施辦法",
            article="第6條、第7條",
            source_url="https://law.moj.gov.tw/",
            source_type=SourceType.CENTRAL_LAW,
        )

        if zone_code in NO_TRANSFER_ZONES:
            r = ModuleResult(
                module=self.module_name,
                status=FinalStatus.AUTO_FAIL,
                result={"zone_code": zone_code, "transferable": False},
                review_required=False,
                notes=[f"分區 {zone_code} 不適用容積移轉"],
                legal_basis=[basis],
            )
            ctx.set_result(self.module_name, r)
            return r

        notes = [
            f"基準容積率: {base_far}%",
            f"容積移轉接受上限: 法定容積之 {TRANSFER_CAP_PCT}%（= {max_transfer_far:.1f}%）",
            f"最大可移入樓地板面積: 約 {max_transfer_area:,.1f} m²",
            f"移入後最大容積率: {base_far + max_transfer_far:.1f}%",
            "容積移轉需有合格送出基地（如公共設施保留地等）",
            "移轉價格依市場行情，需另行評估成本",
        ]

        r = ModuleResult(
            module=self.module_name,
            status=FinalStatus.AUTO_PASS,
            result={
                "zone_code": zone_code,
                "transferable": True,
                "max_transfer_pct": TRANSFER_CAP_PCT,
                "max_transfer_far": round(max_transfer_far, 2),
                "max_transfer_area_sqm": round(max_transfer_area, 2),
                "effective_max_far": round(base_far + max_transfer_far, 2),
            },
            review_required=False,
            notes=notes,
            legal_basis=[basis],
        )
        ctx.set_result(self.module_name, r)
        return r
