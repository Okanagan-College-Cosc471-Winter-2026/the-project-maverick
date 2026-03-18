---
pdf_options:
  format: Letter
  margin: 22mm
  headerTemplate: '<div style="font-size:8px;width:100%;text-align:center;color:#888;">MarketSight - Business Case</div>'
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

## Final Business Case

**Team:** Zane Tessmer, Harsh Kumar, Dante Bertolutti, Parag Jindal, Kaval S, Guntash

COSC 471 - Winter 2026 | Okanagan College

March 17, 2026

</div>

<div style="page-break-after: always;"></div>

# Business Case

## 1. Executive Summary

MarketSight is a machine-learning-powered stock market prediction platform developed as a capstone project for COSC 471 at Okanagan College. The system uses an Optuna-optimized XGBoost model trained on 53 technical indicator features to generate stock price predictions with confidence scores. Users interact with the platform through a React web dashboard or a Streamlit data exploration tool. The system is deployed on DRI production infrastructure with Nginx SSL reverse proxy.

The project has successfully reached the **Initial Operational Capability (IOC)** milestone at the end of Sprint 5, with all acceptance tests passed and client sign-off obtained.

## 2. Problem Statement

Retail investors and finance students lack affordable, accessible tools for data-driven stock price analysis. Existing platforms either require expensive subscriptions, offer no transparency into prediction methodology, or provide no measure of forecast reliability. There is a need for an open, educational platform that combines ML prediction with explainable confidence scoring.

## 3. Proposed Solution

MarketSight addresses this gap by providing:

- **ML-powered predictions** using XGBoost trained on 53 technical indicators (RSI, MACD, Bollinger Bands, lag features, volume metrics, etc.)
- **Confidence scoring** that quantifies prediction reliability based on volatility, RSI, volume, and return magnitude
- **Interactive visualizations** with candlestick/line charts and prediction overlays
- **Automated pipelines** via Airflow for daily data ingestion and weekly model retraining
- **Dual frontends** - a React dashboard for end users and a Streamlit app for data analysts

## 4. Target Users

| User Segment | Need | How MarketSight Helps |
|---|---|---|
| Retail investors | Data-driven price insights | Predictions with confidence scores |
| Day traders | Quick price forecasts | Batch predict across all tracked stocks |
| Finance students | Learning quantitative analysis | Transparent model with technical indicators |
| Data analysts | Data exploration and model testing | Streamlit interface for ad-hoc analysis |

## 5. Scope

### In Scope (Delivered)
- End-to-end stock price prediction pipeline (FMP data -> 53 features -> XGBoost -> API -> frontend)
- Prediction confidence scoring with color-coded display
- Interactive OHLC charts with prediction overlay
- Admin user management and user settings
- Automated Airflow DAGs for data seeding and model retraining
- DRI production server deployment with SSL
- Streamlit data exploration frontend
- Comprehensive test suite (25 backend tests, 20 acceptance tests)

### Out of Scope (Backlog)
- JWT user authentication
- WebSocket real-time streaming
- Prediction history storage and accuracy tracking
- Frontend unit tests with Vitest
- CORS restriction for production

## 6. Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Model accuracy needs improvement | Medium | Medium | 53-feature pipeline + Optuna HPO; continued tuning |
| No authentication on endpoints | Medium | High | CORS restriction; JWT auth in backlog |
| DRI server downtime | Low | High | Management scripts + monitoring |
| FMP API rate limiting | Low | Medium | Chunked downloads + gap-filling scripts |
| Merge conflicts between branches | Medium | Medium | Merge coordination meetings + branch protection |

## 7. Budget and Resources

| Resource | Details |
|---|---|
| **Infrastructure** | DRI production server (DRAC-provided), Docker-based |
| **Compute** | NVIDIA H100 GPU on DRAC cluster for training |
| **Data** | Financial Modeling Prep (FMP) API for historical OHLCV |
| **Team** | 6 developers across 3 sprints (Sprints 3-5) |
| **Timeline** | January - March 2026 (3 construction sprints) |

## 8. Success Criteria

| Criterion | Status |
|---|---|
| End-to-end prediction pipeline functional | Achieved |
| Confidence scores returned with every prediction | Achieved |
| Production deployment on DRI server | Achieved |
| All acceptance tests passed | Achieved (20/20) |
| Client sign-off on IOC milestone | Achieved |
| Sprint velocity sustainable | Achieved (30 -> 73 -> 62 pts) |
