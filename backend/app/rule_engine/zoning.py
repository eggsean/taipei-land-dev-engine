"""Step 2: 都市計畫/分區判定 + 用途合法性檢查。"""

from app.data_sources.base import DataSource
from app.rule_engine.base import EvaluationContext, RuleModule
from app.schemas.enums import FinalStatus, SourceType
from app.schemas.evidence import LegalBasis
from app.schemas.output import ModuleResult

USE_LABEL = {
    "residential": "住宅",
    "office": "辦公",
    "commercial": "商業",
    "hotel": "旅館",
    "industrial_office": "廠辦",
}


class ZoningModule(RuleModule):
    module_name = "zoning"

    def __init__(self, data_source: DataSource) -> None:
        self.ds = data_source

    def evaluate(self, ctx: EvaluationContext) -> ModuleResult:
        address = ctx.site_identity.get("normalized", ctx.raw_input["address_or_lot"])
        zoning = self.ds.get_zoning(address)

        if not zoning:
            result = ModuleResult(
                module=self.module_name,
                status=FinalStatus.REVIEW_REQUIRED,
                result={"zone_code": None, "zone_name": "未知"},
                review_required=True,
                notes=["無法查詢到分區資料，需人工覆核"],
                legal_basis=[
                    LegalBasis(
                        law_name="臺北市土地使用分區線上查詢系統",
                        article="N/A",
                        source_url="https://zone.udd.gov.taipei/",
                        source_type=SourceType.SYSTEM_QUERY,
                        review_required=True,
                    )
                ],
            )
            ctx.set_result(self.module_name, result)
            return result

        ctx.zoning_data = zoning
        intended_use = ctx.raw_input["intended_use"]
        allowed = zoning.get("allowed_uses", [])
        use_allowed = intended_use in allowed

        if use_allowed:
            status = FinalStatus.AUTO_PASS
            notes = [f"分區 {zoning['zone_name']}，允許 {USE_LABEL.get(intended_use, intended_use)} 使用"]
        else:
            status = FinalStatus.AUTO_FAIL
            allowed_labels = [USE_LABEL.get(u, u) for u in allowed]
            notes = [
                f"分區 {zoning['zone_name']}，不允許 {USE_LABEL.get(intended_use, intended_use)} 使用",
                f"允許用途：{', '.join(allowed_labels)}",
            ]

        result = ModuleResult(
            module=self.module_name,
            status=status,
            result={
                "zone_code": zoning["zone_code"],
                "zone_name": zoning["zone_name"],
                "intended_use": intended_use,
                "use_allowed": use_allowed,
                "allowed_uses": allowed,
            },
            legal_basis=[
                LegalBasis(
                    law_name="臺北市土地使用分區管制自治條例",
                    article="各分區使用管制規定",
                    source_url="https://laws.gov.taipei/Law/LawSearch/LawInformation/FL003962",
                    source_type=SourceType.LOCAL_LAW,
                ),
                LegalBasis(
                    law_name="臺北市土地使用分區線上查詢系統",
                    article="N/A",
                    source_url="https://zone.udd.gov.taipei/",
                    source_type=SourceType.SYSTEM_QUERY,
                    notes=["僅供參考，正式認定以都市計畫樁及實地鑑界為準"],
                ),
            ],
            notes=notes,
        )
        ctx.set_result(self.module_name, result)
        return result
