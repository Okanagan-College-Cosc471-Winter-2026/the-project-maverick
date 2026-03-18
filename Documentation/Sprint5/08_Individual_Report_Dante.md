---
pdf_options:
  format: Letter
  margin: 22mm
  headerTemplate: '<div style="font-size:8px;width:100%;text-align:center;color:#888;">MarketSight - Individual Project Report</div>'
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

## Individual Project Report

**Name:** Dante Bertolutti
**Role:** Developer
**XP Pair:** Harsh Kumar (Sprint 4 & 5)
**Branch:** `dante_feature` (PR #45)

COSC 471 - Winter 2026 | Okanagan College

March 17, 2026

</div>

<div style="page-break-after: always;"></div>

# 1. Summary of Contributions

## 1.1 Overview

My primary contributions to MarketSight were the **prediction confidence scoring system** (backend) and the **predictions page UI** (frontend). These features allow users to see not just a price prediction, but also a reliability score that helps them assess how much to trust each forecast.

## 1.2 User Stories Completed

| Sprint | Story | Title | Points | Hours |
|---|---|---|---|---|
| Sprint 4 | US-14 | Add prediction confidence scoring | 5 | 6 |
| Sprint 4 | US-15 | Build predictions page UI | 5 | 7 |
| Sprint 5 | US-30 | Rebase and re-integrate confidence scoring | 5 | 9 |
| Sprint 5 | US-31 | Restore predictions page with new pipeline | 5 | 7 |
| Sprint 5 | US-40 | Final acceptance testing (shared) | 5 | 4.5 |
| **Total** | | | **25 pts** | **33.5 hrs** |

## 1.3 Commits

| Hash | Date | Message |
|---|---|---|
| `76485dc` | Feb 25, 2026 | feat: Add prediction confidence scores to inference API |
| `9036d57` | Feb 25, 2026 | feat: Build predictions page, add confidence display, and align frontend types with backend schemas |

# 2. Sprint 4 Work

## 2.1 Confidence Scoring (US-14)

I designed and implemented a heuristic confidence scoring system in `backend/app/modules/inference/confidence.py`. The module calculates a score between 0.0 and 1.0 based on four weighted market condition factors:

| Factor | Weight | Logic |
|---|---|---|
| **Volatility** | 35% | Lower recent price volatility = higher confidence |
| **Return Magnitude** | 30% | Smaller predicted moves = higher confidence |
| **Volume** | 20% | Normal trading volume = higher confidence |
| **RSI** | 15% | RSI near 50 (neutral) = higher confidence |

Each factor produces a sub-score (0-1) using sigmoid or clamp functions, and the weighted average becomes the final confidence score.

**Files created:**
- `backend/app/modules/inference/confidence.py` (138 lines)
- `backend/tests/modules/test_confidence.py` (213 lines, 8 test cases)

**Test cases written:**
- Volatility sub-score: low, medium, high volatility inputs
- RSI sub-score: neutral (50), overbought (>70), oversold (<30)
- Volume sub-score: normal, low, high volume
- Return magnitude sub-score: small, medium, large predictions
- Composite score: weighted combination
- Edge cases: NaN features, zero values, extreme inputs

## 2.2 Predictions Page (US-15)

I built the full predictions page frontend in `frontend/src/routes/dashboard/predictions.tsx`:

- **Stock Selector:** Dropdown populated from the market API with format "SYMBOL - Name"
- **Predict Button:** Generates a forecast for the selected stock with loading spinner
- **Predict All Button:** Batch generates forecasts for all tracked stocks
- **PredictionCard Component:** Displays symbol, current price, predicted price, return %, confidence score (color-coded), model version, prediction date
- **Color Coding:** Green (>70%), Yellow (40-70%), Red (<40%) confidence indicators
- **View Chart:** Button linking to the stock detail page for chart visualization

**Files modified:**
- `frontend/src/routes/dashboard/predictions.tsx` (rebuilt from stub)
- `frontend/src/hooks/useInference.ts` (updated for new API shape)
- `frontend/src/services/inference.ts` (added predictStock function)
- `frontend/src/types/index.ts` (aligned PredictionResponse with backend)

# 3. Sprint 5 Work

## 3.1 Confidence Scoring Rebase (US-30)

During Sprint 4, Harsh merged PR #48 (ML pipeline) which refactored the inference module. This inadvertently deleted my `confidence.py` module and its tests. In Sprint 5, I:

1. Rebased `dante_feature` onto the updated `main` (20 new commits from Harsh)
2. Resolved merge conflicts in `features.py`, `service.py`, and `model_loader.py`
3. Adapted `confidence.py` to work with the new 53-feature pipeline:
   - Updated feature name references (old 17-feature names to new 53-feature names)
   - Adjusted extraction functions for volatility, RSI, and volume from the new feature DataFrame
4. Updated all 8 unit tests for new feature names and expected values
5. Verified integration: confidence scores now returned in PredictionResponse (no longer `None`)

## 3.2 Predictions Page Restoration (US-31)

The predictions page on main was replaced with a stub ("No predictions yet"). I rebuilt it with the same functionality but adapted for the updated API:

- Updated `PredictionResponse` type to match new backend schema (includes `confidence: number | null`)
- Rebuilt PredictionCard to handle the new response shape
- Ensured "Predict All" works with the current stock list

## 3.3 Acceptance Testing (US-40)

Shared with Zane. I executed acceptance test cases AT-01 through AT-15:
- Verified dashboard summary cards, stock search, chart rendering
- Tested prediction generation (single and batch)
- Confirmed confidence color coding thresholds
- Validated error handling (404 for invalid stock, health check)
- Fixed 1 failing test: confidence display wasn't showing due to a null check

# 4. XP Pair Experience

## Sprint 4: Paired with Harsh Kumar
- **Focus:** Inference API integration + confidence scoring
- **My Role:** I implemented the confidence module while Harsh built the inference service. We coordinated on the `PredictionResponse` schema to ensure confidence scores would be included.
- **Sessions:** 3 pair programming sessions (design, integration, testing)

## Sprint 5: Paired with Harsh Kumar
- **Focus:** Resolving merge conflicts and adapting to new 53-feature pipeline
- **My Role:** I drove the confidence code changes while Harsh navigated on feature name mappings and explained the new pipeline structure.
- **Sessions:** 3 sessions (rebase planning, conflict resolution, integration testing)

# 5. Code Review

I reviewed the following code during the project:
- Harsh's inference service (`service.py`) - reviewed prediction flow logic
- Harsh's feature engineering changes - reviewed the 53-feature pipeline output format
- My own `confidence.py` - self-reviewed against the new feature names after rebase

# 6. Workload Summary

| Week | Hours | Activities |
|---|---|---|
| Feb 23-Mar 1 | 13 hrs | Confidence scoring implementation + predictions page |
| Mar 3-7 | 8 hrs | Rebase planning, conflict resolution, confidence adaptation |
| Mar 10-14 | 7 hrs | Predictions page rebuild, integration testing |
| Mar 15-17 | 5.5 hrs | Acceptance testing, bug fixes, documentation |
| **Total** | **33.5 hrs** | |

# 7. Lessons Learned

1. **Merge coordination is critical.** My Sprint 4 work was overwritten because we didn't coordinate before merging a large refactor. In the future, hold a sync meeting before merging PRs that touch shared modules.

2. **Heuristic scoring is pragmatic but limited.** The confidence scoring system uses hand-tuned weights. A better approach would be conformal prediction or calibrated probabilities from the model itself.

3. **Rebasing is painful but necessary.** The rebase onto 20 new commits was time-consuming, but it forced me to understand Harsh's changes deeply, which made the adaptation smoother.

4. **Frontend work depends on stable APIs.** The predictions page had to be rebuilt twice because the backend API response shape changed. Establishing API contracts early would prevent this.
