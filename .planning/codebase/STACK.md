# Technology Stack

## Languages & Runtime

| Component | Language | Version |
|-----------|----------|---------|
| Backend | Python | >=3.11 |
| Frontend | TypeScript | 5.6.0 |

## Backend Dependencies

### Core
- **fastapi** ^0.115.0 — async web framework
- **uvicorn[standard]** ^0.32.0 — ASGI server
- **pydantic** ^2.10.0 — data validation
- **pydantic-settings** ^2.6.0 — environment-based config

### Database
- **sqlalchemy** ^2.0.0 — ORM (async)
- **aiosqlite** ^0.20.0 — async SQLite driver

### Dev/Test
- **pytest** ^8.0.0
- **pytest-asyncio** ^0.24.0
- **httpx** ^0.27.0 — API test client

## Frontend Dependencies

### Core
- **react** ^18.3.0 + **react-dom**
- **react-router-dom** ^6.28.0
- **@tanstack/react-query** ^5.62.0
- **axios** ^1.7.0

### UI
- **antd** ^5.22.0 (Ant Design, zh_TW locale)
- **@ant-design/icons** ^5.6.0

### Build
- **vite** ^6.0.0
- **@vitejs/plugin-react** ^4.3.0
- **typescript** ^5.6.0

## Configuration

| Setting | Default | Env Var |
|---------|---------|---------|
| Database URL | `sqlite+aiosqlite:///./land_dev.db` | `LAND_DEV_DATABASE_URL` |
| Rule Version | `2025.04.01` | `LAND_DEV_RULE_VERSION` |
| API Prefix | `/api/v1` | — |
| Backend Port | 9000 | — |
| Frontend Port | 5173 (dev) | — |

## Build & Run

```bash
# Backend
cd backend && pip install -e ".[dev]"
uvicorn app.main:app --reload --host 127.0.0.1 --port 9000

# Frontend
cd frontend && npm install && npm run dev

# Tests
cd backend && python -m pytest tests/ -v
cd frontend && npx tsc --noEmit
```
