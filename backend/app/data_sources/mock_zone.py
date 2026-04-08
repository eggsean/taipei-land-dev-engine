"""臺北市使用分區 mock 資料，含容積率、建蔽率、允許用途。"""

from typing import Any

from app.data_sources.base import DataSource

# 臺北市使用分區法定參數（依臺北市土地使用分區管制自治條例）
ZONING_TABLE: dict[str, dict[str, Any]] = {
    "住一": {
        "zone_name": "第一種住宅區",
        "base_far": 60,
        "base_bcr": 30,
        "allowed_uses": ["residential"],
        "urban_plan_parking": None,
    },
    "住二": {
        "zone_name": "第二種住宅區",
        "base_far": 120,
        "base_bcr": 35,
        "allowed_uses": ["residential"],
        "urban_plan_parking": None,
    },
    "住二之一": {
        "zone_name": "第二種住宅區之一",
        "base_far": 160,
        "base_bcr": 35,
        "allowed_uses": ["residential"],
        "urban_plan_parking": None,
    },
    "住二之二": {
        "zone_name": "第二種住宅區之二",
        "base_far": 225,
        "base_bcr": 35,
        "allowed_uses": ["residential", "office"],
        "urban_plan_parking": None,
    },
    "住三": {
        "zone_name": "第三種住宅區",
        "base_far": 225,
        "base_bcr": 45,
        "allowed_uses": ["residential", "office"],
        "urban_plan_parking": None,
    },
    "住三之一": {
        "zone_name": "第三種住宅區之一",
        "base_far": 300,  # 修正：原誤為200
        "base_bcr": 45,
        "allowed_uses": ["residential", "office"],
        "urban_plan_parking": None,
    },
    "住三之二": {
        "zone_name": "第三種住宅區之二",
        "base_far": 400,  # 修正：原誤為300
        "base_bcr": 45,
        "allowed_uses": ["residential", "office", "commercial"],
        "urban_plan_parking": None,
    },
    "住四": {
        "zone_name": "第四種住宅區",
        "base_far": 300,
        "base_bcr": 50,
        "allowed_uses": ["residential", "office", "commercial", "hotel"],
        "urban_plan_parking": None,
    },
    "住四之一": {
        "zone_name": "第四種住宅區之一",
        "base_far": 400,
        "base_bcr": 50,
        "allowed_uses": ["residential", "office", "commercial", "hotel"],
        "urban_plan_parking": None,
    },
    "商一": {
        "zone_name": "第一種商業區",
        "base_far": 360,
        "base_bcr": 55,
        "allowed_uses": ["residential", "office", "commercial", "hotel"],
        "urban_plan_parking": None,
    },
    "商二": {
        "zone_name": "第二種商業區",
        "base_far": 630,
        "base_bcr": 65,
        "allowed_uses": ["residential", "office", "commercial", "hotel"],
        "urban_plan_parking": None,
    },
    "商三": {
        "zone_name": "第三種商業區",
        "base_far": 560,
        "base_bcr": 65,
        "allowed_uses": ["residential", "office", "commercial", "hotel"],
        "urban_plan_parking": None,
    },
    "商四": {
        "zone_name": "第四種商業區",
        "base_far": 800,
        "base_bcr": 75,
        "allowed_uses": ["residential", "office", "commercial", "hotel"],
        "urban_plan_parking": None,
    },
    "工二": {
        "zone_name": "第二種工業區",
        "base_far": 200,  # 修正：原誤為300
        "base_bcr": 45,   # 修正：原誤為55
        "allowed_uses": ["industrial_office"],
        "urban_plan_parking": None,
    },
    "工三": {
        "zone_name": "第三種工業區",
        "base_far": 300,  # 修正：原誤為400
        "base_bcr": 55,   # 修正：原誤為65
        "allowed_uses": ["industrial_office", "office"],
        "urban_plan_parking": None,
    },
}

# 地址/地號 → 分區 mock 映射
ADDRESS_ZONING_MAP: dict[str, str] = {
    "臺北市大安區仁愛路三段1號": "住三",
    "臺北市信義區松仁路100號": "商二",
    "臺北市中山區南京東路二段50號": "商三",
    "臺北市內湖區瑞光路513號": "工三",
    "臺北市北投區中央北路四段100號": "住二",
    "臺北市士林區中山北路七段200號": "住一",
    "臺北市松山區敦化北路100號": "商四",
    "臺北市大同區重慶北路三段1號": "住四",
    "大安區復興段一小段100地號": "住三之二",
    "信義區信義段二小段200地號": "商一",
}


# 地址/地號 → 基地資訊 mock（模擬地政系統查詢）
ADDRESS_SITE_INFO: dict[str, dict[str, Any]] = {
    "臺北市大安區仁愛路三段1號": {"site_area_sqm": 520.0, "land_section": "大安區仁愛段一小段", "lot_number": "0100"},
    "臺北市信義區松仁路100號": {"site_area_sqm": 1200.0, "land_section": "信義區信義段二小段", "lot_number": "0200"},
    "臺北市中山區南京東路二段50號": {"site_area_sqm": 680.0, "land_section": "中山區南京段一小段", "lot_number": "0050"},
    "臺北市內湖區瑞光路513號": {"site_area_sqm": 2500.0, "land_section": "內湖區瑞光段二小段", "lot_number": "0513"},
    "臺北市北投區中央北路四段100號": {"site_area_sqm": 350.0, "land_section": "北投區中央段三小段", "lot_number": "0100"},
    "臺北市士林區中山北路七段200號": {"site_area_sqm": 180.0, "land_section": "士林區中山段一小段", "lot_number": "0200"},
    "臺北市松山區敦化北路100號": {"site_area_sqm": 3200.0, "land_section": "松山區敦化段一小段", "lot_number": "0100"},
    "臺北市大同區重慶北路三段1號": {"site_area_sqm": 450.0, "land_section": "大同區重慶段二小段", "lot_number": "0001"},
    "大安區復興段一小段100地號": {"site_area_sqm": 800.0, "land_section": "大安區復興段一小段", "lot_number": "0100"},
    "信義區信義段二小段200地號": {"site_area_sqm": 1500.0, "land_section": "信義區信義段二小段", "lot_number": "0200"},
}


def _normalize(s: str) -> str:
    """統一台/臺、全半形等差異。"""
    return s.replace("台北", "臺北").replace("　", "").replace(" ", "").strip()


def _fuzzy_lookup(mapping: dict, key: str) -> Any:
    """正規化後做完整匹配，再做部分匹配。"""
    nk = _normalize(key)
    for k, v in mapping.items():
        if _normalize(k) == nk:
            return v
    for k, v in mapping.items():
        nk2 = _normalize(k)
        if nk in nk2 or nk2 in nk:
            return v
    return None


class MockZoneDataSource(DataSource):
    def get_site_info(self, address_or_lot: str) -> dict[str, Any] | None:
        return _fuzzy_lookup(ADDRESS_SITE_INFO, address_or_lot)

    def get_zoning(self, address_or_lot: str) -> dict[str, Any] | None:
        zone_code = _fuzzy_lookup(ADDRESS_ZONING_MAP, address_or_lot)
        if not zone_code:
            zone_code = "住三"

        zone_data = ZONING_TABLE.get(zone_code)
        if zone_data:
            return {"zone_code": zone_code, **zone_data}
        return None

    def get_overlays(self, address_or_lot: str) -> list[dict[str, Any]]:
        overlays = []
        addr = _normalize(address_or_lot)
        if "北投" in addr:
            overlays.append({
                "type": "hillside",
                "description": "山坡地管制區",
                "in_scope": True,
            })
        if "大安" in addr or "信義" in addr:
            overlays.append({
                "type": "urban_design_review",
                "description": "都市設計審議地區",
                "in_scope": True,
            })
        if "大同" in addr:
            overlays.append({
                "type": "cultural_heritage",
                "description": "文化資產潛在範圍",
                "in_scope": True,
            })
        return overlays

    def get_road_info(self, address_or_lot: str) -> dict[str, Any] | None:
        # 各地址對應的道路資訊 mock
        road_data: dict[str, dict[str, Any]] = {
            "臺北市大安區仁愛路三段1號": {
                "fronts_planned_road": True, "road_width_m": 40.0,
                "planned_width_m": 40.0, "road_opened": True,
                "road_name": "仁愛路三段", "exempt_from_building_line": False,
            },
            "臺北市信義區松仁路100號": {
                "fronts_planned_road": True, "road_width_m": 25.0,
                "planned_width_m": 25.0, "road_opened": True,
                "road_name": "松仁路", "exempt_from_building_line": False,
            },
            "臺北市中山區南京東路二段50號": {
                "fronts_planned_road": True, "road_width_m": 30.0,
                "planned_width_m": 30.0, "road_opened": True,
                "road_name": "南京東路二段", "exempt_from_building_line": False,
            },
            "臺北市內湖區瑞光路513號": {
                "fronts_planned_road": True, "road_width_m": 20.0,
                "planned_width_m": 20.0, "road_opened": True,
                "road_name": "瑞光路", "exempt_from_building_line": False,
            },
            "臺北市北投區中央北路四段100號": {
                "fronts_planned_road": True, "road_width_m": 12.0,
                "planned_width_m": 15.0, "road_opened": True,
                "road_name": "中央北路四段", "exempt_from_building_line": False,
            },
            "臺北市士林區中山北路七段200號": {
                "fronts_planned_road": True, "road_width_m": 25.0,
                "planned_width_m": 25.0, "road_opened": True,
                "road_name": "中山北路七段", "exempt_from_building_line": False,
            },
            "臺北市松山區敦化北路100號": {
                "fronts_planned_road": True, "road_width_m": 50.0,
                "planned_width_m": 50.0, "road_opened": True,
                "road_name": "敦化北路", "exempt_from_building_line": False,
            },
            "臺北市大同區重慶北路三段1號": {
                "fronts_planned_road": True, "road_width_m": 20.0,
                "planned_width_m": 20.0, "road_opened": True,
                "road_name": "重慶北路三段", "exempt_from_building_line": False,
            },
        }

        result = _fuzzy_lookup(road_data, address_or_lot)
        if result:
            return result

        # 預設：臨已開闢計畫道路
        return {
            "fronts_planned_road": True,
            "road_width_m": 15.0,
            "planned_width_m": 15.0,
            "road_opened": True,
            "road_name": "計畫道路",
            "exempt_from_building_line": False,
        }
