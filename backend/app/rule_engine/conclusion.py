"""Step 8: 結論整合 — 最嚴格原則，但區分必要模組與加分模組。"""

from app.rule_engine.base import EvaluationContext, RuleModule
from app.schemas.enums import FinalStatus
from app.schemas.output import ModuleResult

STATUS_PRIORITY = {
    FinalStatus.AUTO_FAIL: 0,
    FinalStatus.REVIEW_REQUIRED: 1,
    FinalStatus.HIGH_RISK: 2,
    FinalStatus.AUTO_PASS: 3,
}

STATUS_TEXT = {
    FinalStatus.AUTO_PASS: "可初步開發",
    FinalStatus.AUTO_FAIL: "不建議取得",
    FinalStatus.REVIEW_REQUIRED: "需補件 / 需人工判定",
    FinalStatus.HIGH_RISK: "高風險，建議先人工複核",
}

# 必要模組：FAIL 會一票否決
CRITICAL_MODULES = [
    "zoning", "building_line", "odd_lot", "far_bcr", "parking",
    "overlays", "building_mass", "fire_safety", "traffic",
    "building_permit",
]

# 加分/可選模組：FAIL 不影響整體結論（不適用 ≠ 不可行）
OPTIONAL_MODULES = [
    "far_bonus", "far_transfer", "urban_renewal",
]


class ConclusionModule(RuleModule):
    module_name = "conclusion"

    def evaluate(self, ctx: EvaluationContext) -> ModuleResult:
        critical_statuses: list[FinalStatus] = []
        review_items: list[str] = []
        notes: list[str] = []
        optional_notes: list[str] = []

        for mod_name in CRITICAL_MODULES:
            result = ctx.get_result(mod_name)
            if not result:
                continue
            critical_statuses.append(result.status)
            if result.review_required:
                review_items.append(f"[{mod_name}] {'; '.join(result.notes[:1])}")

        for mod_name in OPTIONAL_MODULES:
            result = ctx.get_result(mod_name)
            if not result:
                continue
            if result.status == FinalStatus.AUTO_FAIL:
                optional_notes.append(f"[{mod_name}] 不適用（不影響開發可行性）")
            elif result.review_required:
                review_items.append(f"[{mod_name}] {'; '.join(result.notes[:1])}")

        if not critical_statuses:
            final = FinalStatus.REVIEW_REQUIRED
        else:
            final = min(critical_statuses, key=lambda s: STATUS_PRIORITY[s])

        notes.append(f"最終結論: {STATUS_TEXT[final]}")
        if review_items:
            notes.append(f"需人工覆核項目數: {len(review_items)}")
        if optional_notes:
            notes.extend(optional_notes)

        all_modules = CRITICAL_MODULES + OPTIONAL_MODULES
        r = ModuleResult(
            module=self.module_name,
            status=final,
            result={
                "final_status": final.value,
                "final_status_text": STATUS_TEXT[final],
                "review_items": review_items,
                "module_statuses": {
                    mod: ctx.get_result(mod).status.value
                    for mod in all_modules if ctx.get_result(mod)
                },
            },
            review_required=bool(review_items),
            notes=notes,
        )
        ctx.set_result(self.module_name, r)
        return r
