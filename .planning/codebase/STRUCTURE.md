# Directory Structure

```
taipei-land-dev-engine/
├── CLAUDE.md                          # Project guidance for Claude Code
├── README_land_dev_taipei_v1_v2.md    # Product spec (V1/V2 scope)
├── .gitignore
│
├── backend/
│   ├── pyproject.toml                 # Python package config
│   ├── app/
│   │   ├── main.py                    # FastAPI app + CORS
│   │   ├── config.py                  # Pydantic Settings (LAND_DEV_* env)
│   │   ├── database.py               # SQLAlchemy async engine (stub)
│   │   │
│   │   ├── api/
│   │   │   ├── router.py             # API router aggregator
│   │   │   └── endpoints/
│   │   │       ├── evaluate.py        # POST /evaluate
│   │   │       └── projects.py        # Project history (stub)
│   │   │
│   │   ├── rule_engine/               # Core: 19-point evaluation
│   │   │   ├── base.py                # RuleModule ABC, EvaluationContext
│   │   │   ├── pipeline.py            # Orchestration + checklist builder
│   │   │   ├── site_normalizer.py     # Address normalization
│   │   │   ├── zoning.py              # Zone & use legality
│   │   │   ├── odd_lot.py             # Odd lot detection
│   │   │   ├── building_line.py       # Road frontage / building line
│   │   │   ├── far_bcr.py             # FAR / BCR calculation
│   │   │   ├── far_bonus.py           # FAR bonuses
│   │   │   ├── far_transfer.py        # FAR transfer
│   │   │   ├── building_mass.py       # Height / sunlight / setback
│   │   │   ├── fire_safety.py         # Fire safety distance
│   │   │   ├── parking.py             # Parking (3-tier fallback)
│   │   │   ├── traffic.py             # Traffic circulation
│   │   │   ├── overlays.py            # GIS overlays (urban design, hillside, etc.)
│   │   │   ├── urban_renewal.py       # Urban renewal / 危老
│   │   │   ├── building_permit.py     # Building permit prereqs
│   │   │   └── conclusion.py          # Final verdict aggregation
│   │   │
│   │   ├── data_sources/
│   │   │   ├── base.py                # DataSource ABC
│   │   │   └── mock_zone.py           # Mock implementation (~10 addresses)
│   │   │
│   │   ├── schemas/
│   │   │   ├── enums.py               # FinalStatus, IntendedUse, SourceType
│   │   │   ├── input.py               # SiteInput
│   │   │   ├── output.py              # ModuleResult, EvaluationReport, ChecklistItem
│   │   │   └── evidence.py            # LegalBasis
│   │   │
│   │   ├── versioning/
│   │   │   └── law_registry.py        # Centralized legal parameters
│   │   │
│   │   └── models/                    # ORM models (stub)
│   │
│   └── tests/
│       ├── conftest.py                # TestClient fixture
│       ├── test_api.py                # API endpoint tests (3)
│       ├── test_pipeline.py           # E2E pipeline tests (12)
│       └── test_parking.py            # Parking module tests (2)
│
└── frontend/
    ├── package.json
    ├── vite.config.ts                 # Proxy /api → localhost:9000
    ├── tsconfig.json
    ├── index.html
    └── src/
        ├── main.tsx                   # React entry
        ├── App.tsx                    # Router + theme (zh_TW)
        ├── api/client.ts              # Axios client + evaluateSite()
        ├── hooks/useEvaluate.ts       # React Query mutation
        ├── types/index.ts             # TS types (mirrors backend schemas)
        ├── pages/
        │   ├── EvaluatePage.tsx        # Input form page (/)
        │   └── ResultPage.tsx          # Report display (/result)
        └── components/
            ├── SiteInputForm.tsx       # Input form
            ├── ReportSummary.tsx       # Status + blockers/risks
            ├── Checklist19.tsx         # 19-point overview
            ├── ChecklistDetailCards.tsx # Expandable per-point details
            ├── OverlayRiskList.tsx      # GIS risk alerts
            ├── EvidenceTable.tsx        # Legal basis table
            ├── ResultCard.tsx           # Module result card
            └── StatusBadge.tsx          # Color-coded status badge
```

## Naming Conventions

| Scope | Convention | Example |
|-------|-----------|---------|
| Python modules | snake_case | `building_line.py` |
| Python classes | PascalCase | `BuildingLineModule` |
| Python constants | UPPER_SNAKE | `STATUS_PRIORITY` |
| TS components | PascalCase files | `SiteInputForm.tsx` |
| TS utilities | camelCase files | `useEvaluate.ts` |
| TS types | PascalCase | `EvaluationReport` |
