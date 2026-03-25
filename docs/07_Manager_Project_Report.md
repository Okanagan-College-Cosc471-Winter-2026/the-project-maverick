# Project Report by the Manager / Scrum Master

**Organization:** Okanagan College
**Course:** COSC 471 - Software Engineering (Winter 2026)
**Project:** the-project-maverick
**Year:** 2026
**Scrum Masters / Managers:** Parag Jindal and Harsh Kumar

---

## 1. Executive Summary

This document captures the outcomes, structural metrics, and addressed risks across the sprint iterations of the "the-project-maverick" Stock Market Prediction System. The project has progressed through five sprints, delivering a fully functional ML-powered stock prediction platform with a React frontend, FastAPI backend, and XGBoost inference engine.

## 2. Project Issues and Risk Management

The team used GitHub Issues and a project board for transparent lifecycle tracking. Issues were assigned due dates and responsible persons for accountability.

### Resolved Issues

| Issue | Description | Resolution | Assigned To |
|-------|------------|------------|-------------|
| ISSUE-11 | Pandas DataFrame transformation delayed API responses to 800ms | Migrated pipeline to optimized raw SQL queries, dropping latency below 100ms | Harsh Kumar |
| ISSUE-14 | ORM properties diverged from actual database columns | Re-initialized Alembic and generated locked revisions using `uv` | Zane Tessmer |
| ISSUE-18 | Frontend chart re-rendered continuously causing browser memory leaks | Implemented debouncing and dependent query keys in TanStack Query | Kaval S |
| ISSUE-22 | Market data queries used stale schema references after migration | Migrated all queries to use new `market` schema with parameterized SQL | Dante Bertolutti |
| ISSUE-25 | Docker build size for ML backend container approached 2.5GB | Optimized Dockerfile layers and removed unnecessary dependencies | Zane Tessmer |
| ISSUE-28 | SQL injection risk in data snapshot date filtering | Replaced string interpolation with SQLAlchemy parameterized queries | Dante Bertolutti |

### Active/Monitoring Items

| Issue | Description | Status | Due | Assigned To |
|-------|------------|--------|-----|-------------|
| ISSUE-30 | Streamlit alternative frontend needs polish | In Progress | Sprint 5 | Guntash Brar |
| ISSUE-31 | Training endpoint response models need standardization | Low Priority | Future | Parag Jindal |

## 3. Iteration Assessment and Lessons Learned

### Evaluation Criteria Met

- Minimum viable API connected to live FMP data endpoints
- React interactive dashboard plotting historical data with ML predictions
- Code coverage thresholds reached 81%
- Next-day 26-bar path prediction model deployed and serving via REST API
- Data snapshot export functionality operational
- CI/CD pipeline running automated tests on every PR

### Process Lessons

**Environment Standardization (Sprint 1):** During the initial week, setting up virtual environments using standard Python `pip` caused desynchronization across team members on different operating systems. The team paused feature development for 2 days to migrate to `uv` and Docker Compose. This initial setback yielded significant consistency improvements for all subsequent sprints.

**Schema Migration Complexity (Sprint 4):** The migration from the original database schema to the new `market` schema required coordinated changes across backend CRUD operations, inference service, and frontend API client. The team learned to plan schema changes as cross-cutting concerns requiring sprint-level coordination rather than isolated tasks.

**Model Artifact Management (Sprint 4-5):** Managing 26 separate XGBoost model files for the multi-horizon prediction required a structured approach. Introducing `meta.json` and `model_manifest.json` files alongside the model artifacts proved essential for reproducibility.

## 4. Finished Tasks and Accomplished Project Work

### Backend API Component

All core entities (MarketData, Stock, Prediction) have been modeled and serialized. The inference service handles next-day 15-minute path predictions across 26 horizons. Market data endpoints serve daily prices, OHLCV data, and stock coverage information. The data module supports snapshot building and downloading in Parquet and CSV formats.

### Frontend Dashboard

TanStack Query reliably caches REST API responses. Recharts and Lightweight Charts render historical prices with predicted paths. The sidebar provides stock symbol navigation. A training monitor dashboard allows administrators to track model training jobs.

### ML Pipeline

The legacy static model was replaced with a multi-horizon XGBoost ensemble. Training scripts support both local execution and DRAC cluster deployment. Airflow DAGs automate daily data snapshots and training triggers. Feature engineering covers RSI, MACD, Bollinger Bands, ATR, OBV, and additional derived indicators.

## 5. Workload Information (Team Member Hours)

| Name | Role Summary | Sprint 3 | Sprint 4 | Sprint 5 | Total |
|------|-------------|----------|----------|----------|-------|
| Dante Bertolutti | Project Lead, Full-Stack Integration | 32 hrs | 36 hrs | 30 hrs | 98 hrs |
| Harsh Kumar | Backend Core, ML Integration | 38 hrs | 40 hrs | 35 hrs | 113 hrs |
| Parag Jindal | API Endpoints, Sprint Planning | 30 hrs | 28 hrs | 25 hrs | 83 hrs |
| Kaval S | React Architecture, State Management | 35 hrs | 30 hrs | 28 hrs | 93 hrs |
| Guntash Brar | Frontend Visualization, Streamlit | 28 hrs | 32 hrs | 30 hrs | 90 hrs |
| Zane Tessmer (Foochini) | DevOps, QA, Documentation | 34 hrs | 35 hrs | 32 hrs | 101 hrs |

**Total Team Effort:** 578 hours across Sprints 3-5.
