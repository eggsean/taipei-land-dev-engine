# External Integrations & Data Sources

## Data Source Architecture

Abstract `DataSource` interface (`data_sources/base.py`):
- `get_site_info(address)` → site area, cadastral data
- `get_zoning(address)` → zone code, FAR, BCR, allowed uses
- `get_overlays(address)` → GIS overlay hits
- `get_road_info(address)` → road frontage, building line data

**Current**: `MockZoneDataSource` (in-memory dictionaries)
**Future**: Real Taipei city API integrations

## Mock Data Coverage

### Addresses (~10 sample locations)
- 大安區仁愛路 → 住三, 520m²
- 信義區松仁路 → 商二, 1200m²
- 中山區南京東路 → 商三, 800m²
- 內湖區瑞光路 → 工三, 2000m²
- 北投區中央北路 → 住二, 350m²
- 士林區中山北路 → 住一, 180m²
- 松山區敦化北路 → 商四, 600m²
- 大同區重慶北路 → 住四, 450m²

### Overlay Detection (keyword-based)
- "北投" → hillside control zone
- "大安" / "信義" → urban design review area
- "大同" → cultural heritage zone

### Unknown Addresses
- `get_zoning()` returns `None` → REVIEW_REQUIRED
- `get_road_info()` returns `None` → REVIEW_REQUIRED
- `get_site_info()` returns `None` → area stays missing

## Planned Real Integrations

| Source | URL | Purpose |
|--------|-----|---------|
| 臺北市土地使用分區查詢 | https://zone.udd.gov.taipei/ | Zoning classification |
| 都市計畫整合查詢系統 | — | Overlays, urban design, building line |
| 建管處系統 | — | Permit status, building history |
| 中央法規資料庫 | https://law.moj.gov.tw/ | National building code |

## Internal Database

- **Engine**: SQLite via aiosqlite (async)
- **Status**: Schema configured, ORM models stub only
- **Project History**: Currently in-memory dict (not persisted)

## Frontend → Backend

- Axios client, base URL `/api/v1`
- Vite proxy: `/api/*` → `http://localhost:9000`
- No external API calls from frontend
