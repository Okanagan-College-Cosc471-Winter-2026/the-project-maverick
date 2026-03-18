---
pdf_options:
  format: Letter
  margin: 22mm
  headerTemplate: '<div style="font-size:8px;width:100%;text-align:center;color:#888;">MarketSight - Scrum Master Project Report</div>'
  footerTemplate: '<div style="font-size:8px;width:100%;text-align:center;color:#888;"><span class="pageNumber"></span> / <span class="totalPages"></span></div>'
  displayHeaderFooter: true
stylesheet: https://cdnjs.cloudflare.com/ajax/libs/github-markdown-css/5.5.1/github-markdown.min.css
body_class: markdown-body
css: |-
  body { font-size: 12px; line-height: 1.7; }
  h1 { color: #1a5276; border-bottom: 2px solid #2980b9; padding-bottom: 6px; }
  h2 { color: #1a5276; border-bottom: 1px solid #bdc3c7; padding-bottom: 4px; margin-top: 18px; }
  h3 { color: #2c3e50; margin-top: 12px; }
  table { font-size: 11px; width: 100%; border-collapse: collapse; }
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

## Project Report by Scrum Master

**Prepared by:** Zane Tessmer (Scrum Master)

COSC 471 - Winter 2026 | Okanagan College

March 17, 2026

</div>

<div style="page-break-after: always;"></div>

# 1. Project Issues

## 1.1 Issue Tracker Summary

Issues were tracked via GitHub Issues with labels (`ml-pipeline`, `frontend`, `testing`, `api`). The following table summarizes all project issues and their resolution status:

| Issue # | Title | Assigned To | Due Date | Status | Resolution |
|---|---|---|---|---|---|
| #46 | Create Prediction Quality Estimate Feature | Dante Bertolutti | Feb 25 | Closed | Implemented confidence scoring in Sprint 4 |
| #36 | Add feature validation tests (no NaN, correct ranges) | Harsh Kumar | Mar 10 | Open | Deferred to backlog; manual validation in place |
| #35 | Design and create market.features table schema | Harsh Kumar | Mar 3 | Open | Features calculated on-the-fly instead of stored |
| #34 | Create feature backfill job for 2yr history | Harsh Kumar | Mar 4 | Closed | Completed with FMP gap-filling scripts |
| #33 | Add volume change and return features | Harsh Kumar | Mar 3 | Open | Included in 53-feature pipeline (not as separate issue) |
| #32 | Add volatility features (daily std, ATR) | Harsh Kumar | Mar 3 | Open | Included in 53-feature pipeline |
| #31 | Implement MACD calculation (12/26/9) | Harsh Kumar | Mar 3 | Open | Included in 53-feature pipeline |
| #30 | Implement RSI computation (14-period) | Harsh Kumar | Mar 3 | Open | Included in 53-feature pipeline |
| #29 | Build rolling window calculations | Harsh Kumar | Mar 3 | Open | Included in 53-feature pipeline |
| #28 | Add TypeScript types matching backend schemas | Parag Jindal | Mar 10 | Open | Partially addressed in Sprint 5 (US-41) |
| #27 | Connect stock selector + chart to live API | Parag Jindal | Mar 3 | Open | Implemented in stock detail page |
| #26 | Build useOHLC hook | Harsh Kumar | Mar 4 | Closed | Implemented and working |
| #25 | Build useStocks hook | Parag Jindal | Mar 3 | Open | Implemented via stocksQueryOptions |

**Note:** Issues #29-33 were individually tracked but were all resolved as part of Harsh's comprehensive 53-feature engineering pipeline (US-27). They remain "open" on GitHub but are functionally complete.

## 1.2 Critical Issues Encountered

### Issue: Merge Conflict Overwrote Sprint 4 Features (CR-003)
- **Severity:** High
- **Date Identified:** March 4, 2026
- **Assigned To:** Dante Bertolutti
- **Description:** PR #48 (ML pipeline merge) deleted `confidence.py`, `test_confidence.py`, and gutted `predictions.tsx`. Dante's Sprint 4 work on confidence scoring and the predictions page was lost from `main`.
- **Root Cause:** Large feature branch (76 files changed) was merged without coordination with PR #45 which was still open.
- **Resolution:** Dante rebased `dante_feature` onto updated `main` during Sprint 5 (US-30, US-31). Confidence module adapted to new 53-feature pipeline.
- **Lesson Learned:** Implemented merge coordination meetings before merging large PRs that affect shared modules.

### Issue: FMP API Rate Limiting During Data Backfill
- **Severity:** Medium
- **Date Identified:** February 20, 2026
- **Assigned To:** Harsh Kumar
- **Description:** FMP API returned 429 (rate limit) errors during historical data backfill for 2020-2023 gap.
- **Resolution:** Implemented chunked download strategy with configurable batch sizes and retry logic (US-26).

<div style="page-break-after: always;"></div>

# 2. Detailed Work by Team Member

## Harsh Kumar (Product Owner / Lead Developer)

| Sprint | Stories | Points | Hours |
|---|---|---|---|
| Sprint 3 | US-01, US-02, US-03, US-05, US-06 | 26 | ~40 hrs |
| Sprint 4 | US-11, US-12, US-13, US-16, US-17, US-18, US-26, US-27, US-28, US-29 | 51 | ~95 hrs |
| Sprint 5 | US-32, US-33, US-34, US-35, US-36, US-37, US-38 | 36 | ~51 hrs |
| **Total** | **22 stories** | **113 pts** | **~186 hrs** |

**Summary:** Harsh was the primary contributor across all sprints, responsible for the complete backend, ML pipeline, infrastructure, and DevOps. Key achievements include the 53-feature engineering pipeline, Optuna HPO training, FMP data integration, DRI production deployment, and Streamlit frontend.

## Dante Bertolutti (Developer)

| Sprint | Stories | Points | Hours |
|---|---|---|---|
| Sprint 4 | US-14, US-15 | 10 | ~13 hrs |
| Sprint 5 | US-30, US-31, US-40 | 15 | ~23 hrs |
| **Total** | **5 stories** | **25 pts** | **~36 hrs** |

**Summary:** Dante implemented the prediction confidence scoring system and the predictions page UI. In Sprint 5, he rebased his work onto the updated main branch, adapted the confidence module for the 53-feature pipeline, and contributed to acceptance testing.

## Zane Tessmer (Scrum Master)

| Sprint | Stories | Points | Hours |
|---|---|---|---|
| Sprint 3 | US-07, US-08 | 4 | ~8 hrs |
| Sprint 4 | US-23, US-24, US-25 | 9 | ~17 hrs |
| Sprint 5 | US-39, US-40 | 8 | ~13 hrs |
| **Total** | **7 stories** | **21 pts** | **~38 hrs** |

**Summary:** Zane managed all sprint ceremonies, documentation, and coordination. Authored all project documentation including the vision, business case, SW specification, use cases, configuration management plan, user's manual, developer's guide, and sprint deliverables.

## Parag Jindal (Developer)

| Sprint | Stories | Points | Hours |
|---|---|---|---|
| Sprint 4 | US-19, US-20 | 6 | ~11 hrs |
| Sprint 5 | US-41 | 3 | ~4 hrs |
| **Total** | **3 stories** | **9 pts** | **~15 hrs** |

## Kaval S (Developer)

| Sprint | Stories | Points | Hours |
|---|---|---|---|
| Sprint 4 | US-21 | 2 | ~3 hrs |
| Sprint 5 | US-42 | 3 | ~3 hrs |
| **Total** | **2 stories** | **5 pts** | **~6 hrs** |

## Guntash (Developer)

| Sprint | Stories | Points | Hours |
|---|---|---|---|
| Sprint 4 | US-22 | 2 | ~3 hrs |
| Sprint 5 | US-43 | 2 | ~3 hrs |
| **Total** | **2 stories** | **4 pts** | **~6 hrs** |

<div style="page-break-after: always;"></div>

# 3. Iteration Assessment

## Sprint 3 Assessment (Construction 1)
- **Goal:** Establish core infrastructure
- **Result:** All 8 stories completed (30 pts). Docker environment, ML notebook, initial frontend, CI/CD pipeline all delivered.
- **Grade:** Fully successful. Foundation was solid for Sprint 4.

## Sprint 4 Assessment (Construction 2)
- **Goal:** Deliver functional MVP with end-to-end prediction
- **Result:** All 19 stories completed (73 pts). Inference API, confidence scoring, predictions page, Airflow, FMP pipeline, 53-feature engineering, Optuna HPO, DRAC pipeline all delivered.
- **Issues:** PR #48 merge overwrote PR #45's work. Confidence scoring and predictions page lost from main.
- **Grade:** Technically successful (highest velocity) but merge process failure created rework in Sprint 5.

## Sprint 5 Assessment (Construction 3)
- **Goal:** Achieve IOC milestone
- **Result:** All 14 stories completed (62 pts). Confidence scoring restored, DRI deployment, Streamlit frontend, native model format, acceptance tests all passed.
- **Grade:** Fully successful. IOC milestone achieved with client sign-off.

## Overall Project Assessment
- **Total Stories:** 41 completed across 3 sprints
- **Total Points:** 165
- **Average Velocity:** 55 pts/sprint
- **Velocity Trend:** 30 -> 73 -> 62 (ramped up then stabilized)
- **IOC Status:** Achieved

# 4. Workload Information

| Team Member | Sprint 3 | Sprint 4 | Sprint 5 | Total Hours |
|---|---|---|---|---|
| Harsh Kumar | 40 hrs | 95 hrs | 51 hrs | **186 hrs** |
| Dante Bertolutti | 0 hrs | 13 hrs | 23 hrs | **36 hrs** |
| Zane Tessmer | 8 hrs | 17 hrs | 13 hrs | **38 hrs** |
| Parag Jindal | 8 hrs | 11 hrs | 4 hrs | **23 hrs** |
| Kaval S | 5 hrs | 3 hrs | 3 hrs | **11 hrs** |
| Guntash | 5 hrs | 3 hrs | 3 hrs | **11 hrs** |
| **Total** | **66 hrs** | **142 hrs** | **97 hrs** | **305 hrs** |
