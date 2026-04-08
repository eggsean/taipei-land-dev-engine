# Architecture

## System Overview

Full-stack legal-computational system for automated preliminary legal opinions on Taipei land development. Evaluates sites against 19 regulatory checkpoints.

```
Frontend (React) → REST API (FastAPI) → Rule Engine Pipeline → DataSource
```

## Rule Engine Pipeline

Sequential pipeline in `rule_engine/pipeline.py`. Each module reads from `EvaluationContext`, writes `ModuleResult` back. Order matters — later modules depend on earlier ones.

### Execution Order & Dependencies

```
1. site_normalizer  → sets ctx.site_identity
2. zoning           → sets ctx.zoning_data (needs DataSource)
3. odd_lot          → reads zoning
4. building_line    → sets ctx.road_info (needs DataSource)
5. far_bcr          → reads zoning, computes max areas
6. far_bonus        → reads zoning + far_bcr
7. far_transfer     → reads zoning + far_bcr
8. building_mass    → reads zoning + far_bcr (height/sunlight)
9. fire_safety      → reads zoning + far_bcr
10. parking         → reads far_bcr (3-tier fallback)
11. traffic         → reads parking + road_info
12. overlays        → reads far_bcr (needs DataSource)
13. urban_renewal   → reads input scheme
14. building_permit → aggregates all prior modules
15. conclusion      → final status (strictest-of-critical)
```

### Key Design Patterns

**Rule Module Pattern**: `RuleModule` ABC with `evaluate(ctx) → ModuleResult`
- Self-contained modules, no inter-module direct calls
- Each module produces `ModuleResult` with status, result dict, legal_basis, notes

**Context Object**: `EvaluationContext`
- Accumulates: `raw_input`, `site_identity`, `zoning_data`, `road_info`, `overlays`
- `module_results: dict[str, ModuleResult]` — keyed by module name
- Methods: `set_result()`, `get_result()`

**Data Source Strategy**: `DataSource` ABC
- Pluggable implementations (mock → real API)
- 4 methods: `get_site_info`, `get_zoning`, `get_overlays`, `get_road_info`

**3-Tier Fallback** (parking): urban plan → 土管§86-1 tiered → 建技規則§59

## Conclusion Logic

Modules split into:
- **Critical** (zoning, building_line, odd_lot, far_bcr, parking, overlays, building_mass, fire_safety, traffic, building_permit) — FAIL = veto
- **Optional** (far_bonus, far_transfer, urban_renewal) — FAIL = "not applicable"

Priority: `AUTO_FAIL > REVIEW_REQUIRED > HIGH_RISK > AUTO_PASS`

Output categorized into: `blockers` / `high_risk_items` / `manual_review_items`

## Data Flow

```
SiteInput (user)
  ↓
Pipeline: auto-query area if missing → run 15 modules → build checklist_19
  ↓
EvaluationReport
  ├── per-module results (status + notes + legal_basis)
  ├── checklist_19 (19-point summary)
  ├── overlay_risks
  ├── blockers / high_risk_items / manual_review_items
  ├── final_status + final_status_text
  ├── legal_basis (deduplicated)
  └── data_mode ("mock" | "live")
```

## API Layer

- `POST /api/v1/evaluate` — main endpoint
- `GET /health` — health check
- CORS: localhost:5173, localhost:3000

## Frontend

- **EvaluatePage** (`/`) — input form → calls API → navigates to result
- **ResultPage** (`/result`) — displays: ReportSummary → Checklist19 → OverlayRiskList → ChecklistDetailCards → EvidenceTable
- React Query mutation for API call
- Location state passes report between pages
