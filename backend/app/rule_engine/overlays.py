"""第14-17點：特殊疊圖風險（都審、山坡地、文資、環評）。

自動化邏輯：
- 都審：面積 < 門檻且不在都審地區 → AUTO_PASS；在都審地區 → HIGH_RISK
- 山坡地：不在管制區 → AUTO_PASS；在管制區 → HIGH_RISK
- 文資：不在範圍 → AUTO_PASS；在範圍 → HIGH_RISK
- 環評：面積 < 門檻 → AUTO_PASS；達門檻 → HIGH_RISK
"""

from app.data_sources.base import DataSource
from app.rule_engine.base import EvaluationContext, RuleModule
from app.schemas.enums import FinalStatus, SourceType
from app.schemas.evidence import LegalBasis
from app.schemas.output import ModuleResult, OverlayRisk
from app.versioning.law_registry import EIA_THRESHOLDS, URBAN_DESIGN_REVIEW_THRESHOLDS


OVERLAY_CONFIG = {
    "urban_design_review": {
        "label": "都市設計審議",
        "law_name": "臺北市都市設計及土地使用開發許可審議規則",
        "article": "第3條（適用範圍）",
        "url": "https://laws.gov.taipei/Law/LawSearch/LawInformation/FL025899",
        "source_type": SourceType.LOCAL_LAW,
    },
    "hillside": {
        "label": "山坡地管制區",
        "law_name": "山坡地保育利用條例",
        "article": "第5條、第10條",
        "url": "https://law.moj.gov.tw/",
        "source_type": SourceType.CENTRAL_LAW,
    },
    "cultural_heritage": {
        "label": "文化資產範圍",
        "law_name": "文化資產保存法",
        "article": "第33條、第34條",
        "url": "https://nchdb.boch.gov.tw/",
        "source_type": SourceType.CENTRAL_LAW,
    },
    "eia": {
        "label": "環境影響評估",
        "law_name": "環境影響評估法",
        "article": "第5條（應實施環評之開發行為）",
        "url": "https://law.moj.gov.tw/",
        "source_type": SourceType.CENTRAL_LAW,
    },
}


class OverlaysModule(RuleModule):
    module_name = "overlays"

    def __init__(self, data_source: DataSource) -> None:
        self.ds = data_source

    def evaluate(self, ctx: EvaluationContext) -> ModuleResult:
        address = ctx.site_identity.get("normalized", ctx.raw_input["address_or_lot"])
        overlay_data = self.ds.get_overlays(address)
        ctx.overlays = overlay_data
        area = ctx.raw_input["site_area_sqm"]

        risks: list[OverlayRisk] = []
        notes: list[str] = []
        all_basis: list[LegalBasis] = []

        in_overlay = {ov["type"] for ov in overlay_data}

        # --- 都審（第17點）---
        # 依臺北市都市設計及土地使用開發許可審議規則第3條
        # 一般開發案：基地面積 ≥ 6,000m² 且 總樓地板面積 ≥ 30,000m²
        udr_general = URBAN_DESIGN_REVIEW_THRESHOLDS["general"]
        udr_area_threshold = udr_general["site_area_sqm"]      # 6000
        udr_floor_threshold = udr_general["total_floor_area_sqm"]  # 30000

        # 估算總樓地板面積
        far_result = ctx.get_result("far_bcr")
        est_floor_area = 0.0
        if far_result and far_result.result.get("max_total_floor_area_sqm"):
            est_floor_area = far_result.result["max_total_floor_area_sqm"]

        udr_config = OVERLAY_CONFIG["urban_design_review"]
        udr_basis = LegalBasis(
            law_name=udr_config["law_name"], article=udr_config["article"],
            source_url=udr_config["url"], source_type=udr_config["source_type"],
        )

        if "urban_design_review" in in_overlay:
            # 圖資標記在都審地區
            risks.append(OverlayRisk(
                risk_type="urban_design_review",
                description="位於都審地區（圖資標記），需經都市設計審議",
                status=FinalStatus.HIGH_RISK,
                legal_basis=[udr_basis],
            ))
            notes.append("位於都審地區（圖資標記），需經都市設計審議")
            all_basis.append(udr_basis)
        elif area >= udr_area_threshold and est_floor_area >= udr_floor_threshold:
            # 面積 + 樓地板面積同時達門檻
            risks.append(OverlayRisk(
                risk_type="urban_design_review",
                description=f"面積 {area:,.0f}m² ≥ {udr_area_threshold:,.0f}m² 且"
                            f"樓地板 {est_floor_area:,.0f}m² ≥ {udr_floor_threshold:,.0f}m²，須都審",
                status=FinalStatus.HIGH_RISK,
                legal_basis=[udr_basis],
            ))
            notes.append(f"面積與樓地板面積均達都審門檻（第3條一般開發案）")
            all_basis.append(udr_basis)
        else:
            notes.append(
                f"未在都審地區，面積 {area:,.0f}m²（門檻 {udr_area_threshold:,.0f}m²）、"
                f"樓地板 {est_floor_area:,.0f}m²（門檻 {udr_floor_threshold:,.0f}m²），免都審"
            )

        # --- 山坡地（第14點）---
        hs_config = OVERLAY_CONFIG["hillside"]
        hs_basis = LegalBasis(
            law_name=hs_config["law_name"], article=hs_config["article"],
            source_url=hs_config["url"], source_type=hs_config["source_type"],
        )
        if "hillside" in in_overlay:
            risks.append(OverlayRisk(
                risk_type="hillside",
                description="位於山坡地管制區，開發受限",
                status=FinalStatus.HIGH_RISK,
                legal_basis=[hs_basis],
            ))
            notes.append("位於山坡地管制區，需水土保持計畫")
            all_basis.append(hs_basis)
        else:
            notes.append("未位於山坡地管制區")

        # --- 文資（第15點）---
        ch_config = OVERLAY_CONFIG["cultural_heritage"]
        ch_basis = LegalBasis(
            law_name=ch_config["law_name"], article=ch_config["article"],
            source_url=ch_config["url"], source_type=ch_config["source_type"],
        )
        if "cultural_heritage" in in_overlay:
            risks.append(OverlayRisk(
                risk_type="cultural_heritage",
                description="位於文化資產範圍或鄰近文資",
                status=FinalStatus.HIGH_RISK,
                legal_basis=[ch_basis],
            ))
            notes.append("位於文化資產潛在範圍，需文資審查")
            all_basis.append(ch_basis)
        else:
            notes.append("未位於文化資產範圍")

        # --- 環評（第16點）---
        eia_config = OVERLAY_CONFIG["eia"]
        eia_basis = LegalBasis(
            law_name=eia_config["law_name"], article=eia_config["article"],
            source_url=eia_config["url"], source_type=eia_config["source_type"],
        )
        eia_area_ha = EIA_THRESHOLDS["site_area_ha"]
        if area >= eia_area_ha * 10000:
            risks.append(OverlayRisk(
                risk_type="eia",
                description=f"面積 {area} m² >= {eia_area_ha} 公頃，可能需環評",
                status=FinalStatus.HIGH_RISK,
                legal_basis=[eia_basis],
            ))
            notes.append(f"面積達環評門檻 ({eia_area_ha} 公頃)")
            all_basis.append(eia_basis)
        else:
            notes.append(f"面積 < {eia_area_ha} 公頃，免環評")

        # 整體狀態
        if risks:
            overall = FinalStatus.HIGH_RISK
        else:
            overall = FinalStatus.AUTO_PASS
            notes.insert(0, "未偵測到特殊疊圖風險")

        r = ModuleResult(
            module=self.module_name,
            status=overall,
            result={"risks": [risk.model_dump() for risk in risks]},
            review_required=bool(risks),
            notes=notes,
            legal_basis=all_basis,
        )
        ctx.set_result(self.module_name, r)
        return r
