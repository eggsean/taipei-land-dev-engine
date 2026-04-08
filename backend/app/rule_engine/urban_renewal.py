"""第18點：都市更新 / 危老重建審議初判。

自動化邏輯：
- 一般開發（非都更/危老）→ AUTO_PASS（不涉及此審議）
- 都更：面積 >= 1000m² → AUTO_PASS（符合自劃門檻）；< 500m² → HIGH_RISK
- 危老：有既有建物 → AUTO_PASS；無建物 → AUTO_FAIL
"""

from app.rule_engine.base import EvaluationContext, RuleModule
from app.schemas.enums import FinalStatus, SourceType
from app.schemas.evidence import LegalBasis
from app.schemas.output import ModuleResult


class UrbanRenewalModule(RuleModule):
    module_name = "urban_renewal"

    def evaluate(self, ctx: EvaluationContext) -> ModuleResult:
        scheme = ctx.raw_input.get("development_scheme") or "general"
        has_building = ctx.raw_input.get("has_existing_building")
        area = ctx.raw_input.get("site_area_sqm") or 0

        notes = []
        result_data = {"development_scheme": scheme, "site_area_sqm": area}

        if scheme == "general":
            notes.append("一般開發，不涉及都更/危老審議程序")
            status = FinalStatus.AUTO_PASS
            basis = [LegalBasis(
                law_name="都市更新條例 / 危老條例",
                article="適用性初判",
                source_url="https://law.moj.gov.tw/",
                source_type=SourceType.CENTRAL_LAW,
            )]

        elif scheme == "urban_renewal":
            basis = [LegalBasis(
                law_name="都市更新條例",
                article="第22條、第65條",
                source_url="https://law.moj.gov.tw/",
                source_type=SourceType.CENTRAL_LAW,
            )]
            notes.append("都市更新制度")
            if area >= 1000:
                status = FinalStatus.AUTO_PASS
                notes.append(f"面積 {area} m² >= 1000 m²，符合自行劃定更新單元基本門檻")
                result_data["meets_minimum_area"] = True
            elif area >= 500:
                status = FinalStatus.HIGH_RISK
                notes.append(f"面積 {area} m² 介於 500~1000 m²，自劃更新單元需符合額外條件")
                result_data["meets_minimum_area"] = False
            else:
                status = FinalStatus.HIGH_RISK
                notes.append(f"面積 {area} m² < 500 m²，自劃更新單元困難")
                result_data["meets_minimum_area"] = False

            notes.append("都更時程：約 3-5 年（含整合、審議、施工）")
            notes.append("需取得一定比例所有權人同意")

        elif scheme == "dangerous_old":
            basis = [LegalBasis(
                law_name="都市危險及老舊建築物加速重建條例",
                article="第3條、第6條",
                source_url="https://law.moj.gov.tw/",
                source_type=SourceType.CENTRAL_LAW,
            )]
            notes.append("危老重建制度")
            if has_building is False:
                status = FinalStatus.AUTO_FAIL
                notes.append("未標示有既有建物，危老重建前提為既有合法建物")
            elif has_building is True:
                status = FinalStatus.AUTO_PASS
                notes.append("有既有建物，符合危老重建基本前提")
                notes.append("需經結構安全性能評估認定為危險或老舊")
                notes.append("需取得全體土地及合法建物所有權人同意")
            else:
                status = FinalStatus.HIGH_RISK
                notes.append("未確認是否有既有建物，請補充資訊")

            notes.append("危老時程：約 1-2 年（較都更快速）")
            notes.append("時程獎勵逐年遞減，建議儘早申請")
        else:
            status = FinalStatus.AUTO_PASS
            notes.append("未指定特殊開發制度")
            basis = [LegalBasis(
                law_name="都市更新條例 / 危老條例",
                article="適用性初判",
                source_url="https://law.moj.gov.tw/",
                source_type=SourceType.CENTRAL_LAW,
            )]

        r = ModuleResult(
            module=self.module_name,
            status=status,
            result=result_data,
            review_required=status not in (FinalStatus.AUTO_PASS, FinalStatus.AUTO_FAIL),
            notes=notes,
            legal_basis=basis,
        )
        ctx.set_result(self.module_name, r)
        return r
