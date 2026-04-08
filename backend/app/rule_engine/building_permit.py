"""第5、19點：建造執照核發可行性綜合初判。

自動化邏輯：
- 收集所有前置條件模組的狀態
- 全部 AUTO_PASS → AUTO_PASS
- 有 AUTO_FAIL → AUTO_FAIL
- 有 HIGH_RISK 但無 FAIL → HIGH_RISK
- 其餘 → REVIEW_REQUIRED
"""

from app.rule_engine.base import EvaluationContext, RuleModule
from app.schemas.enums import FinalStatus, SourceType
from app.schemas.evidence import LegalBasis
from app.schemas.output import ModuleResult

# 建照核發前置條件
PREREQUISITES = [
    ("zoning", "分區/用途合法"),
    ("building_line", "建築線取得"),
    ("odd_lot", "非畸零地或已完成調處"),
    ("far_bcr", "容積/建蔽合規"),
    ("parking", "停車設置合規"),
    ("building_mass", "建築量體合規"),
    ("fire_safety", "防火間距合規"),
]


class BuildingPermitModule(RuleModule):
    module_name = "building_permit"

    def evaluate(self, ctx: EvaluationContext) -> ModuleResult:
        notes = []
        passed = []
        blockers = []
        high_risks = []
        review_needed = []

        for mod_name, desc in PREREQUISITES:
            result = ctx.get_result(mod_name)
            if not result:
                review_needed.append(f"{desc}：未評估")
                continue
            if result.status == FinalStatus.AUTO_FAIL:
                blockers.append(f"{desc}：不通過")
            elif result.status == FinalStatus.REVIEW_REQUIRED:
                review_needed.append(f"{desc}：需覆核")
            elif result.status == FinalStatus.HIGH_RISK:
                high_risks.append(f"{desc}：高風險")
            else:
                passed.append(f"{desc}：通過")

        # 疊圖風險
        overlays = ctx.get_result("overlays")
        overlay_risks_count = 0
        if overlays and overlays.result.get("risks"):
            for risk in overlays.result["risks"]:
                overlay_risks_count += 1
                high_risks.append(f"{risk['description']}：需確認")

        # 判定結論
        if blockers:
            status = FinalStatus.AUTO_FAIL
            notes.append("存在前置條件不通過項目，無法申請建照：")
            notes.extend([f"  - {b}" for b in blockers])
        elif not review_needed and not high_risks:
            status = FinalStatus.AUTO_PASS
            notes.append("所有前置條件初判通過，可進入建照申請程序")
        elif review_needed and not high_risks:
            # 只有少量需覆核，但無高風險
            status = FinalStatus.REVIEW_REQUIRED
            notes.append("部分前置條件需確認：")
            notes.extend([f"  - {r}" for r in review_needed])
        else:
            status = FinalStatus.HIGH_RISK
            notes.append("前置條件存在高風險項目：")
            notes.extend([f"  - {r}" for r in high_risks])
            if review_needed:
                notes.append("另有待覆核項目：")
                notes.extend([f"  - {r}" for r in review_needed])

        if passed:
            notes.append(f"已通過項目: {len(passed)}/{len(PREREQUISITES)}")

        notes.append("")
        notes.append("建造執照核發需經建管處正式審查，系統做前置初判")

        r = ModuleResult(
            module=self.module_name,
            status=status,
            result={
                "blockers": blockers,
                "high_risks": high_risks,
                "review_needed": review_needed,
                "passed": passed,
                "prerequisite_count": len(PREREQUISITES),
                "pass_count": len(passed),
                "overlay_risks_count": overlay_risks_count,
            },
            review_required=status != FinalStatus.AUTO_PASS,
            notes=notes,
            legal_basis=[
                LegalBasis(
                    law_name="建築法",
                    article="第30條（建造執照申請）",
                    source_url="https://law.moj.gov.tw/",
                    source_type=SourceType.CENTRAL_LAW,
                ),
                LegalBasis(
                    law_name="臺北市建築管理自治條例",
                    article="第3條、第4條",
                    source_url="https://laws.gov.taipei/Law/LawSearch/LawArticleContent/FL004106",
                    source_type=SourceType.LOCAL_LAW,
                ),
            ],
        )
        ctx.set_result(self.module_name, r)
        return r
