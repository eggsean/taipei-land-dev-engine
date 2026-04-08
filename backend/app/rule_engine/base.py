"""規則引擎基底類別與評估上下文。"""

from abc import ABC, abstractmethod
from typing import Any

from app.schemas.output import ModuleResult


class EvaluationContext:
    """在 pipeline 中累積各模組結果的上下文物件。"""

    def __init__(self, raw_input: dict[str, Any]) -> None:
        self.raw_input = raw_input
        self.site_identity: dict[str, Any] = {}
        self.zoning_data: dict[str, Any] | None = None
        self.road_info: dict[str, Any] | None = None
        self.overlays: list[dict[str, Any]] = []
        self.module_results: dict[str, ModuleResult] = {}

    def set_result(self, module_name: str, result: ModuleResult) -> None:
        self.module_results[module_name] = result

    def get_result(self, module_name: str) -> ModuleResult | None:
        return self.module_results.get(module_name)


class RuleModule(ABC):
    module_name: str

    @abstractmethod
    def evaluate(self, ctx: EvaluationContext) -> ModuleResult:
        ...
