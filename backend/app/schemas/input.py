from pydantic import BaseModel, Field

from app.schemas.enums import DevelopmentScheme, IntendedUse


class SiteInput(BaseModel):
    address_or_lot: str = Field(..., min_length=2, description="地址或地號")
    site_area_sqm: float | None = Field(None, gt=0, description="基地面積（平方公尺），不填則自動查詢")
    intended_use: IntendedUse = Field(..., description="預計用途")

    single_owner: bool | None = Field(None, description="是否單一地主")
    can_merge_adjacent: bool | None = Field(None, description="是否可整合鄰地")
    has_existing_building: bool | None = Field(None, description="是否已有建物")
    has_permit: bool | None = Field(None, description="是否已有建照/使照")
    development_scheme: DevelopmentScheme | None = Field(None, description="預計制度")
