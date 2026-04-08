"""法規版本與參數註冊表。依實際法規條文設定，不寫死在規則引擎中。"""

from datetime import date
from typing import Any

LAW_VERSIONS: list[dict[str, Any]] = [
    {
        "law_name": "臺北市土地使用分區管制自治條例",
        "version_date": date(2025, 7, 9),
        "source_url": "https://laws.gov.taipei/Law/LawSearch/LawInformation/FL003962",
        "source_type": "local_law",
    },
    {
        "law_name": "臺北市都市設計及土地使用開發許可審議規則",
        "version_date": date(2023, 12, 29),
        "source_url": "https://laws.gov.taipei/Law/LawSearch/LawInformation/FL025899",
        "source_type": "local_law",
    },
    {
        "law_name": "臺北市畸零地使用自治條例",
        "version_date": date(2024, 4, 1),
        "source_url": "https://laws.gov.taipei/Law/LawSearch/LawInformation/FL004107",
        "source_type": "local_law",
    },
    {
        "law_name": "臺北市建築管理自治條例",
        "version_date": date(2024, 1, 1),
        "source_url": "https://laws.gov.taipei/Law/LawSearch/LawArticleContent/FL004106",
        "source_type": "local_law",
    },
    {
        "law_name": "建築技術規則（建築設計施工編）",
        "version_date": date(2024, 1, 1),
        "source_url": "https://law.moj.gov.tw/LawClass/LawAll.aspx?pcode=D0070115",
        "source_type": "central_law",
    },
]

# ============================================================
# 臺北市畸零地標準（依臺北市畸零地使用自治條例）
# 第3條：臨接建築線寬度不得小於 4.8 公尺
# 第4條：深度 11 公尺以上得免認定畸零地
# 注意：更細緻的寬度/深度分級需查都市計畫書圖附表
# ============================================================
ODD_LOT_STANDARDS: dict[str, dict[str, float]] = {
    "住宅區": {"min_width_m": 3.5, "min_depth_m": 11.0, "min_frontage_m": 4.8},
    "商業區": {"min_width_m": 3.5, "min_depth_m": 11.0, "min_frontage_m": 4.8},
    "工業區": {"min_width_m": 5.0, "min_depth_m": 14.0, "min_frontage_m": 4.8},
    "default": {"min_width_m": 3.5, "min_depth_m": 11.0, "min_frontage_m": 4.8},
}

# ============================================================
# 停車計算參數 — 臺北市土地使用分區管制自治條例第 86-1 條
# 依用途分類、樓地板面積分級計算
# ============================================================
# 結構：每個用途有 tiers 列表，依面積門檻遞增適用不同比率
# {"up_to": 面積上限, "per_sqm": 每多少m²設1輛}
# 超過所有 tier 的用最後一個
PARKING_PARAMS_86_1: dict[str, dict[str, Any]] = {
    "residential": {
        "label": "第二類（多戶住宅）",
        "car_tiers": [
            {"up_to": None, "per_sqm": 120},  # 每 120m² 設 1 輛
        ],
        "motor_tiers": [
            {"up_to": None, "per_sqm": 100},  # 每 100m² 設 1 輛
        ],
        "law_name": "臺北市土地使用分區管制自治條例",
        "article": "第86-1條第二類",
    },
    "office": {
        "label": "第五類（辦公）",
        "car_tiers": [
            {"up_to": 4000, "per_sqm": 100},
            {"up_to": 10000, "per_sqm": 120},
            {"up_to": None, "per_sqm": 150},
        ],
        "motor_tiers": [
            {"up_to": None, "per_sqm": 70},
        ],
        "law_name": "臺北市土地使用分區管制自治條例",
        "article": "第86-1條第五類",
    },
    "commercial": {
        "label": "第三類（零售/飲食/服務）",
        "car_tiers": [
            {"up_to": 2000, "per_sqm": 100},
            {"up_to": 4000, "per_sqm": 150},
            {"up_to": 10000, "per_sqm": 200},
            {"up_to": None, "per_sqm": 250},
        ],
        "motor_tiers": [
            {"up_to": None, "per_sqm": 200},
        ],
        "law_name": "臺北市土地使用分區管制自治條例",
        "article": "第86-1條第三類",
    },
    "hotel": {
        "label": "第三類（旅館）",
        "car_tiers": [
            {"up_to": 2000, "per_sqm": 100},
            {"up_to": 4000, "per_sqm": 150},
            {"up_to": 10000, "per_sqm": 200},
            {"up_to": None, "per_sqm": 250},
        ],
        "motor_tiers": [
            {"up_to": None, "per_sqm": 200},
        ],
        "law_name": "臺北市土地使用分區管制自治條例",
        "article": "第86-1條第三類",
    },
    "industrial_office": {
        "label": "第六類（廠辦/倉儲）",
        "car_tiers": [
            {"up_to": 4000, "per_sqm": 150},
            {"up_to": 10000, "per_sqm": 200},
            {"up_to": None, "per_sqm": 250},
        ],
        "motor_tiers": [
            {"up_to": None, "per_sqm": 200},
        ],
        "law_name": "臺北市土地使用分區管制自治條例",
        "article": "第86-1條第六類",
    },
}

# 建築技術規則第59條 fallback（都市計畫區內）
PARKING_PARAMS_BUILDING_CODE: dict[str, dict[str, Any]] = {
    "residential": {
        "exempt_sqm": 500,   # 500m² 以下免設
        "per_sqm": 150,      # 超過部分每 150m² 設 1 輛
        "law_name": "建築技術規則（建築設計施工編）",
        "article": "第59條第二類",
    },
    "commercial": {
        "exempt_sqm": 300,
        "per_sqm": 150,
        "law_name": "建築技術規則（建築設計施工編）",
        "article": "第59條第一類",
    },
    "hotel": {
        "exempt_sqm": 500,
        "per_sqm": 200,
        "law_name": "建築技術規則（建築設計施工編）",
        "article": "第59條第三類",
    },
    "office": {
        "exempt_sqm": 300,
        "per_sqm": 150,
        "law_name": "建築技術規則（建築設計施工編）",
        "article": "第59條第一類",
    },
    "industrial_office": {
        "exempt_sqm": 500,
        "per_sqm": 200,
        "law_name": "建築技術規則（建築設計施工編）",
        "article": "第59條",
    },
}

# ============================================================
# 都審適用門檻（臺北市都市設計及土地使用開發許可審議規則第3條）
# 注意：有多種案件類型，以下為一般開發案門檻
# ============================================================
URBAN_DESIGN_REVIEW_THRESHOLDS: dict[str, Any] = {
    "general": {
        "site_area_sqm": 6000,        # 基地面積 ≥ 6,000 m²
        "total_floor_area_sqm": 30000,  # 且總樓地板面積 ≥ 30,000 m²
        "condition": "and",  # 需同時滿足
    },
    "public_facility": {
        "site_area_sqm": 10000,       # 公共設施 ≥ 10,000 m²
    },
    "public_building": {
        "total_floor_area_sqm": 15000,  # 公有建築/社會住宅 ≥ 15,000 m²
    },
    "existing_renovation": {
        "total_floor_area_sqm": 5000,   # 既有建築改建 ≥ 5,000 m²
    },
    "far_transfer_ratio": 0.30,  # 容積移轉移入 ≥ 接受基地原基準容積之 30%
}

# 環評門檻（環境影響評估法施行細則）
EIA_THRESHOLDS: dict[str, float] = {
    "site_area_ha": 1.0,  # 住宅社區基地面積 ≥ 1 公頃
    "total_floor_area_sqm": 60000,  # 或總樓地板面積 ≥ 60,000 m²（商辦）
}

# ============================================================
# 防火間距（建築技術規則第110條）
# 注意：規範的是防火時效要求，非強制退縮距離
# ============================================================
FIRE_SEPARATION_RULES: dict[str, Any] = {
    "boundary_less_than_1_5m": {
        "description": "外牆距境界線 < 1.5m",
        "fire_rating_hr": 1.0,
        "opening_restricted": True,
    },
    "boundary_1_5m_to_3m": {
        "description": "外牆距境界線 1.5m ~ 3m",
        "fire_rating_hr": 0.5,
        "opening_restricted": True,  # 開口面積 ≤ 該面外牆 40%
    },
    "boundary_over_3m": {
        "description": "外牆距境界線 ≥ 3m",
        "fire_rating_hr": 0,
        "opening_restricted": False,
    },
    "same_site_two_buildings_less_3m": {
        "description": "同基地二幢建築間距 < 3m",
        "fire_rating_hr": 1.0,
    },
    "opening_limit_within_3m": 0.40,  # 距境界線 3m 內開口面積上限比率
}

# ============================================================
# 日照檢討（建築技術規則第39-1條）
# ============================================================
SUNLIGHT_RULES: dict[str, Any] = {
    "requirement": "冬至日1小時以上有效日照",
    "north_setback_m": 6.0,            # 北向退縮 ≥ 6m
    "north_projection_width_m": 20.0,  # 北向投影面寬合計 ≤ 20m
}
