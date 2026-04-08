# Testing

## Setup

- **Framework**: pytest 8.0+ with pytest-asyncio
- **HTTP Testing**: httpx via FastAPI TestClient
- **Config**: `backend/pyproject.toml` (`[tool.pytest.ini_options]`)

```bash
cd backend
pytest                                    # all tests
pytest -v                                 # verbose
pytest tests/test_pipeline.py             # single file
pytest -k test_residential                # filter by name
```

## Test Files (19 tests total)

| File | Tests | Type |
|------|-------|------|
| `test_pipeline.py` | 12 | End-to-end pipeline |
| `test_api.py` | 3 | API integration |
| `test_parking.py` | 2 | Module unit |
| `conftest.py` | — | Fixtures (TestClient) |

## Test Patterns

### E2E Pipeline Tests
```python
def test_residential_in_residential_zone():
    """住三區做住宅 → 分區通過"""
    site = SiteInput(address_or_lot="...", site_area_sqm=500, intended_use=IntendedUse.RESIDENTIAL)
    report = run_pipeline(site)
    assert report.zoning_result.status == FinalStatus.AUTO_PASS
```

### Module Tests (with helper)
```python
def _make_ctx(address, area, use) -> EvaluationContext:
    ctx = EvaluationContext({...})
    SiteNormalizer().evaluate(ctx)
    ZoningModule(ds).evaluate(ctx)
    FarBcrModule().evaluate(ctx)
    return ctx
```

### API Tests
```python
def test_evaluate_endpoint(client):
    resp = client.post("/api/v1/evaluate", json={...})
    assert resp.status_code == 200
```

## Coverage

### Well-Covered
- Zoning pass/fail scenarios
- Parking 3-tier fallback
- Unknown address handling (REVIEW_REQUIRED)
- Area provenance (auto/manual/missing)
- Blocker vs review_items separation
- Checklist 19-point completeness
- API validation (422 on bad input)

### Gaps (implicit coverage only)
- Building line (6 scenarios)
- Building mass (height/sunlight)
- Fire safety
- Traffic
- FAR bonus/transfer edge cases
- Individual overlay types
