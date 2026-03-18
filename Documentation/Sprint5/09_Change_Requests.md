---
pdf_options:
  format: Letter
  margin: 22mm
  headerTemplate: '<div style="font-size:8px;width:100%;text-align:center;color:#888;">MarketSight - Change Requests</div>'
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

## Change Request Document

**Prepared by:** Zane Tessmer (Scrum Master)

COSC 471 - Winter 2026 | Okanagan College

March 17, 2026

</div>

<div style="page-break-after: always;"></div>

# Change Request Summary

| CR ID | Title | Priority | Status | Sprint |
|---|---|---|---|---|
| CR-001 | Remove authentication module from MVP | Medium | Approved & Implemented | Sprint 4 |
| CR-002 | Add prediction confidence scores to API | High | Approved & Implemented | Sprint 4 |
| CR-003 | Restore confidence scoring deleted during ML merge | High | Approved & Implemented | Sprint 5 |
| CR-004 | Migrate to native XGBoost .ubj model format | Medium | Approved & Implemented | Sprint 5 |
| CR-005 | Add Streamlit as secondary frontend | Medium | Approved & Implemented | Sprint 5 |

<div style="page-break-after: always;"></div>

# CR-001: Remove Authentication Module from MVP

| Field | Details |
|---|---|
| **CR ID** | CR-001 |
| **Title** | Remove authentication module from MVP |
| **Requested By** | Harsh Kumar (Product Owner) |
| **Date Submitted** | February 10, 2026 |
| **Priority** | Medium |
| **Status** | Approved & Implemented |

**Description:** Remove the authentication module (JWT-based login/signup) from the Sprint 4 scope to prioritize core prediction features. Authentication will be re-implemented in a future sprint using JWT tokens.

**Justification:** The client prioritized prediction accuracy and confidence scoring over authentication for the MVP demo. The existing auth module was built on a template and needed significant rework to integrate with the market and inference modules. Development time was better spent on core prediction features.

**Impact Analysis:**
- Users can access all endpoints without authentication
- CORS is set to allow all origins
- Acceptable for development/demo phase
- Must be addressed before any production deployment with real users

**Approval:** Approved by team consensus on February 10, 2026.

---

# CR-002: Add Prediction Confidence Scores to API

| Field | Details |
|---|---|
| **CR ID** | CR-002 |
| **Title** | Add prediction confidence scores to API |
| **Requested By** | Client (stakeholder feedback from Sprint 3 demo) |
| **Date Submitted** | February 10, 2026 |
| **Priority** | High |
| **Status** | Approved & Implemented |

**Description:** Add a confidence score (0.0 to 1.0) to each prediction response. The score should be based on market conditions (volatility, RSI, volume) and prediction characteristics (return magnitude).

**Justification:** Client feedback from the Sprint 3 demo specifically requested confidence scores to help users assess forecast reliability. Without confidence scores, users have no way to gauge how trustworthy a prediction is.

**Impact Analysis:**
- New `confidence_score` field added to PredictionResponse schema
- New `confidence.py` module created (138 lines)
- New `test_confidence.py` test file (213 lines, 8 test cases)
- Frontend updated with color-coded confidence indicators
- No breaking changes to existing API contracts (new field is additive)

**Approval:** Approved by Product Owner on February 10, 2026.
**Implementation:** Completed by Dante Bertolutti on February 25, 2026 (PR #45).

---

# CR-003: Restore Confidence Scoring Deleted During ML Merge

| Field | Details |
|---|---|
| **CR ID** | CR-003 |
| **Title** | Restore confidence scoring deleted during ML pipeline merge |
| **Requested By** | Dante Bertolutti (Developer) |
| **Date Submitted** | March 4, 2026 |
| **Priority** | High |
| **Status** | Approved & Implemented |

**Description:** PR #48 (ML pipeline merge, 76 files changed) inadvertently deleted the `confidence.py` module, `test_confidence.py` tests, and replaced the predictions page UI with a stub. These features need to be rebased and re-integrated with the new 53-feature inference pipeline.

**Justification:** Confidence scoring (GitHub Issue #46) was a client-requested feature completed in Sprint 4. The predictions page was the primary user interface for generating forecasts. Both were lost during a large merge that refactored the inference module without coordinating with the open PR #45.

**Impact Analysis:**
- `dante_feature` branch (PR #45) must be rebased onto updated `main` (20 new commits)
- `confidence.py` must be adapted for new 53-feature names and pipeline
- `test_confidence.py` must be updated for new expected values
- Predictions page must be rebuilt to work with updated PredictionResponse type
- Estimated rework: ~16 hours (2 user stories, 10 story points)

**Root Cause:** No merge coordination meeting was held before merging a large refactor that affected a shared module (inference) while another PR was open against the same module.

**Prevention:** Merge coordination meetings now required before merging PRs that affect shared modules. Branch protection rules reviewed.

**Approval:** Approved by team consensus on March 4, 2026.
**Implementation:** Completed by Dante Bertolutti in Sprint 5 (US-30, US-31).

---

# CR-004: Migrate to Native XGBoost .ubj Model Format

| Field | Details |
|---|---|
| **CR ID** | CR-004 |
| **Title** | Migrate from JSON model format to native XGBoost .ubj |
| **Requested By** | Harsh Kumar (Product Owner) |
| **Date Submitted** | March 6, 2026 |
| **Priority** | Medium |
| **Status** | Approved & Implemented |

**Description:** Switch model artifact storage from XGBoost JSON export to native `.ubj` binary format with an accompanying `meta.json` file containing model metadata.

**Justification:** Native format loads significantly faster (~1.2s vs ~3s for JSON), uses less disk space, and the `meta.json` sidecar provides structured metadata including horizon, split date, feature names, and ticker mappings.

**Impact Analysis:**
- Updated `model_loader.py` to read native .ubj format
- New artifact directory structure with `meta.json`
- Training pipeline updated to export in new format
- No changes to API contracts (transparent to frontend)
- Backwards incompatible: old JSON model files no longer supported

**Approval:** Approved by Product Owner on March 6, 2026.
**Implementation:** Completed by Harsh Kumar (US-34).

---

# CR-005: Add Streamlit as Secondary Frontend

| Field | Details |
|---|---|
| **CR ID** | CR-005 |
| **Title** | Add Streamlit as secondary frontend |
| **Requested By** | Harsh Kumar (Product Owner) |
| **Date Submitted** | March 8, 2026 |
| **Priority** | Medium |
| **Status** | Approved & Implemented |

**Description:** Add a Streamlit-based frontend application alongside the existing React dashboard, focused on data exploration, inference testing, and dataset snapshot management.

**Justification:** Data analysts and ML engineers need a quick way to explore market data and test predictions without the full React UI. Streamlit provides rapid prototyping for data-focused workflows and can be deployed independently.

**Impact Analysis:**
- New `frontend_streamlit/` directory with `app.py`
- New Docker Compose service for Streamlit (port 8501)
- Runs independently from the React frontend
- No changes to existing React code or backend API
- Consumes the same backend API endpoints

**Approval:** Approved by team on March 8, 2026.
**Implementation:** Completed by Harsh Kumar (US-32). Merged via PR #49.
