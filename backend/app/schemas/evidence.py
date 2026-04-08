from pydantic import BaseModel

from app.schemas.enums import SourceType


class LegalBasis(BaseModel):
    law_name: str
    article: str
    source_url: str
    source_type: SourceType
    is_official_proof: bool = False
    review_required: bool = False
    notes: list[str] = []
