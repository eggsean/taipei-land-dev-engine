"""停車模組測試 — 驗證三層 fallback。"""

from app.rule_engine.base import EvaluationContext
from app.rule_engine.far_bcr import FarBcrModule
from app.rule_engine.parking import ParkingModule
from app.rule_engine.site_normalizer import SiteNormalizer
from app.rule_engine.zoning import ZoningModule
from app.data_sources.mock_zone import MockZoneDataSource
from app.schemas.enums import IntendedUse


def _make_ctx(address: str, area: float, use: str) -> EvaluationContext:
    ctx = EvaluationContext({
        "address_or_lot": address,
        "site_area_sqm": area,
        "intended_use": use,
    })
    ds = MockZoneDataSource()
    SiteNormalizer().evaluate(ctx)
    ZoningModule(ds).evaluate(ctx)
    FarBcrModule().evaluate(ctx)
    return ctx


def test_residential_parking():
    ctx = _make_ctx("臺北市大安區仁愛路三段1號", 500, "residential")
    result = ParkingModule().evaluate(ctx)
    assert result.result["required_car_spaces"] > 0
    assert result.result["required_motor_spaces"] > 0
    assert "土地使用分區管制" in result.result["calculation_basis"]


def test_industrial_parking_uses_building_code():
    ctx = _make_ctx("臺北市內湖區瑞光路513號", 1000, "industrial_office")
    result = ParkingModule().evaluate(ctx)
    assert result.result["required_car_spaces"] > 0
