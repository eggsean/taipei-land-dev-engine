# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

臺北市土地開發法定結論系統 — a rule engine that evaluates Taipei land parcels against 19 regulatory checkpoints and produces a legal preliminary assessment report. Users input an address/lot number and intended use; the system auto-queries site data, runs all rules, and outputs pass/fail/risk status per checkpoint.

## Commands

```bash
# Backend (from backend/)
pip install -e ".[dev]"
uvicorn app.main:app --reload --host 127.0.0.1 --port 9000
python -m pytest tests/ -v

# Frontend (from frontend/)
npm install
npm run dev          # dev server on :5173, proxies /api to :9000
npx tsc --noEmit     # type check
```

## Architecture

### Rule Engine Pipeline (`app/rule_engine/pipeline.py`)

The core is a sequential pipeline that runs 19 rule modules against an `EvaluationContext`. Each module reads from context, writes its `ModuleResult` back, and the next module can reference prior results.

Execution order matters — later modules depend on earlier ones:
1. `site_normalizer` → sets `ctx.site_identity`, auto-queries area from `DataSource`
2. `zoning` → sets `ctx.zoning_data` (FAR, BCR, allowed uses)
3. `odd_lot` → reads zoning for zone-specific thresholds
4. `building_line` → sets `ctx.road_info`
5. `far_bcr` → reads zoning, computes max floor/building area
6-7. `far_bonus`, `far_transfer` → read zoning + far_bcr results
8. `building_mass` → reads zoning + far_bcr for height/sunlight checks
9. `fire_safety` → reads zoning + far_bcr
10. `parking` → reads far_bcr for total floor area, uses 3-tier fallback
11. `traffic` → reads parking result + road_info
12. `overlays` → reads far_bcr for floor area (urban design review threshold)
13. `urban_renewal` → reads input scheme
14. `building_permit` → aggregates all prior modules
15. `conclusion` → final status using strictest-of-critical-modules principle

### Conclusion Logic

Modules are split into **critical** (zoning, building_line, parking, etc. — FAIL = veto) and **optional** (far_bonus, far_transfer, urban_renewal — FAIL = "not applicable", doesn't block development). Priority: AUTO_FAIL > REVIEW_REQUIRED > HIGH_RISK > AUTO_PASS.

### Data Source Abstraction (`app/data_sources/base.py`)

`DataSource` ABC with methods: `get_site_info`, `get_zoning`, `get_overlays`, `get_road_info`. Currently only `MockZoneDataSource` exists. To connect real APIs, implement the same interface. The mock uses `_fuzzy_lookup` to handle 台/臺 normalization.

### Law Parameters (`app/versioning/law_registry.py`)

All regulatory numbers (FAR/BCR per zone, parking tiers, thresholds) are centralized here — **never hardcode legal values in rule modules**. Key structures:
- `PARKING_PARAMS_86_1` — tiered parking calculation per 土管第86-1條
- `PARKING_PARAMS_BUILDING_CODE` — fallback per 建技規則第59條
- `URBAN_DESIGN_REVIEW_THRESHOLDS` — multi-criteria per 都審規則第3條
- `ODD_LOT_STANDARDS`, `FIRE_SEPARATION_RULES`, `SUNLIGHT_RULES`

### Parking 3-Tier Fallback

`parking.py` checks in order: (1) urban plan specific rules → (2) 土管第86-1條 tiered formula → (3) 建技規則第59條. First match wins. The tiered formula uses `_calc_tiered()` which processes area brackets with different rates.

### Frontend

React + TypeScript + Ant Design. Two pages: `EvaluatePage` (input form) → `ResultPage` (report). The result page shows: `ReportSummary` → `Checklist19` table (19-point overview) → `ChecklistDetailCards` → `EvidenceTable`. Vite proxies `/api` to backend.

## Key Constraints

- All rule outputs must include `legal_basis` with law name, article, source URL, and source type — this is the evidence chain requirement from the product spec.
- Status `REVIEW_REQUIRED` means the system cannot make a definitive determination; it must never be used for items that can be programmatically resolved.
- 用中文撰寫面向使用者的文字（notes、status_text等）。
