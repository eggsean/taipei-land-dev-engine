# Coding Conventions

## Language Usage

- **Code identifiers**: English (function/class/variable names)
- **User-facing text**: Chinese (notes, status_text, descriptions)
- **Docstrings**: Chinese for module-level, mixed for inline comments
- **Legal references**: Chinese (law names, articles)

```python
# Module docstring: Chinese
"""Step 2: 都市計畫/分區判定 + 用途合法性檢查。"""

# User-facing notes: Chinese
notes.append(f"分區 {zone_name}，允許 {use_label} 使用")

# Variable names: English
total_floor_area = area * base_far / 100
```

## Python Patterns

### Imports
Three groups, alphabetical within each:
1. Standard library
2. Third-party (fastapi, pydantic, sqlalchemy)
3. Local (`app.*` absolute paths, no relative imports)

### Type Annotations
- All function signatures typed with return type
- `float | None` (Python 3.10+ union syntax)
- `dict[str, Any]` for flexible dicts
- Pydantic `Field(...)` for required, `Field(None)` for optional

### Rule Module Pattern
```python
class XxxModule(RuleModule):
    module_name = "xxx"

    def evaluate(self, ctx: EvaluationContext) -> ModuleResult:
        # 1. Read from context
        area = ctx.raw_input.get("site_area_sqm") or 0
        # 2. Compute
        # 3. Build ModuleResult with status, result, notes, legal_basis
        # 4. ctx.set_result(self.module_name, r)
        return r
```

### Error Handling
- **Status-based, not exception-based**: Return `ModuleResult` with appropriate `FinalStatus`
- Missing data → `REVIEW_REQUIRED` (not crash, not silent default)
- `area = ctx.raw_input.get("site_area_sqm") or 0` pattern for None-safe access

### Legal Basis (every module must include)
```python
LegalBasis(
    law_name="法規名稱",
    article="第X條",
    source_url="https://...",
    source_type=SourceType.LOCAL_LAW,
)
```

## Frontend Patterns

### Component Structure
- Pages in `pages/`, components in `components/`
- One component per file, PascalCase naming
- Props typed inline or via interface

### State Management
- React Query `useMutation` for API calls
- `location.state` for page-to-page data passing
- No global state store

### Status Color Coding
- AUTO_PASS → green (#52c41a)
- AUTO_FAIL → red (#ff4d4f)  
- REVIEW_REQUIRED → orange (#faad14)
- HIGH_RISK → purple (#722ed1)
