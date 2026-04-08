"""第13點：車道 / 交通動線初判。

自動化邏輯：
- 停車位少 + 臨路寬度足 → AUTO_PASS
- 停車位多 + 臨路寬 → AUTO_PASS
- 臨路窄 → HIGH_RISK
- 需交通影響評估 → HIGH_RISK
"""

from app.rule_engine.base import EvaluationContext, RuleModule
from app.schemas.enums import FinalStatus, SourceType
from app.schemas.evidence import LegalBasis
from app.schemas.output import ModuleResult


class TrafficModule(RuleModule):
    module_name = "traffic"

    def evaluate(self, ctx: EvaluationContext) -> ModuleResult:
        road_info = ctx.road_info or {}
        road_width = road_info.get("road_width_m", 0)
        area = ctx.raw_input.get("site_area_sqm") or 0

        parking_result = ctx.get_result("parking")
        car_spaces = parking_result.result.get("required_car_spaces", 0) if parking_result else 0

        notes = []
        issues = []

        # 車道寬度需求
        if car_spaces <= 50:
            min_driveway = 3.5
            driveway_type = "單車道"
        elif car_spaces <= 150:
            min_driveway = 5.5
            driveway_type = "雙車道"
        else:
            min_driveway = 5.5
            driveway_type = "雙車道 + 迴車空間"

        notes.append(f"法定停車位: {car_spaces} 輛 → 需 {driveway_type}（淨寬 >= {min_driveway}m）")

        # 臨路寬度
        if road_width > 0:
            notes.append(f"臨路寬度: {road_width} m")
            if road_width < 8:
                issues.append("臨路寬度 < 8m，車道出入口配置受限")
        else:
            issues.append("無法確認臨路寬度")

        # 坡道
        if car_spaces > 0:
            notes.append(f"需設地下室坡道（淨寬 >= {min_driveway}m，坡度 <= 1/6）")

        # 交通影響評估門檻
        needs_tia = area >= 10000 or car_spaces >= 300
        if needs_tia:
            issues.append(f"基地規模大（面積 {area} m² / 車位 {car_spaces}），需交通影響評估")
        else:
            notes.append("未達交通影響評估門檻")

        # 判定
        if issues:
            status = FinalStatus.HIGH_RISK
            notes = [f"-- {i}" for i in issues] + notes
        else:
            status = FinalStatus.AUTO_PASS
            notes.insert(0, "車道/交通動線初判可行")

        r = ModuleResult(
            module=self.module_name,
            status=status,
            result={
                "car_spaces": car_spaces,
                "min_driveway_width_m": min_driveway,
                "driveway_type": driveway_type,
                "road_width_m": road_width,
                "needs_traffic_impact_assessment": needs_tia,
            },
            review_required=status != FinalStatus.AUTO_PASS,
            notes=notes,
            legal_basis=[
                LegalBasis(
                    law_name="建築技術規則（建築設計施工編）",
                    article="第60條（車道寬度）、第62條（坡道）",
                    source_url="https://law.moj.gov.tw/LawClass/LawAll.aspx?pcode=D0070115",
                    source_type=SourceType.CENTRAL_LAW,
                ),
            ],
        )
        ctx.set_result(self.module_name, r)
        return r
