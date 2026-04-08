"""Step 5: 容積率/建蔽率查表。"""

from app.rule_engine.base import EvaluationContext, RuleModule
from app.schemas.enums import FinalStatus, SourceType
from app.schemas.evidence import LegalBasis
from app.schemas.output import ModuleResult


class FarBcrModule(RuleModule):
    module_name = "far_bcr"

    def evaluate(self, ctx: EvaluationContext) -> ModuleResult:
        zoning = ctx.zoning_data
        area = ctx.raw_input["site_area_sqm"]

        basis = LegalBasis(
            law_name="臺北市土地使用分區管制自治條例",
            article="各分區容積率及建蔽率規定",
            source_url="https://laws.gov.taipei/Law/LawSearch/LawInformation/FL003962",
            source_type=SourceType.LOCAL_LAW,
        )

        if not zoning:
            r = ModuleResult(
                module=self.module_name,
                status=FinalStatus.REVIEW_REQUIRED,
                result={},
                review_required=True,
                notes=["無分區資料，無法計算容積與建蔽"],
                legal_basis=[basis],
            )
            ctx.set_result(self.module_name, r)
            ctx.set_result("coverage", r)
            return r

        base_far = zoning["base_far"]
        base_bcr = zoning["base_bcr"]
        max_floor_area = area * base_far / 100
        max_building_area = area * base_bcr / 100

        result_data = {
            "zone_code": zoning["zone_code"],
            "base_far_pct": base_far,
            "base_bcr_pct": base_bcr,
            "site_area_sqm": area,
            "max_total_floor_area_sqm": round(max_floor_area, 2),
            "max_building_area_sqm": round(max_building_area, 2),
        }

        r = ModuleResult(
            module=self.module_name,
            status=FinalStatus.AUTO_PASS,
            result=result_data,
            notes=[
                f"法定容積率 {base_far}%，最大總樓地板面積 {max_floor_area:,.1f} m²",
                f"法定建蔽率 {base_bcr}%，最大建築面積 {max_building_area:,.1f} m²",
            ],
            legal_basis=[basis],
        )
        ctx.set_result(self.module_name, r)
        # coverage 共用 far_bcr 結果
        ctx.set_result("coverage", r)
        return r
