from enum import Enum


class FinalStatus(str, Enum):
    AUTO_PASS = "AUTO_PASS"
    AUTO_FAIL = "AUTO_FAIL"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    HIGH_RISK = "HIGH_RISK"


class SourceType(str, Enum):
    CENTRAL_LAW = "central_law"
    LOCAL_LAW = "local_law"
    GIS_DATA = "gis_data"
    SYSTEM_QUERY = "system_query"


class IntendedUse(str, Enum):
    RESIDENTIAL = "residential"
    OFFICE = "office"
    COMMERCIAL = "commercial"
    HOTEL = "hotel"
    INDUSTRIAL_OFFICE = "industrial_office"


class DevelopmentScheme(str, Enum):
    GENERAL = "general"
    URBAN_RENEWAL = "urban_renewal"
    DANGEROUS_OLD = "dangerous_old"
