"""端對端 pipeline 測試。"""

from app.rule_engine.pipeline import run_pipeline
from app.schemas.enums import FinalStatus, IntendedUse
from app.schemas.input import SiteInput


def test_residential_in_residential_zone():
    """住三區做住宅 → 分區通過，建築線需覆核，整體應為 REVIEW_REQUIRED。"""
    site = SiteInput(
        address_or_lot="臺北市大安區仁愛路三段1號",
        site_area_sqm=500,
        intended_use=IntendedUse.RESIDENTIAL,
    )
    report = run_pipeline(site)
    assert report.zoning_result.status == FinalStatus.AUTO_PASS
    assert report.far_result.status == FinalStatus.AUTO_PASS
    assert report.parking_result.status == FinalStatus.AUTO_PASS
    # 建築線需覆核，所以整體不會是 AUTO_PASS
    assert report.final_status in (FinalStatus.REVIEW_REQUIRED, FinalStatus.HIGH_RISK)
    assert report.project_id.startswith("TPE-")


def test_residential_in_industrial_zone():
    """工三區做住宅 → AUTO_FAIL。"""
    site = SiteInput(
        address_or_lot="臺北市內湖區瑞光路513號",
        site_area_sqm=1000,
        intended_use=IntendedUse.RESIDENTIAL,
    )
    report = run_pipeline(site)
    assert report.zoning_result.status == FinalStatus.AUTO_FAIL
    assert report.final_status == FinalStatus.AUTO_FAIL


def test_small_lot_odd_lot_suspect():
    """小面積地 → 疑似畸零地。"""
    site = SiteInput(
        address_or_lot="臺北市大安區仁愛路三段1號",
        site_area_sqm=8,  # 約 2.8m 邊長，低於最小寬度
        intended_use=IntendedUse.RESIDENTIAL,
    )
    report = run_pipeline(site)
    assert report.odd_lot_result.status == FinalStatus.REVIEW_REQUIRED
    assert report.odd_lot_result.result["is_odd_lot_suspect"] is True


def test_large_site_triggers_urban_design_review():
    """位於都審地區 → 觸發都審。依第3條，一般開發需面積≥6000m²且樓地板≥30000m²。
    大安區在mock中標記為都審地區，所以即使面積小也會觸發。"""
    site = SiteInput(
        address_or_lot="臺北市大安區仁愛路三段1號",
        site_area_sqm=500,
        intended_use=IntendedUse.RESIDENTIAL,
    )
    report = run_pipeline(site)
    risk_types = [r.risk_type for r in report.overlay_risks]
    assert "urban_design_review" in risk_types


def test_small_site_no_urban_design_review():
    """不在都審地區且面積未達門檻 → 不觸發都審。"""
    site = SiteInput(
        address_or_lot="臺北市士林區中山北路七段200號",
        site_area_sqm=180,
        intended_use=IntendedUse.RESIDENTIAL,
    )
    report = run_pipeline(site)
    risk_types = [r.risk_type for r in report.overlay_risks]
    assert "urban_design_review" not in risk_types


def test_report_has_legal_basis():
    """報告包含法規依據。"""
    site = SiteInput(
        address_or_lot="臺北市信義區松仁路100號",
        site_area_sqm=300,
        intended_use=IntendedUse.OFFICE,
    )
    report = run_pipeline(site)
    assert len(report.legal_basis) > 0
    assert report.rule_version
    assert report.generated_at


def test_auto_area_lookup():
    """不填面積 → 系統自動查詢。"""
    site = SiteInput(
        address_or_lot="臺北市大安區仁愛路三段1號",
        intended_use=IntendedUse.RESIDENTIAL,
    )
    report = run_pipeline(site)
    assert report.site_identity["site_area_sqm"] == 520.0
    assert report.project_id.startswith("TPE-")


def test_checklist_19_complete():
    """報告包含完整 19 點 checklist，全部為 V1。"""
    site = SiteInput(
        address_or_lot="臺北市大安區仁愛路三段1號",
        site_area_sqm=500,
        intended_use=IntendedUse.RESIDENTIAL,
    )
    report = run_pipeline(site)
    assert len(report.checklist_19) == 19
    # 全部都是 V1
    assert all(c.v1_scope for c in report.checklist_19)
    # 全部都有狀態
    assert all(c.status is not None for c in report.checklist_19)
    # 編號 1-19
    nums = [c.point_number for c in report.checklist_19]
    assert nums == list(range(1, 20))
