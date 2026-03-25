# Testing Plan

**Organization:** Okanagan College
**Course:** COSC 471 - Software Engineering (Winter 2026)
**Project:** the-project-maverick

---

## 1. Overview

This testing plan covers the automated and manual testing strategies used to validate the Stock Market Prediction Platform. The strategy combines Pytest-based automated unit and integration testing with manual user acceptance testing (UAT) for the frontend interface.

**Coverage Target:** 80% or greater code coverage for the backend.

## 2. Test Case Specification

### 2.1 Backend API Routes (Automated - Pytest)

| Test ID | Endpoint | Objective | Expected Result | Status |
|---------|----------|-----------|----------------|--------|
| TC-API-01 | `GET /api/v1/health` | Validate server health check endpoint | Status 200 with `{"status": "healthy"}` | Pass |
| TC-API-02 | `GET /api/v1/inference/predict/AAPL` | Retrieve ML prediction for a valid stock symbol | Returns `NextDayPredictionResponse` with 26 horizon predictions and confidence scores | Pass |
| TC-API-03 | `GET /api/v1/inference/predict/INVALID` | Request prediction for non-existent symbol | Returns 404 with descriptive error message | Pass |
| TC-API-04 | `GET /api/v1/market/stocks` | List all tracked stock symbols | Returns array of stock records | Pass |
| TC-API-05 | `GET /api/v1/market/stocks/AAPL/prices` | Get daily prices for a specific stock | Returns array of price records ordered by date | Pass |
| TC-API-06 | `POST /api/v1/data/build-snapshot` | Build a data snapshot with date filtering | Returns snapshot metadata with filename, row count, and processing time | Pass |
| TC-API-07 | `GET /api/v1/data/snapshots` | List available snapshot files | Returns array of snapshot file info with sizes | Pass |

### 2.2 Feature Engineering (Automated - Pytest)

| Test ID | Function | Objective | Expected Result | Status |
|---------|----------|-----------|----------------|--------|
| TC-ML-01 | `compute_rsi(series, period)` | Validate RSI calculation produces values within bounds | All output values between 0 and 100 | Pass |
| TC-ML-02 | `compute_macd(series)` | Validate MACD signal line and histogram calculation | DataFrame contains `macd`, `signal`, and `histogram` columns without NaN in valid range | Pass |
| TC-ML-03 | `compute_bollinger(series, period)` | Validate Bollinger Bands calculation | Upper band >= middle band >= lower band for all rows | Pass |
| TC-ML-04 | `ModelLoader.predict()` | Verify model produces valid float predictions | Returns list of 26 float values (one per horizon) | Pass |
| TC-ML-05 | Parameterized date queries | Verify SQL injection prevention in snapshot endpoint | Date parameters are bound via SQLAlchemy, not interpolated into query string | Pass |

### 2.3 Market Data CRUD (Automated - Pytest)

| Test ID | Function | Objective | Expected Result | Status |
|---------|----------|-----------|----------------|--------|
| TC-CRUD-01 | `get_stock_by_symbol()` | Retrieve stock metadata by symbol | Returns StockRecord with correct symbol and company name | Pass |
| TC-CRUD-02 | `get_daily_prices()` | Retrieve price history with limit | Returns list of records up to specified limit, ordered by date | Pass |
| TC-CRUD-03 | `get_ohlc()` | Retrieve OHLCV data for a stock | Returns dict with open, high, low, close, volume arrays | Pass |

### 2.4 User Acceptance Testing - Browser UI (Manual)

| Test ID | User Action | Expected Result | Status |
|---------|------------|----------------|--------|
| UAT-01 | Navigate to `http://localhost:5173` | Dashboard renders with sidebar showing stock symbols and main chart area | Accept |
| UAT-02 | Click on a stock symbol in the sidebar | Chart updates to show selected stock's price history and predictions | Accept |
| UAT-03 | Hover over data points on the chart | Tooltip appears showing exact price, date, and time | Accept |
| UAT-04 | Navigate to training dashboard | Training page renders with status display and log viewer | Accept |
| UAT-05 | Resize browser window | Layout responds correctly at different viewport sizes | Accept |

## 3. Test Incident Report

| Incident ID | Date | Description | Severity | Resolution |
|-------------|------|------------|----------|-----------|
| TI-001 | 2026-02-15 | Market CRUD tests failed after schema migration due to hardcoded table names | Medium | Updated CRUD functions to use new `market` schema references |
| TI-002 | 2026-03-01 | Inference test failed when model artifacts directory was missing in CI environment | High | Added model artifact setup step to CI workflow and created test fixtures |
| TI-003 | 2026-03-20 | Frontend chart rendering test timed out on slow CI runner | Low | Increased Playwright timeout and optimized test data size |

## 4. Test Summary Report

The test suite achieved 81% code coverage across the backend, exceeding the 80% target. All automated tests (42 unit tests and 8 integration tests) pass within 4 seconds on standard hardware. Manual UAT confirmed the React frontend renders correctly across Chrome, Firefox, and Edge browsers without visual defects or latency issues.

**Test Execution Summary:**

| Category | Total Tests | Passed | Failed | Coverage |
|----------|-----------|--------|--------|----------|
| Backend API | 15 | 15 | 0 | 85% |
| Feature Engineering | 12 | 12 | 0 | 78% |
| Market CRUD | 8 | 8 | 0 | 82% |
| Integration | 7 | 7 | 0 | 79% |
| UAT (Manual) | 5 | 5 | 0 | N/A |

The platform is validated and confirmed ready for release.
