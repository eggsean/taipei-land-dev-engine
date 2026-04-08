# Concerns & Technical Debt

## HIGH Severity

### H1: Mock-Only Data Source
All zoning, site info, roads, and overlays are hardcoded for ~10 addresses. Unknown addresses get REVIEW_REQUIRED (fixed), but system cannot evaluate real properties.
**Impact**: Not usable for real assessments.
**Fix**: Implement real DataSource against Taipei WebGIS APIs.

### H2: No Authentication
`/evaluate` endpoint completely open. No API keys, rate limiting, or audit trail.
**Impact**: Anyone can call the API; no accountability.
**Fix**: Add API key or JWT auth before any deployment.

### H3: Legal Parameter Accuracy
FAR/BCR values, parking tiers, height limits claim to match Taipei ordinances but are manually transcribed. No automated verification against official law text.
**Impact**: Incorrect parameters → incorrect legal conclusions.
**Fix**: Establish ground-truth test suite; cross-reference official gazette.

### H4: Building Mass Heuristics
Uses `math.sqrt(area)` to estimate lot dimensions (assumes square). Height estimation uses fixed 3.3m floor height. Sunlight check is threshold-only (no actual solar angle calculation).
**Impact**: Unrealistic estimates for non-square lots.
**Fix**: Accept actual lot dimensions or use cadastral geometry.

## MEDIUM Severity

### M1: Fuzzy Address Matching
Uses substring matching after 台/臺 normalization. Can return wrong zone for ambiguous inputs (e.g., partial address matches multiple entries).
**Fix**: Require exact match or use structured lot number lookup.

### M2: In-Memory Project History
`projects.py` stores history in `_history: dict = {}`. Lost on restart. SQLAlchemy configured but not used for this.
**Fix**: Implement ORM models and persist to SQLite.

### M3: Overlay Detection Oversimplified
Checks district name keywords only ("北投" → hillside). No actual GIS layer intersection.
**Fix**: Integrate real GIS overlay API.

### M4: CORS Configuration
Allows credentials=True with specific origins. Needs production hardening.
**Fix**: Configure per-environment CORS settings.

### M5: No Caching
Every evaluation queries data source fresh. No performance optimization.
**Fix**: Add caching layer for repeated lookups.

### M6: Logging May Expose PII
Logs raw addresses via `logger.info("Received input: %s", ...)`.
**Fix**: Redact or hash addresses in logs.

### M7: Exception Handling
Pipeline errors bubble up as 500 without structured error response. No partial results if a module fails mid-pipeline.
**Fix**: Wrap each module in try/catch, return partial results with failed modules marked.

## LOW Severity

### L1: Unused Schema Fields
`SiteInput` has fields (`single_owner`, `can_merge_adjacent`, `has_permit`) that few modules use. May confuse users.

### L2: No CI/CD
No GitHub Actions, no automated test runs on push.

### L3: Frontend State via location.state
Report passed between pages via React Router location state. Refreshing `/result` loses data.
**Fix**: Store report in URL param or fetch by project_id.

### L4: No OpenAPI Customization
FastAPI auto-generates docs but no custom descriptions, examples, or tags.

### L5: Database Models Empty
`models/__init__.py` exists but no ORM models defined. Database layer is a stub.

## Architecture Limitations

- **Sequential Pipeline**: Cannot parallelize independent modules
- **No Conditional Skip**: All modules always run even if upstream fails
- **Tight Coupling to Mock**: `pipeline.py` defaults to `MockZoneDataSource()` if none provided
- **No Versioned Rules**: Can't compare results across different regulation versions
