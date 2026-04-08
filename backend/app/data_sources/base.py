from abc import ABC, abstractmethod
from typing import Any


class DataSource(ABC):
    @abstractmethod
    def get_site_info(self, address_or_lot: str) -> dict[str, Any] | None:
        """查詢基地基本資訊（面積、地籍資料）"""

    @abstractmethod
    def get_zoning(self, address_or_lot: str) -> dict[str, Any] | None:
        """查詢土地使用分區"""

    @abstractmethod
    def get_overlays(self, address_or_lot: str) -> list[dict[str, Any]]:
        """查詢疊圖風險（都審、山坡地、文資、環評）"""

    @abstractmethod
    def get_road_info(self, address_or_lot: str) -> dict[str, Any] | None:
        """查詢臨路與建築線資訊"""
