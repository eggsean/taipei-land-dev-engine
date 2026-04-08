"""第11點：防火間距 / 開口限制初判。

依建築技術規則第110條：
- 距境界線 < 1.5m → 外牆需 1hr 防火時效，開口受限
- 距境界線 1.5m~3m → 外牆需 0.5hr 防火時效，開口面積 ≤ 40%
- 距境界線 ≥ 3m → 無限制
防火間距不是強制退縮距離，而是影響外牆防火等級與開口限制。
"""

import math

from app.rule_engine.base import EvaluationContext, RuleModule
from app.schemas.enums import FinalStatus, SourceType
from app.schemas.evidence import LegalBasis
from app.schemas.output import ModuleResult
from app.versioning.law_registry import FIRE_SEPARATION_RULES


class FireSafetyModule(RuleModule):
    module_name = "fire_safety"

    def evaluate(self, ctx: EvaluationContext) -> ModuleResult:
        area = ctx.raw_input.get("site_area_sqm", 0)
        zoning = ctx.zoning_data or {}
        zone_code = zoning.get("zone_code", "")
        intended_use = ctx.raw_input.get("intended_use", "")

        side = math.sqrt(area)
        opening_limit = FIRE_SEPARATION_RULES["opening_limit_within_3m"]

        # 估算可能的境界線退縮
        # 商業區可貼境界線建築（退縮 0m），住宅區通常退縮 1.5m+
        if "商" in zone_code:
            likely_setback = 0
        elif "工" in zone_code:
            likely_setback = 1.5
        else:
            likely_setback = 1.5

        notes = []

        # 依退縮距離判定防火等級需求
        if likely_setback < 1.5:
            fire_rating = "1小時以上"
            notes.append(f"商業區可貼境界線建築，外牆需 {fire_rating} 防火時效（第110條）")
            notes.append(f"距境界線 3m 內開口面積 ≤ 外牆面積之 {opening_limit*100:.0f}%")
        elif likely_setback < 3.0:
            fire_rating = "半小時以上"
            notes.append(f"退縮 1.5m~3m，外牆需 {fire_rating} 防火時效")
            notes.append(f"距境界線 3m 內開口面積 ≤ 外牆面積之 {opening_limit*100:.0f}%")
        else:
            fire_rating = "無特殊要求"
            notes.append(f"退縮 ≥ 3m，外牆無特殊防火時效要求")

        # 防火區劃
        far_result = ctx.get_result("far_bcr")
        total_floor_area = 0
        if far_result:
            total_floor_area = far_result.result.get("max_total_floor_area_sqm", 0)

        if total_floor_area > 1500:
            notes.append(f"總樓地板 {total_floor_area:,.0f}m² > 1,500m²，需設防火區劃")
        else:
            notes.append("總樓地板面積未超過防火區劃門檻")

        # 特殊用途消防要求
        if intended_use == "hotel":
            notes.append("旅館用途：需符合消防法特殊要求（自動撒水、排煙、緊急照明等）")
        elif intended_use == "commercial":
            notes.append("商業用途：營業面積 > 300m² 需設自動撒水設備")

        # 建築面積與基地的關係
        bcr = zoning.get("base_bcr", 50)
        building_area = area * bcr / 100
        non_building_area = area - building_area
        avg_setback = non_building_area / (4 * math.sqrt(building_area)) if building_area > 0 else 0

        notes.append(f"建蔽率 {bcr}%，估算平均境界線退縮: {avg_setback:.1f}m")

        # 判定
        if area < 30:
            status = FinalStatus.AUTO_FAIL
            notes.insert(0, "基地面積過小，防火配置困難")
        elif avg_setback < 1.0 and "住" in zone_code:
            status = FinalStatus.HIGH_RISK
            notes.insert(0, "住宅區平均退縮不足 1m，防火配置受限")
        else:
            status = FinalStatus.AUTO_PASS
            notes.insert(0, "防火間距與開口限制初判可行")

        r = ModuleResult(
            module=self.module_name,
            status=status,
            result={
                "fire_rating_required": fire_rating,
                "avg_setback_m": round(avg_setback, 1),
                "opening_limit_ratio": opening_limit,
                "needs_fire_compartment": total_floor_area > 1500,
            },
            review_required=status != FinalStatus.AUTO_PASS,
            notes=notes,
            legal_basis=[
                LegalBasis(
                    law_name="建築技術規則（建築設計施工編）",
                    article="第110條（防火間距與開口）、第79條（防火區劃）",
                    source_url="https://law.moj.gov.tw/LawClass/LawAll.aspx?pcode=D0070115",
                    source_type=SourceType.CENTRAL_LAW,
                ),
            ],
        )
        ctx.set_result(self.module_name, r)
        return r
