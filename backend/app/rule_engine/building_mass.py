"""第10點：建築量體初判（高度、日照、斜線、退縮）。

自動化邏輯：
- 估算高度 ≤ 限制且不需日照檢討 → AUTO_PASS
- 估算高度 > 限制 → AUTO_FAIL
- 需日照檢討但面積充足 → HIGH_RISK
- 無高度限制 → AUTO_PASS
"""

from app.rule_engine.base import EvaluationContext, RuleModule
from app.schemas.enums import FinalStatus, SourceType
from app.schemas.evidence import LegalBasis
from app.schemas.output import ModuleResult

# 臺北市各分區高度限制（公尺）
HEIGHT_LIMITS: dict[str, float | None] = {
    "住一": 10.5,
    "住二": 21.0,
    "住三": 36.0,
    "住三之一": 36.0,
    "住三之二": 36.0,
    "住四": 50.0,
    "住四之一": 50.0,
    "商一": 50.0,
    "商二": None,
    "商三": None,
    "商四": None,
    "工二": 21.0,
    "工三": 36.0,
}

# 日照檢討門檻
SUNLIGHT_THRESHOLD_FLOORS = 7  # 7層以上

# 前院退縮（公尺）
SETBACK_FRONT: dict[str, float] = {
    "住一": 6.0, "住二": 4.0, "住三": 3.0, "住三之一": 3.0,
    "住三之二": 3.0, "住四": 3.0, "住四之一": 3.0,
    "商一": 0.0, "商二": 0.0, "商三": 0.0, "商四": 0.0,
    "工二": 3.0, "工三": 3.0,
}

FLOOR_HEIGHT_M = 3.3  # 每層樓高估算


class BuildingMassModule(RuleModule):
    module_name = "building_mass"

    def evaluate(self, ctx: EvaluationContext) -> ModuleResult:
        zoning = ctx.zoning_data or {}
        zone_code = zoning.get("zone_code", "")
        base_far = zoning.get("base_far", 0)
        base_bcr = zoning.get("base_bcr", 0)
        area = ctx.raw_input.get("site_area_sqm") or 0

        height_limit = HEIGHT_LIMITS.get(zone_code)
        setback = SETBACK_FRONT.get(zone_code, 3.0)

        max_floor_area = area * base_far / 100 if base_far else 0
        max_building_area = area * base_bcr / 100 if base_bcr else area
        est_floors = max_floor_area / max_building_area if max_building_area > 0 else 0
        est_height = est_floors * FLOOR_HEIGHT_M

        notes = []
        is_residential = "住" in zone_code
        needs_sunlight = is_residential and est_floors >= SUNLIGHT_THRESHOLD_FLOORS
        height_exceeded = height_limit is not None and est_height > height_limit

        # 高度
        if height_limit is not None:
            notes.append(f"分區高度限制: {height_limit} m")
            if height_exceeded:
                notes.append(f"估算建築高度 {est_height:.1f} m > 限制 {height_limit} m")
                notes.append("需調整樓層數或建築面積配置以符合高度限制")
            else:
                notes.append(f"估算建築高度 {est_height:.1f} m，符合高度限制")
        else:
            notes.append("本分區無高度限制")
            notes.append(f"估算建築高度 {est_height:.1f} m")

        notes.append(f"估算樓層數: 約 {est_floors:.1f} 層")
        notes.append(f"前院退縮: {setback} m")

        # 日照（建築技術規則第39-1條）
        if needs_sunlight:
            notes.append(f"估算 {est_floors:.0f} 層 >= {SUNLIGHT_THRESHOLD_FLOORS} 層，需日照檢討")
            notes.append("日照要求：冬至日需有 1 小時以上有效日照（第39-1條）")
            notes.append("北向退縮距離需 >= 6m，北向投影面寬合計 <= 20m")
            if area >= 300:
                notes.append("基地面積尚足，日照檢討可透過建築配置解決")
            else:
                notes.append("基地面積較小，日照檢討可能影響量體配置")
        elif is_residential:
            notes.append("層數未達日照檢討門檻，免檢討")

        # 後院深度比
        import math
        side = math.sqrt(area)
        rear_depth = side * 0.25  # 概估後院 = 邊長 25%
        notes.append(f"後院深度概估: {rear_depth:.1f} m（依建築技術規則需 ≥ 建築高度之比例）")

        # 決定狀態
        if height_exceeded:
            status = FinalStatus.AUTO_FAIL
        elif needs_sunlight and area < 200:
            status = FinalStatus.HIGH_RISK
        elif needs_sunlight:
            status = FinalStatus.AUTO_PASS
            notes.append("量體初判可行，惟日照需於設計階段檢討")
        else:
            status = FinalStatus.AUTO_PASS
            notes.append("量體初判可行")

        r = ModuleResult(
            module=self.module_name,
            status=status,
            result={
                "height_limit_m": height_limit,
                "estimated_height_m": round(est_height, 1),
                "estimated_floors": round(est_floors, 1),
                "setback_front_m": setback,
                "height_exceeded": height_exceeded,
                "needs_sunlight_review": needs_sunlight,
                "max_floor_area_sqm": round(max_floor_area, 1),
                "max_building_area_sqm": round(max_building_area, 1),
            },
            review_required=status != FinalStatus.AUTO_PASS,
            notes=notes,
            legal_basis=[
                LegalBasis(
                    law_name="臺北市土地使用分區管制自治條例",
                    article="各分區高度限制",
                    source_url="https://laws.gov.taipei/Law/LawSearch/LawInformation/FL003962",
                    source_type=SourceType.LOCAL_LAW,
                ),
                LegalBasis(
                    law_name="建築技術規則（建築設計施工編）",
                    article="第23條（日照）、第24條（斜線）",
                    source_url="https://law.moj.gov.tw/LawClass/LawAll.aspx?pcode=D0070115",
                    source_type=SourceType.CENTRAL_LAW,
                ),
            ],
        )
        ctx.set_result(self.module_name, r)
        return r
