# Change Requests

**Organization:** Okanagan College
**Course:** COSC 471 - Software Engineering (Winter 2026)
**Project:** the-project-maverick

---

## CR-001: Migration to Asynchronous SQLAlchemy Engine

**CR ID:** CR-001
**Requestor:** Harsh Kumar
**Date:** 2026-01-27

**Proposed Change Description:**
Transition the entire database interaction layer from synchronous `psycopg2` driver logic to `asyncpg` combined with SQLAlchemy 2.0 async sessions.

**Reason for Change:**
The original system used blocking network calls during API requests. Stock market dashboards are highly concurrent, and synchronous API calls caused thread bottlenecks during simultaneous dashboard reloads, producing latency spikes above 800ms. Asynchronous connections allow the Python event loop to service thousands of concurrent requests efficiently.

**Impact Analysis:**

- Affected Components: `database.py`, all files in `/api/`, `requirements.txt`
- Time/Schedule Impact: Requires approximately 8 hours of refactoring. Pauses Milestone 2 API completion by 1 day.
- Risk Assessment: High risk. Changing ORM session logic requires refactoring all `db.query` statements into `select()` statements.

**Approval Status:** APPROVED
**Scrum Master Signature:** Parag Jindal

---

## CR-002: Switching Frontend Bundler to Vite

**CR ID:** CR-002
**Requestor:** Kaval S
**Date:** 2026-02-03

**Proposed Change Description:**
Replace `create-react-app` (CRA) and Webpack with Vite using the ESBuild ecosystem.

**Reason for Change:**
CRA inflated build times with dev server hot reload taking over 15 seconds. Vite serves modules near-instantaneously, providing the frontend developers a substantially faster iterative workflow.

**Impact Analysis:**

- Affected Components: `frontend/package.json`, root HTML structure, environment variable syntax (`REACT_APP_` to `VITE_`)
- Time/Schedule Impact: Minimal. Approximately 2 hours for migration.
- Risk Assessment: Low risk, isolated to frontend.

**Approval Status:** APPROVED
**Scrum Master Signature:** Harsh Kumar

---

## CR-003: Removal of TimescaleDB Requirement for MVP

**CR ID:** CR-003
**Requestor:** Zane Tessmer
**Date:** 2026-02-17

**Proposed Change Description:**
Drop TimescaleDB containerization and rely solely on vanilla PostgreSQL 16 for storing time-series market data during the academic presentation cycle.

**Reason for Change:**
TimescaleDB mandated specific image sizes, chunk partitioning, and hyper-table routing which increased Docker complexity and broke initial database seed scripts on Windows machines. Since the application does not need to ingest 100k+ rows simultaneously for the MVP, standard relational SQL is computationally adequate.

**Impact Analysis:**

- Affected Components: `docker-compose.yml`, `seed_data.py`
- Time/Schedule Impact: Recovers lost scheduling time by removing unnecessary enterprise deployment architecture.
- Risk Assessment: Negligible for MVP, though removes long-term hyper-scale capabilities.

**Approval Status:** APPROVED
**Scrum Master Signature:** Parag Jindal

---

## CR-004: Migration to Multi-Horizon XGBoost Model

**CR ID:** CR-004
**Requestor:** Harsh Kumar
**Date:** 2026-03-10

**Proposed Change Description:**
Replace the single-output XGBoost regressor with a multi-horizon ensemble of 26 XGBoost models, each predicting a 15-minute bar of the next trading day.

**Reason for Change:**
The original single-prediction model only provided a next-day close price. Stakeholder feedback indicated that intraday path predictions would be significantly more valuable for day traders. The new model provides 26 predicted price points covering the full trading day at 15-minute intervals.

**Impact Analysis:**

- Affected Components: `model_loader.py`, `service.py`, `features.py`, `schemas.py`, `api.py`, model artifacts directory
- Time/Schedule Impact: Adds approximately 20 hours across Sprint 4-5 for training, validation, and backend integration.
- Risk Assessment: Medium risk. Changes the API response schema, requiring frontend updates to handle the new prediction format.

**Approval Status:** APPROVED
**Scrum Master Signature:** Parag Jindal

---

## CR-005: Parameterize Data Snapshot SQL Queries

**CR ID:** CR-005
**Requestor:** Dante Bertolutti
**Date:** 2026-03-25

**Proposed Change Description:**
Replace string-interpolated date values in the data snapshot build endpoint with SQLAlchemy parameterized query bindings.

**Reason for Change:**
The `build-snapshot` endpoint was interpolating user-supplied `start_date` and `end_date` strings directly into raw SQL via f-strings, creating a potential SQL injection vector. While ticker names were validated against a whitelist, the date parameters bypassed any sanitization.

**Impact Analysis:**

- Affected Components: `backend/app/modules/data/api.py`
- Time/Schedule Impact: Less than 1 hour.
- Risk Assessment: No functional change to query results. Only the method of passing date values to the database changes.

**Approval Status:** APPROVED
**Scrum Master Signature:** Parag Jindal
