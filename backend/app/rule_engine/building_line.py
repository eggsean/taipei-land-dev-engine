"""第4點：臨路/建築線前置判定。

自動化邏輯：
- 臨接已開闢計畫道路且道路寬度 ≥ 計畫寬度 → 建築線依道路邊界指示 → AUTO_PASS
- 臨接已開闢計畫道路但道路尚未拓寬至計畫寬度 → 需指定建築線 → REVIEW_REQUIRED
- 免指示建築線地區 → AUTO_PASS
- 未臨接計畫道路 → AUTO_FAIL
- 道路資訊不完整 → REVIEW_REQUIRED
"""

from app.data_sources.base import DataSource
from app.rule_engine.base import EvaluationContext, RuleModule
from app.schemas.enums import FinalStatus, SourceType
from app.schemas.evidence import LegalBasis
from app.schemas.output import ModuleResult


class BuildingLineModule(RuleModule):
    module_name = "building_line"

    def __init__(self, data_source: DataSource) -> None:
        self.ds = data_source

    def evaluate(self, ctx: EvaluationContext) -> ModuleResult:
        address = ctx.site_identity.get("normalized", ctx.raw_input["address_or_lot"])
        road_info = self.ds.get_road_info(address)
        ctx.road_info = road_info

        basis_local = LegalBasis(
            law_name="臺北市建築管理自治條例",
            article="第3條、第4條",
            source_url="https://laws.gov.taipei/Law/LawSearch/LawArticleContent/FL004106",
            source_type=SourceType.LOCAL_LAW,
        )
        basis_central = LegalBasis(
            law_name="建築法",
            article="第48條（建築線指示）",
            source_url="https://law.moj.gov.tw/",
            source_type=SourceType.CENTRAL_LAW,
        )
        all_basis = [basis_local, basis_central]

        if not road_info:
            return self._result(ctx, FinalStatus.REVIEW_REQUIRED, True,
                {"fronts_planned_road": None},
                ["無法查詢道路資訊，需人工覆核"], all_basis)

        fronts_road = road_info.get("fronts_planned_road", False)
        exempt = road_info.get("exempt_from_building_line", False)
        road_width = road_info.get("road_width_m", 0)
        planned_width = road_info.get("planned_width_m", road_width)
        road_opened = road_info.get("road_opened", True)

        result_data = {
            **road_info,
            "building_line_status": "",
        }

        # 情況 1：未臨計畫道路
        if not fronts_road:
            result_data["building_line_status"] = "不得建築"
            return self._result(ctx, FinalStatus.AUTO_FAIL, False,
                result_data,
                [f"基地未臨接計畫道路，依建築法第48條不得建築"],
                all_basis)

        # 情況 2：免指示建築線地區
        if exempt:
            result_data["building_line_status"] = "免指示"
            return self._result(ctx, FinalStatus.AUTO_PASS, False,
                result_data,
                ["基地屬免申請指示建築線地區，無需另行申請"],
                all_basis)

        # 情況 3：臨已開闢計畫道路，現況寬度 ≥ 計畫寬度
        #   → 建築線依道路邊界線指示（最常見情況，可自動判定）
        if road_opened and road_width >= planned_width and road_width > 0:
            result_data["building_line_status"] = "依道路邊界指示"
            return self._result(ctx, FinalStatus.AUTO_PASS, False,
                result_data,
                [
                    f"基地臨接已開闢計畫道路（寬 {road_width}m），道路寬度已達計畫寬度",
                    "建築線依道路邊界線指示（建築法第48條第1項）",
                    "建築線位置 = 道路邊界線",
                ],
                all_basis)

        # 情況 4：臨計畫道路但尚未拓寬至計畫寬度
        #   → 需「指定」建築線（退縮至計畫道路邊界）
        if road_opened and road_width < planned_width:
            setback = (planned_width - road_width) / 2
            result_data["building_line_status"] = "需指定（退縮）"
            result_data["required_setback_m"] = round(setback, 2)
            return self._result(ctx, FinalStatus.HIGH_RISK, False,
                result_data,
                [
                    f"道路現況寬度 {road_width}m < 計畫寬度 {planned_width}m",
                    f"建築線需退縮至計畫道路邊界，估算退縮約 {setback:.1f}m",
                    "依建築法第48條，建築線由主管機關指定",
                    "退縮部分不得計入建蔽率與容積率計算基地面積",
                ],
                all_basis)

        # 情況 5：道路尚未開闢
        if not road_opened:
            result_data["building_line_status"] = "道路未開闢"
            return self._result(ctx, FinalStatus.REVIEW_REQUIRED, True,
                result_data,
                [
                    "計畫道路尚未開闢",
                    "建築線需依計畫道路境界線指定",
                    "需確認計畫道路位置與寬度",
                ],
                all_basis)

        # 情況 6：有臨路但資訊不完整
        result_data["building_line_status"] = "依道路邊界指示"
        return self._result(ctx, FinalStatus.AUTO_PASS, False,
            result_data,
            [
                f"基地臨接計畫道路（寬 {road_width}m）",
                "建築線依道路邊界線指示",
            ],
            all_basis)

    def _result(self, ctx: EvaluationContext, status: FinalStatus,
                review: bool, result: dict, notes: list[str],
                basis: list[LegalBasis]) -> ModuleResult:
        r = ModuleResult(
            module=self.module_name,
            status=status,
            result=result,
            review_required=review,
            notes=notes,
            legal_basis=basis,
        )
        ctx.set_result(self.module_name, r)
        ctx.set_result("road_frontage", r)
        return r
