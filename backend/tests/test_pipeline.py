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
    assert report.module_results["zoning"].status == FinalStatus.AUTO_PASS
    assert report.module_results["far_bcr"].status == FinalStatus.AUTO_PASS
    assert report.module_results["parking"].status == FinalStatus.AUTO_PASS
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
    assert report.module_results["zoning"].status == FinalStatus.AUTO_FAIL
    assert report.final_status == FinalStatus.AUTO_FAIL


def test_small_lot_odd_lot_suspect():
    """小面積地 → 疑似畸零地。"""
    site = SiteInput(
        address_or_lot="臺北市大安區仁愛路三段1號",
        site_area_sqm=8,  # 約 2.8m 邊長，低於最小寬度
        intended_use=IntendedUse.RESIDENTIAL,
    )
    report = run_pipeline(site)
    assert report.module_results["odd_lot"].status == FinalStatus.REVIEW_REQUIRED
    assert report.module_results["odd_lot"].result["is_odd_lot_suspect"] is True


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


def test_unknown_address_not_auto_pass():
    """未知地址不應得到 AUTO_PASS，應為 REVIEW_REQUIRED 或更差。"""
    site = SiteInput(
        address_or_lot="臺北市某某區不存在路999號",
        site_area_sqm=300,
        intended_use=IntendedUse.RESIDENTIAL,
    )
    report = run_pipeline(site)
    assert report.final_status != FinalStatus.AUTO_PASS
    # 分區應該是 REVIEW_REQUIRED（查無資料）
    assert report.module_results["zoning"].status == FinalStatus.REVIEW_REQUIRED


def test_unknown_address_no_area_stays_missing():
    """未知地址且未填面積 → 面積來源標示為「查無資料」。"""
    site = SiteInput(
        address_or_lot="臺北市某某區不存在路999號",
        intended_use=IntendedUse.RESIDENTIAL,
    )
    report = run_pipeline(site)
    assert report.site_identity["area_source"] == "查無資料"
    assert report.site_identity["site_area_sqm"] is None


def test_auto_area_provenance():
    """自動查詢面積 → 面積來源標示為「系統自動查詢」。"""
    site = SiteInput(
        address_or_lot="臺北市大安區仁愛路三段1號",
        intended_use=IntendedUse.RESIDENTIAL,
    )
    report = run_pipeline(site)
    assert report.site_identity["area_source"] == "系統自動查詢"
    assert report.site_identity["site_area_sqm"] == 520.0


def test_manual_area_provenance():
    """手動填寫面積 → 面積來源標示為「使用者輸入」。"""
    site = SiteInput(
        address_or_lot="臺北市大安區仁愛路三段1號",
        site_area_sqm=300,
        intended_use=IntendedUse.RESIDENTIAL,
    )
    report = run_pipeline(site)
    assert report.site_identity["area_source"] == "使用者輸入"


def test_blocker_not_in_review_items():
    """AUTO_FAIL 項目應出現在 blockers，不應出現在 manual_review_items。"""
    site = SiteInput(
        address_or_lot="臺北市內湖區瑞光路513號",
        site_area_sqm=1000,
        intended_use=IntendedUse.RESIDENTIAL,
    )
    report = run_pipeline(site)
    assert report.final_status == FinalStatus.AUTO_FAIL
    assert len(report.blockers) > 0
    # blocker 的模組名不應重複出現在 manual_review_items
    blocker_mods = {b.split("]")[0].strip("[") for b in report.blockers}
    review_mods = {r.split("]")[0].strip("[") for r in report.manual_review_items}
    assert blocker_mods.isdisjoint(review_mods)


def test_data_mode_is_mock():
    """使用 MockZoneDataSource 時報告標示 data_mode=mock。"""
    site = SiteInput(
        address_or_lot="臺北市大安區仁愛路三段1號",
        site_area_sqm=500,
        intended_use=IntendedUse.RESIDENTIAL,
    )
    report = run_pipeline(site)
    assert report.data_mode == "mock"


def test_sunlight_review_is_high_risk():
    """住宅區 7 層以上需日照檢討 → 應為 HIGH_RISK，不能是 AUTO_PASS。"""
    site = SiteInput(
        address_or_lot="臺北市大安區仁愛路三段1號",
        site_area_sqm=500,
        intended_use=IntendedUse.RESIDENTIAL,
    )
    report = run_pipeline(site)
    mass = report.module_results["building_mass"]
    if mass.result.get("needs_sunlight_review"):
        assert mass.status == FinalStatus.HIGH_RISK


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
