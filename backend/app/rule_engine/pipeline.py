"""規則引擎 Pipeline — 依序執行 19 點評估，組裝 EvaluationReport。"""

from datetime import datetime, timezone

from app.config import settings
from app.data_sources.base import DataSource
from app.data_sources.mock_zone import MockZoneDataSource
from app.rule_engine.base import EvaluationContext
from app.rule_engine.building_line import BuildingLineModule
from app.rule_engine.building_mass import BuildingMassModule
from app.rule_engine.building_permit import BuildingPermitModule
from app.rule_engine.conclusion import ConclusionModule, STATUS_TEXT
from app.rule_engine.far_bcr import FarBcrModule
from app.rule_engine.far_bonus import FarBonusModule
from app.rule_engine.far_transfer import FarTransferModule
from app.rule_engine.fire_safety import FireSafetyModule
from app.rule_engine.odd_lot import OddLotModule
from app.rule_engine.overlays import OverlaysModule
from app.rule_engine.parking import ParkingModule
from app.rule_engine.site_normalizer import SiteNormalizer
from app.rule_engine.traffic import TrafficModule
from app.rule_engine.urban_renewal import UrbanRenewalModule
from app.rule_engine.zoning import ZoningModule
from app.schemas.enums import FinalStatus
from app.schemas.evidence import LegalBasis
from app.schemas.input import SiteInput
from app.schemas.output import ChecklistItem, EvaluationReport, ModuleResult, OverlayRisk


def _empty_result(module: str) -> ModuleResult:
    return ModuleResult(
        module=module,
        status=FinalStatus.REVIEW_REQUIRED,
        review_required=True,
        notes=["模組未執行"],
    )


# 19 點定義：(編號, 標題, 對應模組名)
CHECKLIST_19_DEF = [
    (1, "都市計畫 / 使用分區", "zoning"),
    (2, "使用項目是否合法", "zoning"),
    (3, "畸零地 / 開發規模", "odd_lot"),
    (4, "臨路 / 建築線", "building_line"),
    (5, "是否可申請建照", "building_permit"),
    (6, "容積率", "far_bcr"),
    (7, "建蔽率", "coverage"),
    (8, "容積獎勵", "far_bonus"),
    (9, "容積移轉", "far_transfer"),
    (10, "建築量體（高度/日照/斜線）", "building_mass"),
    (11, "防火間距 / 開口限制", "fire_safety"),
    (12, "停車數量", "parking"),
    (13, "車道 / 交通動線", "traffic"),
    (14, "山坡地限制", None),      # 疊圖子項
    (15, "文化資產", None),        # 疊圖子項
    (16, "環境影響評估", None),    # 疊圖子項
    (17, "都市設計審議", None),    # 疊圖子項
    (18, "都市更新 / 危老審議", "urban_renewal"),
    (19, "建造執照核發", "building_permit"),
]

# 疊圖子項目對應
OVERLAY_POINT_MAP = {
    14: "hillside",
    15: "cultural_heritage",
    16: "eia",
    17: "urban_design_review",
}


def _build_checklist(ctx: EvaluationContext) -> list[ChecklistItem]:
    items: list[ChecklistItem] = []
    for num, title, mod_name in CHECKLIST_19_DEF:

        # 疊圖類 (14-17) 要看特定風險
        if num in OVERLAY_POINT_MAP:
            overlay_key = OVERLAY_POINT_MAP[num]
            overlays_result = ctx.get_result("overlays")
            if overlays_result and overlays_result.result.get("risks"):
                matched = [r for r in overlays_result.result["risks"] if r["risk_type"] == overlay_key]
                if matched:
                    r = matched[0]
                    items.append(ChecklistItem(
                        point_number=num, title=title, v1_scope=True,
                        status=FinalStatus(r["status"]),
                        status_text=r["description"],
                        notes=[r["description"]],
                    ))
                else:
                    items.append(ChecklistItem(
                        point_number=num, title=title, v1_scope=True,
                        status=FinalStatus.AUTO_PASS,
                        status_text="未偵測到風險", notes=["未偵測到此項疊圖風險"],
                    ))
            else:
                items.append(ChecklistItem(
                    point_number=num, title=title, v1_scope=True,
                    status=FinalStatus.AUTO_PASS,
                    status_text="未偵測到風險", notes=[],
                ))
            continue

        # 一般模組
        result = ctx.get_result(mod_name) if mod_name else None
        if result:
            items.append(ChecklistItem(
                point_number=num, title=title, v1_scope=True,
                status=result.status,
                status_text="; ".join(result.notes[:2]),
                notes=result.notes,
            ))
        else:
            items.append(ChecklistItem(
                point_number=num, title=title, v1_scope=True,
                status=FinalStatus.REVIEW_REQUIRED,
                status_text="模組未執行", notes=["模組未執行"],
            ))

    return items


def run_pipeline(site_input: SiteInput, data_source: DataSource | None = None) -> EvaluationReport:
    ds = data_source or MockZoneDataSource()
    raw = site_input.model_dump()

    # 自動查詢基地面積（若使用者未填）
    if raw.get("site_area_sqm") is None:
        site_info = ds.get_site_info(raw["address_or_lot"])
        if site_info and site_info.get("site_area_sqm"):
            raw["site_area_sqm"] = site_info["site_area_sqm"]
            raw["_area_auto"] = True
        else:
            raw["site_area_sqm"] = None  # 保持缺失，由各模組處理
            raw["_area_missing"] = True

    ctx = EvaluationContext(raw)

    # === 19 點依序評估 ===

    # Step 1: 基地正規化
    SiteNormalizer().evaluate(ctx)

    # 第1-2點: 分區 / 用途
    ZoningModule(ds).evaluate(ctx)

    # 第3點: 畸零地
    OddLotModule().evaluate(ctx)

    # 第4點: 建築線
    BuildingLineModule(ds).evaluate(ctx)

    # 第6-7點: 容積 / 建蔽
    FarBcrModule().evaluate(ctx)

    # 第8點: 容積獎勵
    FarBonusModule().evaluate(ctx)

    # 第9點: 容積移轉
    FarTransferModule().evaluate(ctx)

    # 第10點: 建築量體
    BuildingMassModule().evaluate(ctx)

    # 第11點: 防火間距
    FireSafetyModule().evaluate(ctx)

    # 第12點: 停車
    ParkingModule().evaluate(ctx)

    # 第13點: 車道/交通
    TrafficModule().evaluate(ctx)

    # 第14-17點: 疊圖風險
    OverlaysModule(ds).evaluate(ctx)

    # 第18點: 都更/危老
    UrbanRenewalModule().evaluate(ctx)

    # 第5,19點: 建照核發（綜合判定，需在其他模組之後）
    BuildingPermitModule().evaluate(ctx)

    # 結論整合
    conclusion_result = ConclusionModule().evaluate(ctx)

    # 收集所有法規依據（去重）
    all_basis: list[LegalBasis] = []
    for r in ctx.module_results.values():
        all_basis.extend(r.legal_basis)
    seen = set()
    unique_basis: list[LegalBasis] = []
    for b in all_basis:
        key = (b.law_name, b.article)
        if key not in seen:
            seen.add(key)
            unique_basis.append(b)

    blockers = conclusion_result.result.get("blockers", [])
    high_risks = conclusion_result.result.get("high_risks", [])
    review_items = conclusion_result.result.get("review_items", [])

    overlays_result = ctx.get_result("overlays")
    overlay_risks = []
    if overlays_result and overlays_result.result.get("risks"):
        overlay_risks = [OverlayRisk(**r) for r in overlays_result.result["risks"]]

    final_status = FinalStatus(conclusion_result.result["final_status"])

    checklist = _build_checklist(ctx)

    # 標示資料模式
    data_mode = "mock" if isinstance(ds, MockZoneDataSource) else "live"

    return EvaluationReport(
        project_id=ctx.site_identity.get("project_id", "UNKNOWN"),
        site_identity=ctx.site_identity,
        data_mode=data_mode,
        zoning_result=ctx.get_result("zoning") or _empty_result("zoning"),
        use_result=ctx.get_result("zoning") or _empty_result("use"),
        road_frontage_result=ctx.get_result("road_frontage") or _empty_result("road_frontage"),
        building_line_result=ctx.get_result("building_line") or _empty_result("building_line"),
        odd_lot_result=ctx.get_result("odd_lot") or _empty_result("odd_lot"),
        far_result=ctx.get_result("far_bcr") or _empty_result("far"),
        coverage_result=ctx.get_result("coverage") or _empty_result("coverage"),
        parking_result=ctx.get_result("parking") or _empty_result("parking"),
        overlay_risks=overlay_risks,
        blockers=blockers,
        high_risk_items=high_risks,
        manual_review_items=review_items,
        final_status=final_status,
        final_status_text=STATUS_TEXT[final_status],
        legal_basis=unique_basis,
        source_evidence=unique_basis,
        checklist_19=checklist,
        generated_at=datetime.now(timezone.utc),
        rule_version=settings.rule_version,
    )
