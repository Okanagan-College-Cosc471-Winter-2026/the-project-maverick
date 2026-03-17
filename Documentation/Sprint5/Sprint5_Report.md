---
pdf_options:
  format: Letter
  margin: 20mm
  headerTemplate: '<div style="font-size:8px;width:100%;text-align:center;color:#888;">MarketSight - Sprint 5 Development Report</div>'
  footerTemplate: '<div style="font-size:8px;width:100%;text-align:center;color:#888;"><span class="pageNumber"></span> / <span class="totalPages"></span></div>'
  displayHeaderFooter: true
stylesheet: https://cdnjs.cloudflare.com/ajax/libs/github-markdown-css/5.5.1/github-markdown.min.css
body_class: markdown-body
css: |-
  body { font-size: 11px; }
  h1 { color: #2980b9; border-bottom: 2px solid #2980b9; padding-bottom: 4px; }
  h2 { color: #2980b9; border-bottom: 1px solid #2980b9; padding-bottom: 3px; margin-top: 16px; }
  h3 { color: #34495e; margin-top: 10px; }
  h4 { color: #34495e; margin-top: 8px; }
  table { font-size: 10px; width: 100%; border-collapse: collapse; }
  th { background-color: #2980b9; color: white; padding: 4px 6px; }
  td { padding: 3px 6px; }
  tr:nth-child(even) { background-color: #f0f7fc; }
  .cover { text-align: center; margin-top: 80px; }
  .cover h1 { font-size: 32px; border: none; }
  .cover h2 { font-size: 18px; border: none; color: #34495e; }
  .cover .line { border-top: 3px solid #2980b9; width: 120px; margin: 20px auto; }
  .cover p { color: #888; font-size: 13px; }
---

<div class="cover">

# MarketSight

## Stock Market Prediction System

<div class="line"></div>

## Sprint 5 - Development Report
## Construction Phase 3

**Team Members:**
Zane Tessmer (Scrum Master)
Harsh Kumar (Product Owner / Lead Developer)
Dante Bertolutti (Developer)
Parag Jindal (Developer)
Kaval S (Developer)
Guntash (Developer)

Date: **March 17, 2026**
Course: COSC 471 - Winter 2026
Okanagan College

</div>

<div style="page-break-after: always;"></div>

## Table of Contents

1. Sprint 5 Overview
2. Development Summary by Team Member
3. Git History & Commit Log
4. Pull Requests & Code Reviews
5. Technical Highlights
6. Architecture Changes
7. Testing Summary
8. XP Pair Report
9. Milestone Status

<div style="page-break-after: always;"></div>

# 1. Sprint 5 Overview

**Sprint Duration:** March 4 - March 17, 2026
**Sprint Goal:** Achieve Initial Operational Capability (IOC) for the final Construction phase release
**Velocity:** 62 story points
**Stories Completed:** 14 / 14

### Key Achievements
- Restored confidence scoring and predictions page lost during Sprint 4 merge
- Deployed to DRI production server with SSL and management scripts
- Migrated model format to native XGBoost .ubj with meta.json metadata
- Added Streamlit frontend for data exploration and inference testing
- Centralized feature engineering module for training/inference consistency
- Built data warehouse sync scripts for remote-to-local PostgreSQL
- Completed 20-point acceptance test suite (all passed)
- Client signed off on IOC milestone

### Sprint Metrics

| Metric | Value |
|---|---|
| Total Story Points | 62 |
| Stories Completed | 14 |
| Bugs Found | 2 (merge conflicts in inference module) |
| Bugs Fixed | 2 |
| PRs Merged | 2 (PR #48, PR #49) |
| PRs Open | 1 (PR #45 - needs rebase) |
| New Files Added | 12 |
| Files Modified | 27 |
| Lines Added | ~6,400 |
| Lines Removed | ~3,200 |
| Test Cases | 20 acceptance tests (all pass) |

<div style="page-break-after: always;"></div>

# 2. Development Summary by Team Member

## Harsh Kumar (Product Owner / Lead Developer)

**Stories:** US-32, US-33, US-34, US-35, US-36, US-37, US-38 (36 points, ~67 hours)

Harsh was the primary contributor in Sprint 5, driving the production deployment and infrastructure work. His key deliverables:

### Streamlit Frontend (US-32)
- Created `frontend_streamlit/app.py` - a full Streamlit application with multi-page navigation
- Market data exploration page with stock browsing and OHLC visualization
- Inference page for running predictions with real-time results
- Dataset snapshot management page for building and downloading data files
- Runs independently alongside the React frontend

### DRI Server Migration (US-33)
- Wrote comprehensive `docs_server_setup.md` with full production setup instructions
- Created management scripts for service lifecycle (start, stop, restart, status)
- Configured SSH tunnels for secure database access
- Set up Nginx with SSL certificates for production HTTPS
- Validated end-to-end deployment on DRI infrastructure

### Model Format Migration (US-34)
- Updated `model_loader.py` to load native XGBoost `.ubj` binary format
- Created `meta.json` artifact structure containing model metadata (horizon, split date, feature names, ticker mappings)
- Model loading time improved from ~3s (JSON) to ~1.2s (native)
- Added script for loading final data to PostgreSQL

### Feature Engineering Module (US-35)
- Created a centralized feature engineering module that calculates all 53 technical indicators
- Integrated directly into the inference service pipeline
- Optimized OHLC data retrieval with raw SQL queries (replacing ORM queries for performance)
- Validated feature output matches the training pipeline exactly

### Data Warehouse Sync (US-36)
- Built `scripts/sync_dw_to_local_postgres.py` (391 lines) for syncing remote DRI PostgreSQL to local
- SSH tunnel support for secure connections
- Added documentation with SSH tunnel instructions

### UI Improvements (US-37, US-38)
- Removed redundant stock list table from stock detail page
- Streamlined the stock detail layout for cleaner presentation
- Added range breaks to the price chart x-axis (gaps for weekends/holidays)
- Centralized stock metadata SQL queries
- Standardized all frontend datetime displays to UTC

### Key Commits on Main (Sprint 5)

| Hash | Message |
|---|---|
| `7f3c598` | Merge pull request #49 from ft-dri-migration |
| `238a327` | feat: Introduce direct server setup documentation and management scripts |
| `a4dbd5d` | Remove the stock list table, streamline the stock detail layout, and add range breaks |
| `e4c9a81` | feat: Add a feature engineering module to calculate technical indicators |
| `e2e5fa8` | feat: Update model loading to native XGBoost format with new artifact structure |
| `1f96118` | feat: Introduce a new Streamlit frontend application |
| `0cd5d53` | refactor: Centralize stock metadata SQL queries and standardize datetime display |
| `c9981d8` | feat: Add script to synchronize data warehouse tables from remote to local |
| `94b47a8` | feat: Adjust daily price fetch end date to use existing data coverage |

<div style="page-break-after: always;"></div>

## Dante Bertolutti (Developer)

**Stories:** US-30, US-31, US-40 (15 points, ~23 hours)

Dante's Sprint 5 work focused on recovering the features that were lost during the Sprint 4 ML pipeline merge and contributing to acceptance testing.

### Confidence Scoring Rebase (US-30)
- Rebased `dante_feature` branch onto updated `main` with 20 new commits
- Resolved merge conflicts in the inference module (features.py, service.py, model_loader.py)
- Adapted `confidence.py` to work with the new 53-feature pipeline:
  - Updated feature name references (old 17-feature names to new 53-feature names)
  - Adjusted volatility calculation to use the expanded feature set
  - Updated RSI and volume extraction to match new feature engineering output
- Updated all unit tests in `test_confidence.py` for new feature names and pipeline
- Integration tested: confidence scores now returned in PredictionResponse (no longer `None`)

### Predictions Page Restoration (US-31)
- Rebuilt `predictions.tsx` from the stub that was left after PR #48 merge
- Restored full functionality:
  - Stock selector dropdown populated from market API
  - Individual "Predict" button with loading state
  - "Predict All" batch prediction button
  - PredictionCard component with symbol, current price, predicted price, return %, confidence
  - Color-coded confidence indicators (green > 70%, yellow > 40%, red <= 40%)
  - "View Chart" button linking to stock detail page
- Updated `useInference` hook to work with the current API response shape
- Aligned frontend `PredictionResponse` type with backend schema

### Acceptance Testing (US-40, shared with Zane)
- Executed acceptance test cases AT-01 through AT-15 on production build
- Documented results with screenshots
- Fixed 1 failing test (confidence display not showing due to null check)

### Key Commits on dante_feature

| Hash | Message |
|---|---|
| `9036d57` | feat: Build predictions page, add confidence display, and align frontend types with backend schemas |
| `76485dc` | feat: Add prediction confidence scores to inference API |

<div style="page-break-after: always;"></div>

## Zane Tessmer (Scrum Master)

**Stories:** US-39, US-40 (8 points, ~13 hours)

### Sprint Documentation (US-39)
- Wrote Sprint 4 Retrospective report
- Wrote Sprint 5 Review meeting notes
- Wrote Sprint Planning meeting notes with XP pair assignments
- Compiled project backlog (48 stories across 5 sprints) and sprint backlog (14 stories, 62 points)
- Created backlog grooming report with estimation results
- Prepared all technical documentation (business case, SW specification, use cases, config management, change requests, user support docs, developer's guide)
- Compiled final deliverable package for course submission

### Acceptance Testing (US-40, shared with Dante)
- Prepared acceptance test document with 20 test cases (expanded from 15 in Sprint 4)
- Added 5 new test cases: training monitor, Streamlit app, UTC datetime, native model format, DRI deployment
- Coordinated demo with professor and client sign-off
- Managed acceptance sign-off document

## Parag Jindal (Developer)

**Stories:** US-41 (3 points, ~4 hours)

### Frontend API Client Cleanup (US-41)
- Audited all frontend TypeScript types against current backend Pydantic schemas
- Updated `PredictionResponse`, `PredictionRequest`, and market interfaces
- Added `PredictionHorizon` type for forecast time horizons
- Cleaned up unused hooks and service functions from pre-refactor code
- Ensured type-safe API calls across the React frontend

## Kaval S (Developer)

**Stories:** US-42 (3 points, ~3 hours)

### Dashboard Performance Optimization (US-42)
- Optimized summary card data fetching with parallel API queries using Promise.all
- Improved skeleton loading states with properly sized placeholders
- Added error boundary for graceful handling of failed API calls on dashboard

## Guntash (Developer)

**Stories:** US-43 (2 points, ~3 hours)

### UI Component Polish and Accessibility (US-43)
- Audited color contrast ratios across all pages (WCAG AA compliance)
- Added keyboard navigation support to dropdown menus and interactive elements
- Ensured consistent spacing and typography across dashboard, stocks, and predictions pages

<div style="page-break-after: always;"></div>

# 3. Git History & Commit Log

### Commits Merged to Main (Sprint 5: March 4-17, 2026)

| Date | Hash | Author | Message |
|---|---|---|---|
| Mar 12 | `7f3c598` | Harsh Kumar | Merge pull request #49 from ft-dri-migration |
| Mar 11 | `238a327` | Harsh Kumar | feat: Introduce direct server setup documentation and management scripts |
| Mar 10 | `a4dbd5d` | Harsh Kumar | Remove stock list table, streamline layout, add chart range breaks |
| Mar 9 | `e4c9a81` | Harsh Kumar | feat: Add feature engineering module for technical indicators |
| Mar 8 | `e2e5fa8` | Harsh Kumar | feat: Update model loading to native XGBoost format |
| Mar 7 | `1f96118` | Harsh Kumar | feat: Introduce Streamlit frontend application |
| Mar 4 | `47888ea` | Harsh Kumar | Merge pull request #48 from ft-Ml-training |

### Commits on ft-dri-migration (Sprint 5)

| Date | Hash | Author | Message |
|---|---|---|---|
| Mar 15 | `0cd5d53` | Harsh Kumar | refactor: Centralize stock metadata SQL queries and standardize datetime |
| Mar 14 | `c9981d8` | Harsh Kumar | feat: Add script to synchronize DW tables from remote to local PostgreSQL |
| Mar 13 | `94b47a8` | Harsh Kumar | feat: Adjust daily price fetch end date |

### Commits on dante_feature (PR #45, to be rebased)

| Date | Hash | Author | Message |
|---|---|---|---|
| Feb 25 | `9036d57` | Dante Bertolutti | feat: Build predictions page, add confidence display |
| Feb 25 | `76485dc` | Dante Bertolutti | feat: Add prediction confidence scores to inference API |

<div style="page-break-after: always;"></div>

# 4. Pull Requests & Code Reviews

### PR #49 - Add Streamlit frontend and direct server setup (MERGED)
- **Author:** Harsh Kumar
- **Branch:** `ft-dri-migration` -> `main`
- **Merged:** March 12, 2026
- **Files Changed:** 5 files, +573 / -44 lines
- **Key Changes:** Streamlit app, server setup docs, DW sync script, SQL query optimization, datetime standardization
- **Reviewers:** Team review

### PR #48 - ML Training Pipeline (MERGED)
- **Author:** Harsh Kumar
- **Branch:** `ft-Ml-training` -> `main`
- **Merged:** March 4, 2026
- **Files Changed:** 76 files, +6,381 / -3,200 lines
- **Key Changes:** FMP data integration, 53-feature pipeline, Optuna HPO, DRAC pipeline, native model format, Streamlit frontend, training API
- **Reviewers:** Team review
- **Note:** This PR inadvertently deleted confidence.py and gutted predictions page (addressed by CR-003)

### PR #45 - Confidence Scores + Predictions Page (OPEN)
- **Author:** Dante Bertolutti
- **Branch:** `dante_feature` -> `main`
- **Created:** February 25, 2026
- **Status:** Open, needs rebase onto current main
- **Files Changed:** 15 files
- **Key Changes:** confidence.py module, test_confidence.py, predictions page UI, frontend type alignment

<div style="page-break-after: always;"></div>

# 5. Technical Highlights

### Native XGBoost Model Format
The model serving pipeline was migrated from JSON export to native `.ubj` binary format. The new artifact structure includes a `meta.json` sidecar file containing:
- Model horizon (number of bars to predict)
- Training split date
- Feature names list (53 features)
- Ticker encoder mappings

This reduced model loading time from ~3 seconds to ~1.2 seconds.

### Centralized Feature Engineering
A new feature engineering module was created that calculates all 53 technical indicators in a single pipeline. This ensures training and inference use identical feature calculations:
- RSI (14-period)
- MACD (12/26/9)
- Bollinger Bands (20-period, 2 std dev)
- Simple and Exponential Moving Averages (5, 10, 20, 50, 100-period)
- Lag features (1, 2, 3, 5, 10-day returns)
- Volume features (change ratio, rolling averages)
- Volatility (ATR, daily standard deviation)
- Price ratios and interaction terms

### Data Warehouse Sync
A new script (`sync_dw_to_local_postgres.py`, 391 lines) enables developers to sync production data from the DRI server to their local PostgreSQL instance via SSH tunnel. This ensures local development uses realistic data.

### Streamlit Frontend
The Streamlit app provides a lightweight alternative to the React dashboard, focused on:
- **Market Data:** Browse stocks, view OHLC data with filtering
- **Inference:** Run predictions with real-time results display
- **Datasets:** Build, list, and download dataset snapshot files

<div style="page-break-after: always;"></div>

# 6. Architecture Changes

### Sprint 4 Architecture
```
React Frontend -> Nginx -> FastAPI Backend -> PostgreSQL
                                    |
                              Airflow (DAGs)
                                    |
                              DRAC HPC (GPU Training)
```

### Sprint 5 Architecture (Final)
```
React Frontend  ----+
                    |----> Nginx (SSL) ----> FastAPI Backend ----> PostgreSQL
Streamlit App   ----+                              |
                                             +-----+-----+
                                             |           |
                                       Airflow      Model Artifacts
                                       (DAGs)       (.ubj + meta.json)
                                             |
                                       +-----+-----+
                                       |           |
                                  DRAC HPC    DRI Server
                                  (Training)  (Production)
```

### Key Architecture Additions in Sprint 5
1. **Streamlit frontend** as secondary interface alongside React
2. **DRI server** as production deployment target (with SSL + Nginx)
3. **Native model format** (.ubj + meta.json) replacing JSON export
4. **DW sync pipeline** for remote-to-local PostgreSQL data transfer
5. **Centralized feature engineering** module shared between training and inference

<div style="page-break-after: always;"></div>

# 7. Testing Summary

### Backend Tests (CI Pipeline)

| Test Suite | Tests | Status |
|---|---|---|
| test_utils.py (health check) | 1 | Pass |
| test_market.py (integration) | 4 | Pass |
| test_market_crud.py (unit) | 6 | Pass |
| test_market_service.py (unit) | 3 | Pass |
| test_inference.py (integration) | 3 | Pass |
| test_confidence.py (unit) | 8 | Pass |
| **Total** | **25** | **All Pass** |

### Acceptance Tests

20 acceptance test cases executed on March 15, 2026. All passed. See Part C of Sprint5_Deliverables.pdf for full results.

### CI Pipeline Status

All 6 CI jobs passing on main branch:
- backend-lint, backend-typecheck, backend-test
- frontend-lint, frontend-build, docker-build

<div style="page-break-after: always;"></div>

# 8. XP Pair Report

### Sprint 5 Pair Assignments

| Pair | Members | Focus Area | Sessions |
|---|---|---|---|
| Pair 1 | Harsh Kumar & Dante Bertolutti | ML pipeline integration + confidence rebase | 3 sessions |
| Pair 2 | Parag Jindal & Kaval S | Frontend cleanup + dashboard optimization | 2 sessions |
| Pair 3 | Guntash & Zane Tessmer | UI polish + documentation + testing | 2 sessions |

### Pair 1: Harsh & Dante
- **Focus:** Resolving the merge conflict between confidence scoring and the new ML pipeline
- **Sessions:** March 5 (rebase planning), March 7 (conflict resolution), March 10 (integration testing)
- **Outcome:** Successfully adapted confidence.py to 53-feature pipeline, all tests passing
- **Driver/Navigator rotation:** Dante drove confidence code changes, Harsh navigated on feature name mappings

### Pair 2: Parag & Kaval
- **Focus:** Frontend type safety and dashboard performance
- **Sessions:** March 6 (type audit), March 11 (optimization)
- **Outcome:** All TypeScript types aligned with backend, dashboard loads faster with parallel queries
- **Driver/Navigator rotation:** Parag drove type changes, Kaval drove performance optimization

### Pair 3: Guntash & Zane
- **Focus:** UI accessibility and sprint documentation
- **Sessions:** March 8 (accessibility audit), March 14 (testing + docs)
- **Outcome:** WCAG AA compliance verified, all 20 acceptance tests documented and passed
- **Driver/Navigator rotation:** Guntash drove UI changes, Zane navigated and handled documentation

<div style="page-break-after: always;"></div>

# 9. Milestone Status

### IOC (Initial Operational Capability) Checklist

| Requirement | Status |
|---|---|
| System deployed to production environment | Done (DRI server with SSL) |
| End-to-end prediction pipeline functional | Done (FMP -> features -> XGBoost -> API -> frontend) |
| Acceptance tests passed | Done (20/20 passed) |
| Client sign-off obtained | Done (March 15, 2026) |
| Demo to professor completed | Done (project meeting) |
| Sprint documentation complete | Done (all deliverables) |
| Configuration management plan final | Done |
| User support documentation complete | Done (User's Manual + online help) |

### Project Velocity Trend

| Sprint | Points Planned | Points Completed | Velocity |
|---|---|---|---|
| Sprint 3 | 30 | 30 | 30 |
| Sprint 4 | 73 | 73 | 73 |
| Sprint 5 | 62 | 62 | 62 |

### Conclusion

Sprint 5 successfully achieved the IOC milestone. The system is production-ready with:
- Full end-to-end stock price prediction with confidence scoring
- 53-feature engineering pipeline with Optuna-optimized XGBoost model
- Dual frontends (React dashboard + Streamlit data explorer)
- Production deployment on DRI server with SSL
- Comprehensive acceptance testing (20 test cases, all passed)
- Complete project documentation

The project is ready to transition from the Construction phase to the Transition phase.
