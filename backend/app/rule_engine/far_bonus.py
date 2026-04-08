"""第8點：容積獎勵初判。

自動化邏輯：
- 依分區、用途、制度自動列出適用獎勵項目
- 計算各項上限與合計上限
- 一般開發：可明確列出適用項目與上限 → AUTO_PASS
- 都更/危老：有額外獎勵但需審議 → HIGH_RISK
- 工業區等限制較多 → 標示限制
"""

from app.rule_engine.base import EvaluationContext, RuleModule
from app.schemas.enums import FinalStatus, SourceType
from app.schemas.evidence import LegalBasis
from app.schemas.output import ModuleResult


# 臺北市容積獎勵項目資料庫
BONUS_ITEMS = {
    "open_space": {
        "name": "開放空間獎勵",
        "max_pct": 20,
        "condition": "留設開放空間供公眾通行或休憩",
        "applicable_zones": ["住", "商"],
        "schemes": ["general", "urban_renewal", "dangerous_old"],
        "law": "臺北市土地使用分區管制自治條例",
        "article": "開放空間獎勵相關條文",
    },
    "parking_public": {
        "name": "停車獎勵",
        "max_pct": 20,
        "condition": "設置超額公共停車位供公眾使用",
        "applicable_zones": ["住", "商"],
        "schemes": ["general", "urban_renewal", "dangerous_old"],
        "law": "臺北市土地使用分區管制自治條例",
        "article": "停車獎勵相關條文",
    },
    "green_building": {
        "name": "綠建築獎勵",
        "max_pct": 10,
        "condition": "取得綠建築銀級以上標章",
        "applicable_zones": ["住", "商", "工"],
        "schemes": ["general", "urban_renewal", "dangerous_old"],
        "law": "臺北市土地使用分區管制自治條例",
        "article": "綠建築獎勵相關條文",
    },
    "smart_building": {
        "name": "智慧建築獎勵",
        "max_pct": 6,
        "condition": "取得智慧建築標章",
        "applicable_zones": ["住", "商", "工"],
        "schemes": ["general", "urban_renewal", "dangerous_old"],
        "law": "臺北市土地使用分區管制自治條例",
        "article": "智慧建築獎勵相關條文",
    },
    "urban_renewal": {
        "name": "都市更新容積獎勵",
        "max_pct": 50,
        "condition": "依都市更新條例申請，含規模、時程、處理方式等獎勵",
        "applicable_zones": ["住", "商"],
        "schemes": ["urban_renewal"],
        "law": "都市更新條例",
        "article": "第65條",
    },
    "dangerous_old": {
        "name": "危老重建容積獎勵",
        "max_pct": 40,
        "condition": "依危老條例申請重建",
        "applicable_zones": ["住", "商"],
        "schemes": ["dangerous_old"],
        "law": "都市危險及老舊建築物加速重建條例",
        "article": "第6條",
    },
    "time_bonus": {
        "name": "時程獎勵",
        "max_pct": 10,
        "condition": "於規定期限內申請重建（逐年遞減）",
        "applicable_zones": ["住", "商"],
        "schemes": ["dangerous_old"],
        "law": "都市危險及老舊建築物加速重建條例",
        "article": "第6條",
    },
}

# 容積獎勵上限（法定容積倍率）
MAX_BONUS_CAP = {
    "general": 0.20,         # 一般開發最多 20% 法定容積
    "urban_renewal": 0.50,   # 都更最多 50%
    "dangerous_old": 0.40,   # 危老最多 40%（含時程）
}


class FarBonusModule(RuleModule):
    module_name = "far_bonus"

    def evaluate(self, ctx: EvaluationContext) -> ModuleResult:
        zoning = ctx.zoning_data or {}
        zone_code = zoning.get("zone_code", "")
        base_far = zoning.get("base_far", 0)
        area = ctx.raw_input.get("site_area_sqm", 0)
        scheme = ctx.raw_input.get("development_scheme") or "general"

        # 找出適用獎勵
        applicable = []
        for key, item in BONUS_ITEMS.items():
            # 檢查分區是否適用
            zone_match = any(z in zone_code for z in item["applicable_zones"])
            scheme_match = scheme in item["schemes"]
            if zone_match and scheme_match:
                applicable.append(item)

        # 計算上限
        cap_rate = MAX_BONUS_CAP.get(scheme, 0.20)
        total_bonus_pct = min(sum(i["max_pct"] for i in applicable), base_far * cap_rate)
        bonus_floor_area = area * total_bonus_pct / 100

        notes = [
            f"基準容積率: {base_far}%",
            f"開發制度: {scheme}",
            f"適用獎勵項目: {len(applicable)} 項",
        ]
        for item in applicable:
            notes.append(f"  - {item['name']}（上限 {item['max_pct']}%）：{item['condition']}")

        notes.append(f"獎勵上限合計: {total_bonus_pct:.1f}%（法定容積之 {cap_rate*100:.0f}% 為上限）")
        notes.append(f"獎勵容積估算: 約 {bonus_floor_area:,.1f} m²")

        # 一般開發的獎勵項目明確，可自動判定
        if scheme == "general":
            status = FinalStatus.AUTO_PASS
            notes.append("一般開發容積獎勵項目與上限明確")
        else:
            status = FinalStatus.HIGH_RISK
            notes.append(f"{scheme} 獎勵需經審議核定，實際核給量由主管機關認定")

        legal_basis = [
            LegalBasis(
                law_name="臺北市土地使用分區管制自治條例",
                article="容積獎勵相關條文",
                source_url="https://laws.gov.taipei/Law/LawSearch/LawInformation/FL003962",
                source_type=SourceType.LOCAL_LAW,
            ),
        ]
        if scheme == "urban_renewal":
            legal_basis.append(LegalBasis(
                law_name="都市更新條例",
                article="第65條",
                source_url="https://law.moj.gov.tw/",
                source_type=SourceType.CENTRAL_LAW,
            ))
        elif scheme == "dangerous_old":
            legal_basis.append(LegalBasis(
                law_name="都市危險及老舊建築物加速重建條例",
                article="第6條",
                source_url="https://law.moj.gov.tw/",
                source_type=SourceType.CENTRAL_LAW,
            ))

        r = ModuleResult(
            module=self.module_name,
            status=status,
            result={
                "applicable_count": len(applicable),
                "applicable_items": [i["name"] for i in applicable],
                "total_bonus_pct": round(total_bonus_pct, 1),
                "bonus_floor_area_sqm": round(bonus_floor_area, 1),
                "cap_rate": cap_rate,
                "base_far_pct": base_far,
                "scheme": scheme,
            },
            review_required=status != FinalStatus.AUTO_PASS,
            notes=notes,
            legal_basis=legal_basis,
        )
        ctx.set_result(self.module_name, r)
        return r
