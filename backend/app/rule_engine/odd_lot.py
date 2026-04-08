"""Step 4: 畸零地初判。"""

import math

from app.rule_engine.base import EvaluationContext, RuleModule
from app.schemas.enums import FinalStatus, SourceType
from app.schemas.evidence import LegalBasis
from app.schemas.output import ModuleResult
from app.versioning.law_registry import ODD_LOT_STANDARDS


class OddLotModule(RuleModule):
    module_name = "odd_lot"

    def evaluate(self, ctx: EvaluationContext) -> ModuleResult:
        area = ctx.raw_input.get("site_area_sqm")
        if area is None:
            r = ModuleResult(
                module=self.module_name, status=FinalStatus.REVIEW_REQUIRED,
                result={"is_odd_lot_suspect": None}, review_required=True,
                notes=["基地面積未知，無法判定畸零地"],
            )
            ctx.set_result(self.module_name, r)
            return r
        zoning = ctx.zoning_data or {}
        zone_code = zoning.get("zone_code", "")

        # 決定使用哪組畸零地標準
        if "住" in zone_code:
            standards = ODD_LOT_STANDARDS["住宅區"]
        elif "商" in zone_code:
            standards = ODD_LOT_STANDARDS["商業區"]
        elif "工" in zone_code:
            standards = ODD_LOT_STANDARDS["工業區"]
        else:
            standards = ODD_LOT_STANDARDS["default"]

        min_width = standards["min_width_m"]
        min_depth = standards["min_depth_m"]
        min_frontage = standards["min_frontage_m"]

        # MVP 簡化：用面積反推概略尺寸（假設近正方形）
        estimated_side = math.sqrt(area)

        basis = LegalBasis(
            law_name="臺北市畸零地使用自治條例",
            article="第3條、第6條",
            source_url="https://laws.gov.taipei/Law/LawSearch/LawInformation/FL004107",
            source_type=SourceType.LOCAL_LAW,
        )

        result_data = {
            "site_area_sqm": area,
            "estimated_side_m": round(estimated_side, 2),
            "min_width_m": min_width,
            "min_depth_m": min_depth,
            "min_frontage_m": min_frontage,
        }

        notes = []
        is_suspect = False

        if estimated_side < min_width:
            is_suspect = True
            notes.append(f"估算邊長 {estimated_side:.1f}m < 最小寬度 {min_width}m")
        if estimated_side < min_depth:
            is_suspect = True
            notes.append(f"估算邊長 {estimated_side:.1f}m < 最小深度 {min_depth}m")
        if estimated_side < min_frontage:
            is_suspect = True
            notes.append(f"估算邊長 {estimated_side:.1f}m < 最小臨建築線寬度 {min_frontage}m")

        if is_suspect:
            status = FinalStatus.REVIEW_REQUIRED
            notes.insert(0, "疑似畸零地，建議實測確認尺寸後評估是否需調處或合併鄰地")
            result_data["is_odd_lot_suspect"] = True
        else:
            status = FinalStatus.AUTO_PASS
            notes.append("面積與估算尺寸初判非畸零地")
            result_data["is_odd_lot_suspect"] = False

        r = ModuleResult(
            module=self.module_name,
            status=status,
            result=result_data,
            review_required=is_suspect,
            notes=notes,
            legal_basis=[basis],
        )
        ctx.set_result(self.module_name, r)
        return r
