"""第12點：停車數量初算 — 三層 fallback（都市計畫→土管86-1→建技規則）。

依臺北市土地使用分區管制自治條例第86-1條，停車位依用途分類、
樓地板面積分級計算。非簡化的單一比例。
"""

import math

from app.rule_engine.base import EvaluationContext, RuleModule
from app.schemas.enums import FinalStatus, SourceType
from app.schemas.evidence import LegalBasis
from app.schemas.output import ModuleResult
from app.versioning.law_registry import PARKING_PARAMS_86_1, PARKING_PARAMS_BUILDING_CODE


def _calc_tiered(total_area: float, tiers: list[dict]) -> int:
    """依分級 tiers 計算停車位數。"""
    remaining = total_area
    count = 0
    prev_limit = 0

    for tier in tiers:
        up_to = tier["up_to"]
        per_sqm = tier["per_sqm"]

        if up_to is None:
            # 最後一級，算完剩餘面積
            count += remaining / per_sqm
            remaining = 0
        else:
            tier_range = up_to - prev_limit
            applicable = min(remaining, tier_range)
            count += applicable / per_sqm
            remaining -= applicable
            prev_limit = up_to

        if remaining <= 0:
            break

    return math.ceil(count)


class ParkingModule(RuleModule):
    module_name = "parking"

    def evaluate(self, ctx: EvaluationContext) -> ModuleResult:
        zoning = ctx.zoning_data or {}
        intended_use = ctx.raw_input["intended_use"]
        area = ctx.raw_input.get("site_area_sqm") or 0

        # 取 far_bcr 結果算總樓地板面積
        far_result = ctx.get_result("far_bcr")
        if far_result and far_result.result.get("max_total_floor_area_sqm"):
            total_floor_area = far_result.result["max_total_floor_area_sqm"]
        else:
            base_far = zoning.get("base_far", 200)
            total_floor_area = area * base_far / 100

        # === 三層 fallback ===

        # Layer 1: 都市計畫停車規定
        urban_plan_parking = zoning.get("urban_plan_parking")
        if urban_plan_parking:
            return self._from_urban_plan(ctx, urban_plan_parking, total_floor_area)

        # Layer 2: 土管第86-1條（分級制）
        params = PARKING_PARAMS_86_1.get(intended_use)
        if params:
            return self._from_86_1(ctx, params, total_floor_area)

        # Layer 3: 建築技術規則第59條 fallback
        return self._from_building_code(ctx, intended_use, total_floor_area)

    def _from_urban_plan(self, ctx: EvaluationContext, plan: dict,
                          total_floor_area: float) -> ModuleResult:
        car = plan.get("car_spaces", 0)
        motor = plan.get("motor_spaces", 0)
        return self._build_result(ctx, car, motor, total_floor_area,
            "都市計畫停車規定", "依都市計畫書圖規定",
            "https://zone.udd.gov.taipei/", SourceType.GIS_DATA,
            ["依都市計畫書圖另定停車規定優先適用"])

    def _from_86_1(self, ctx: EvaluationContext, params: dict,
                    total_floor_area: float) -> ModuleResult:
        car = _calc_tiered(total_floor_area, params["car_tiers"])
        motor = _calc_tiered(total_floor_area, params["motor_tiers"])

        tier_desc = []
        for t in params["car_tiers"]:
            if t["up_to"]:
                tier_desc.append(f"≤{t['up_to']}m²: 每{t['per_sqm']}m²設1輛")
            else:
                tier_desc.append(f"其餘: 每{t['per_sqm']}m²設1輛")

        notes = [
            f"適用 {params['label']}",
            f"總樓地板面積: {total_floor_area:,.1f} m²",
            f"汽車位分級: {'; '.join(tier_desc)}",
            f"法定汽車位: {car} 輛",
            f"法定機車位: {motor} 輛",
        ]

        return self._build_result(ctx, car, motor, total_floor_area,
            params["law_name"], params["article"],
            "https://laws.gov.taipei/Law/LawSearch/LawInformation/FL003962",
            SourceType.LOCAL_LAW, notes)

    def _from_building_code(self, ctx: EvaluationContext, intended_use: str,
                             total_floor_area: float) -> ModuleResult:
        params = PARKING_PARAMS_BUILDING_CODE.get(intended_use, {
            "exempt_sqm": 500, "per_sqm": 150,
            "law_name": "建築技術規則（建築設計施工編）", "article": "第59條",
        })
        exempt = params["exempt_sqm"]
        per_sqm = params["per_sqm"]
        taxable = max(0, total_floor_area - exempt)
        car = math.ceil(taxable / per_sqm)
        motor = 0  # 建技規則未強制規定機車位

        notes = [
            "都市計畫及土管未規定，回歸建築技術規則第59條",
            f"總樓地板面積: {total_floor_area:,.1f} m²",
            f"免設門檻: {exempt} m²",
            f"超過部分每 {per_sqm} m² 設 1 輛",
            f"法定汽車位: {car} 輛",
        ]

        return self._build_result(ctx, car, motor, total_floor_area,
            params["law_name"], params["article"],
            "https://law.moj.gov.tw/LawClass/LawAll.aspx?pcode=D0070115",
            SourceType.CENTRAL_LAW, notes)

    def _build_result(self, ctx: EvaluationContext, car: int, motor: int,
                       total_floor_area: float, law_name: str, article: str,
                       url: str, source_type: SourceType,
                       notes: list[str]) -> ModuleResult:
        r = ModuleResult(
            module=self.module_name,
            status=FinalStatus.AUTO_PASS,
            result={
                "required_car_spaces": car,
                "required_motor_spaces": motor,
                "total_floor_area_sqm": round(total_floor_area, 2),
                "calculation_basis": law_name,
            },
            legal_basis=[
                LegalBasis(
                    law_name=law_name,
                    article=article,
                    source_url=url,
                    source_type=source_type,
                )
            ],
            notes=notes,
        )
        ctx.set_result(self.module_name, r)
        return r
