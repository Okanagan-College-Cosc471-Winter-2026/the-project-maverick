# Internal Testing Guide — the-project-maverick

**Course:** COSC 471  
**Audience:** Students and instructors during the **internal presentation**  
**Purpose:** Step through consistent tests while others try to **break** the app. Update the **Known bugs** section as you find issues.

---

## 1. What you are testing

A **Stock Market Prediction** web application with:

- **Backend:** FastAPI (`backend/`), PostgreSQL, ML inference under `/api/v1/inference/...` and related modules  
- **Frontend:** React + Vite (`frontend/`), dashboard routes under `/dashboard/...`  
- **Orchestration:** `docker-compose.yml` (database, prestart/migrations, backend, frontend)

---

## 2. Environment setup (before class)

**Prerequisites**

- Docker Desktop **or** local Postgres + Python `uv` + Node/Bun for frontend  
- Copy `.env` from `.env.example` and set passwords / URLs as in `README.md` or `Documentation/Installation_Guide.md`

**Recommended: Docker**

1. From repo root: start services with docker compose (see `README.md`).  
2. Wait until **db** is healthy and **prestart** completes.  
3. Confirm backend responds at `http://localhost:8000` and frontend at the port mapped in compose (often **5173** or as documented).

**Sanity URLs**

- API docs: `http://localhost:8000/docs`  
- Health: use OpenAPI to find the health / utils routes your build exposes (paths may vary by version; search “health” in Swagger).

---

## 3. Test matrix (execute in order)

### 3.1 Smoke tests (5 min)

| Step | Action | Expected |
|------|--------|----------|
| S1 | Open Swagger `/docs` | UI loads, endpoints listed |
| S2 | Call health-related endpoint (if present) | 2xx, no stack trace in response body |
| S3 | Open frontend home/dashboard | No blank screen; no infinite spinner |

**Fail if:** 5xx errors, missing OpenAPI, or frontend build errors in console.

---

### 3.2 API — inference (10 min)

| ID | Request | Expected |
|----|---------|----------|
| API-1 | `GET /api/v1/inference/predict/THIS_SYMBOL_DOES_NOT_EXIST` | **404**, detail mentions not found |
| API-2 | `GET /api/v1/inference/predict/AAPL` (or another **seeded** symbol) | **200** with structured prediction payload **or** documented 400 if data/model pipeline incomplete |
| API-3 | Repeat API-2 rapidly (~20 requests in 10 s) | No crash; stable latency; DB connection errors should not appear |

**Notes from codebase**

- `test_inference.py` expects **404** for `FAKE_SYMBOL`.  
- `InferenceService` may **400** if insufficient bars/features for the active model bundle.

---

### 3.3 API — market / data (10 min)

Use Swagger to exercise market/list and OHLC/chart endpoints **as exposed in your build**.

| ID | Action | Expected |
|----|--------|----------|
| M1 | List stocks | Non-empty list if DB seeded |
| M2 | Request OHLC for a symbol with **no** prices | Empty array or documented empty state |
| M3 | Request OHLC for a symbol **with** prices | Points return; timestamps numeric (see `test_market_service.py`) |

---

### 3.4 UI / UAT (15 min)

| ID | User flow | Expected |
|----|-----------|----------|
| UI-1 | Login / auth (if enabled in your deployment) | Only authorized users reach admin routes |
| UI-2 | Navigate **Stocks** → pick a symbol | Detail page loads without console errors |
| UI-3 | Resize browser window on chart page | Chart resizes (Lightweight Charts resize handler) |
| UI-4 | Rapid navigation: stocks ↔ predictions ↔ settings | No memory blow-up; no stuck loading state |

---

### 3.5 “Try to break it” ideas (peers)

- **Invalid input:** empty symbol, SQL-like strings in query params, extremely long symbol strings  
- **Concurrency:** two browsers on same symbol; refresh during load  
- **Network:** throttle to “Slow 3G” in DevTools; cancel requests  
- **DB:** stop Postgres container mid-request; observe error handling (expect 5xx — document behavior)  
- **Security:** confirm no secrets in API responses or frontend bundle  

---

## 4. Recording results

Use a copy of this table during the session:

| Tester | Date | Test ID | Pass/Fail | Notes / screenshot |
|--------|------|---------|-----------|----------------------|
| | | | | |

---

## 5. Known bugs and limitations (maintain this list)

*Team: edit before and after internal demo.*

| ID | Symptom | Steps to reproduce | Severity | Owner |
|----|---------|--------------------|----------|-------|
| KB-1 | WebSocket / live stream incomplete | *Manager report ISSUE-22* | Medium | Parag Jindal |
| KB-2 | Large Docker image / slow pull | Build backend image | Low | Foochini |
| KB-3 | Prediction path may 400 if feature pipeline incomplete for bundle | Predict with valid symbol but missing feature columns | Medium | Backend |
| KB-4 | `test_predict_stock_price_success_mock` is a placeholder `pass` | Run pytest — success path under-tested | Low | QA |

**Non-bugs to mention verbally**

- Predictions are **not** financial advice.  
- Model quality depends on **data** and **market regime**.  

---

## 6. Automated regression (for presenters)

From `backend/` (with DB env vars set as in CI):

```bash
uv sync
uv run alembic upgrade head
uv run pytest tests/ -v
```

Frontend (from `frontend/`):

```bash
bun install
bunx biome check .
bun run build
```

---

## 7. After the internal session

1. Attach completed **Recording results** table to your **Individual** or **Manager** report.  
2. File GitHub Issues for any new KB rows.  
3. Update `Documentation/Testing_Plan.md` if acceptance criteria change.  
