---
pdf_options:
  format: Letter
  margin: 22mm
  headerTemplate: '<div style="font-size:8px;width:100%;text-align:center;color:#888;">MarketSight - Testing Plan &amp; Acceptance Test</div>'
  footerTemplate: '<div style="font-size:8px;width:100%;text-align:center;color:#888;"><span class="pageNumber"></span> / <span class="totalPages"></span></div>'
  displayHeaderFooter: true
stylesheet: https://cdnjs.cloudflare.com/ajax/libs/github-markdown-css/5.5.1/github-markdown.min.css
body_class: markdown-body
css: |-
  body { font-size: 11.5px; line-height: 1.65; }
  h1 { color: #1a5276; border-bottom: 2px solid #2980b9; padding-bottom: 6px; }
  h2 { color: #1a5276; border-bottom: 1px solid #bdc3c7; padding-bottom: 4px; margin-top: 18px; }
  h3 { color: #2c3e50; margin-top: 12px; }
  table { font-size: 10.5px; width: 100%; border-collapse: collapse; }
  th { background-color: #2980b9; color: white; padding: 5px 8px; }
  td { padding: 4px 8px; border: 1px solid #ddd; }
  tr:nth-child(even) { background-color: #f4f8fb; }
  .cover { text-align: center; margin-top: 80px; }
  .cover h1 { font-size: 32px; border: none; }
  .cover h2 { font-size: 16px; border: none; color: #7f8c8d; font-weight: 400; }
  .cover .line { border-top: 3px solid #2980b9; width: 100px; margin: 20px auto; }
---

<div class="cover">

# MarketSight

## Stock Market Prediction System

<div class="line"></div>

## Testing Plan & Acceptance Test

**Prepared by:** Zane Tessmer & Dante Bertolutti

COSC 471 - Winter 2026 | Okanagan College

March 17, 2026

</div>

<div style="page-break-after: always;"></div>

# 1. Test Strategy Overview

## 1.1 Testing Levels

| Level | Scope | Tools | Responsibility |
|---|---|---|---|
| **Unit Tests** | Individual functions and methods | Pytest, Pytest-mock | Developers |
| **Integration Tests** | API endpoint request/response cycles | Pytest, FastAPI TestClient | Developers |
| **Regression Tests** | CI pipeline on every push/PR | GitHub Actions | Automated |
| **Acceptance Tests** | End-to-end user workflows | Manual testing | Zane & Dante |

## 1.2 Test Environment

| Environment | Configuration |
|---|---|
| **Unit/Integration** | In-memory SQLite via pytest fixtures |
| **Regression (CI)** | Ubuntu Latest, GitHub-hosted runner |
| **Acceptance** | Docker Compose (full stack) on local machine |

<div style="page-break-after: always;"></div>

# 2. Test Case Specification

## 2.1 Unit Test Cases

### Market CRUD (test_market_crud.py)

| TC-ID | Test Case | Input | Expected Output |
|---|---|---|---|
| TC-U01 | Create a stock record | Stock(symbol="AAPL", name="Apple") | Stock created in DB |
| TC-U02 | Read a stock by symbol | get_stock(session, "AAPL") | Returns Stock object |
| TC-U03 | Read non-existent stock | get_stock(session, "INVALID") | Returns None |
| TC-U04 | Create daily price record | DailyPrice(open, high, low, close, volume) | Price record created |
| TC-U05 | Read OHLC data for symbol | get_ohlc(session, "AAPL", days=5) | Returns list of 5 prices |
| TC-U06 | List stocks with filtering | list_stocks(session) | Returns all seeded stocks |

### Market Service (test_market_service.py)

| TC-ID | Test Case | Input | Expected Output |
|---|---|---|---|
| TC-U07 | List stocks via service | MarketService.list_stocks() | Returns stock list |
| TC-U08 | Get stock via service | MarketService.get_stock("AAPL") | Returns Stock |
| TC-U09 | Get OHLC via service | MarketService.get_ohlc("AAPL", 5) | Returns OHLC list |

### Confidence Scoring (test_confidence.py)

| TC-ID | Test Case | Input | Expected Output |
|---|---|---|---|
| TC-U10 | Volatility score - low | volatility=0.01 | Score near 1.0 |
| TC-U11 | Volatility score - high | volatility=0.10 | Score near 0.0 |
| TC-U12 | RSI score - neutral (50) | RSI=50 | Score near 1.0 |
| TC-U13 | RSI score - overbought (80) | RSI=80 | Score < 0.5 |
| TC-U14 | Volume score - normal | volume_ratio=1.0 | Score near 1.0 |
| TC-U15 | Return magnitude - small | return=0.01 | Score near 1.0 |
| TC-U16 | Composite confidence | All factors combined | Score between 0.0-1.0 |
| TC-U17 | Edge case - NaN features | NaN values in features | Handles gracefully |

## 2.2 Integration Test Cases

### Health Check (test_utils.py)

| TC-ID | Test Case | Input | Expected Output |
|---|---|---|---|
| TC-I01 | Health check endpoint | GET /api/v1/utils/health-check/ | 200, body: true |

### Market API (test_market.py)

| TC-ID | Test Case | Input | Expected Output |
|---|---|---|---|
| TC-I02 | List stocks endpoint | GET /api/v1/market/stocks | 200, returns stock array |
| TC-I03 | Get stock by symbol | GET /api/v1/market/stocks/AAPL | 200, returns stock |
| TC-I04 | Get OHLC data | GET /api/v1/market/stocks/AAPL/ohlc | 200, returns OHLC array |
| TC-I05 | Invalid stock 404 | GET /api/v1/market/stocks/INVALID | 404 |

### Inference API (test_inference.py)

| TC-ID | Test Case | Input | Expected Output |
|---|---|---|---|
| TC-I06 | Predict stock price | GET /api/v1/inference/predict/AAPL | 200, PredictionResponse |
| TC-I07 | Invalid stock prediction | GET /api/v1/inference/predict/INVALID | 404 |
| TC-I08 | Response schema check | Prediction response fields | All required fields present |

<div style="page-break-after: always;"></div>

# 3. Acceptance Test Specification

**Tested by:** Zane Tessmer & Dante Bertolutti
**Date:** March 15, 2026
**Environment:** Docker Compose (full stack), Chrome browser

## 3.1 Acceptance Test Cases

| AT-ID | Category | Test Description | Expected Result | Actual Result | Status |
|---|---|---|---|---|---|
| AT-01 | Dashboard | Navigate to /dashboard, verify 4 summary cards | Cards: stocks, sectors, model, API status | Displayed correctly | **PASS** |
| AT-02 | Stocks | Navigate to /dashboard/stocks, search "AAPL" | AAPL appears in filtered list | Found and displayed | **PASS** |
| AT-03 | Chart | Click AAPL, verify candlestick chart | Interactive chart with OHLC data | Rendered with range breaks | **PASS** |
| AT-04 | Chart | Toggle to line chart mode | Line series displayed | Line chart displayed | **PASS** |
| AT-05 | Chart | Select 1W time range | Chart zooms to 7 days | Applied correctly | **PASS** |
| AT-06 | Chart | Enable prediction overlay | Orange dashed line to predicted price | Overlay rendered | **PASS** |
| AT-07 | Predictions | Navigate to /dashboard/predictions | Page with stock selector | Loaded correctly | **PASS** |
| AT-08 | Predictions | Select AAPL, click Predict | Card: symbol, prices, return, confidence | All fields populated | **PASS** |
| AT-09 | Predictions | Verify confidence range | Score between 0-100% | Within valid range | **PASS** |
| AT-10 | Predictions | Click "Predict All" | Cards for all stocks | All predictions shown | **PASS** |
| AT-11 | Predictions | Verify confidence colors | Green >70%, Yellow 40-70%, Red <40% | Colors matched | **PASS** |
| AT-12 | API | GET /predict/INVALID | 404 error | "Stock not found" | **PASS** |
| AT-13 | API | GET /utils/health-check/ | 200, true | Response correct | **PASS** |
| AT-14 | CI | Run CI pipeline on main | All 6 jobs pass | All green | **PASS** |
| AT-15 | Docker | docker compose up | All services healthy | All running | **PASS** |
| AT-16 | Training | Navigate to /dashboard/training | Training monitor loads | Page loaded | **PASS** |
| AT-17 | Streamlit | Open Streamlit app | Market data visible | Data displayed | **PASS** |
| AT-18 | Datetime | Check timestamps across pages | All show UTC | UTC consistent | **PASS** |
| AT-19 | Model | Verify model loads (native .ubj) | Loads within 2s | Loaded in ~1.2s | **PASS** |
| AT-20 | Deployment | Access via production URL | App served with SSL | Served correctly | **PASS** |

<div style="page-break-after: always;"></div>

# 4. Test Incident Report

## Incident #1: Confidence Display Null Check

| Field | Details |
|---|---|
| **Incident ID** | TI-001 |
| **Date** | March 15, 2026 |
| **Test Case** | AT-09 (Verify confidence range) |
| **Severity** | Medium |
| **Description** | Confidence score was not displaying on prediction cards. The field showed blank instead of a percentage. |
| **Root Cause** | The predictions page had a null check `if (confidence !== null)` but the rebased code was returning `confidence` as `undefined` instead of `null` due to a type mismatch between the old and new API response shapes. |
| **Resolution** | Updated the null check to `if (confidence != null)` (loose equality) to handle both null and undefined. |
| **Fixed By** | Dante Bertolutti |
| **Verified By** | Zane Tessmer |

## Incident #2: Chart Range Breaks on Weekends

| Field | Details |
|---|---|
| **Incident ID** | TI-002 |
| **Date** | March 10, 2026 |
| **Test Case** | AT-03 (Candlestick chart rendering) |
| **Severity** | Low |
| **Description** | Candlestick charts showed large gaps on weekends where no trading occurred, making the chart hard to read. |
| **Root Cause** | The chart x-axis was using continuous time, including non-trading days. |
| **Resolution** | Added range breaks to the x-axis configuration to skip weekends and holidays. |
| **Fixed By** | Harsh Kumar |
| **Verified By** | Dante Bertolutti |

<div style="page-break-after: always;"></div>

# 5. Test Summary Report

## 5.1 Test Execution Summary

| Test Level | Total Tests | Passed | Failed | Pass Rate |
|---|---|---|---|---|
| Unit Tests | 17 | 17 | 0 | 100% |
| Integration Tests | 8 | 8 | 0 | 100% |
| Acceptance Tests | 20 | 20 | 0 | 100% |
| **Total** | **45** | **45** | **0** | **100%** |

## 5.2 Test Incidents Summary

| Total Incidents | Resolved | Open |
|---|---|---|
| 2 | 2 | 0 |

## 5.3 CI Pipeline Status

All 6 CI jobs passing on main branch:
- backend-lint: **PASS** (~30s)
- backend-typecheck: **PASS** (~45s)
- backend-test: **PASS** (~2 min, 25 tests)
- frontend-lint: **PASS** (~20s)
- frontend-build: **PASS** (~45s)
- docker-build: **PASS** (~3 min)

## 5.4 Test Conclusion

All 45 test cases across unit, integration, and acceptance testing levels have passed. Two test incidents were identified and resolved during the testing phase. The system meets the acceptance criteria for the IOC milestone.

## 5.5 Acceptance Sign-Off

All 20 acceptance test cases passed. The system is approved for Initial Operational Capability.

**Signed:**

Client Representative: _________________________ Date: _____________

Product Owner (Harsh Kumar): _________________________ Date: _____________

Scrum Master (Zane Tessmer): _________________________ Date: _____________

Tester (Dante Bertolutti): _________________________ Date: _____________
