---
pdf_options:
  format: Letter
  margin: 22mm
  headerTemplate: '<div style="font-size:8px;width:100%;text-align:center;color:#888;">MarketSight - Vision Document</div>'
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

## Vision Document

**Team:** Zane Tessmer, Harsh Kumar, Dante Bertolutti, Parag Jindal, Kaval S, Guntash

COSC 471 - Winter 2026 | Okanagan College

March 17, 2026

</div>

<div style="page-break-after: always;"></div>

## Table of Contents

1. Introduction
2. Positioning
3. Stakeholder and User Descriptions
4. Product Overview
5. Product Features
6. Constraints
7. Quality Ranges
8. Precedence and Priority
9. Other Product Requirements
10. Documentation Requirements
11. Appendix: Glossary

<div style="page-break-after: always;"></div>

# 1. Introduction

## 1.1 Purpose
This document describes the vision for MarketSight, a web-based stock market prediction platform that uses machine learning to forecast stock prices. It captures the stakeholder needs, high-level features, and constraints that shape the system.

## 1.2 Scope
MarketSight is a capstone project for COSC 471 at Okanagan College. The system provides end-to-end stock price prediction with confidence scoring, interactive data visualization, automated data pipelines, and production deployment. The project spans three construction sprints (Sprints 3-5, January-March 2026).

## 1.3 References
- IBM Rational Unified Process (RUP) Vision template
- Agile Unified Process (AUP) guidelines
- COSC 471 course deliverable requirements

<div style="page-break-after: always;"></div>

# 2. Positioning

## 2.1 Business Opportunity
The retail investment technology market continues to grow as individual investors seek data-driven tools. Most ML-based prediction platforms are either proprietary (expensive) or academic (no production deployment). MarketSight fills the gap as an educational, open, and deployable platform that demonstrates a complete ML prediction pipeline from data ingestion to user interface.

## 2.2 Problem Statement

| Element | Description |
|---|---|
| **The problem of** | Lack of accessible, transparent stock prediction tools |
| **Affects** | Retail investors, finance students, and data analysts |
| **The impact of which is** | Reliance on gut feeling, expensive subscriptions, or opaque prediction tools |
| **A successful solution would** | Provide free ML-powered predictions with explainable confidence scores and interactive visualizations |

## 2.3 Product Position Statement

| Element | Description |
|---|---|
| **For** | Retail investors, finance students, and data analysts |
| **Who** | Need data-driven stock price forecasts with reliability indicators |
| **MarketSight** | Is a web-based stock prediction platform |
| **That** | Uses XGBoost ML models trained on 53 technical indicators to predict prices with confidence scores |
| **Unlike** | Expensive proprietary platforms or black-box prediction tools |
| **Our product** | Is transparent, educational, and deployable with automated data pipelines |

<div style="page-break-after: always;"></div>

# 3. Stakeholder and User Descriptions

## 3.1 Stakeholder Summary

| Stakeholder | Role | Responsibilities |
|---|---|---|
| Professor (Client) | Course instructor, project sponsor | Evaluates deliverables, signs acceptance tests |
| Assistant Instructor | Teaching assistant | Reviews submissions, provides feedback |
| Zane Tessmer | Scrum Master | Sprint ceremonies, documentation, coordination |
| Harsh Kumar | Product Owner / Lead Developer | Backlog prioritization, architecture, ML pipeline |
| Dante Bertolutti | Developer | Confidence scoring, predictions UI |
| Parag Jindal | Developer | Frontend routing, API client |
| Kaval S | Developer | User settings, dashboard optimization |
| Guntash | Developer | Dashboard cards, UI polish |

## 3.2 User Summary

| User Type | Description | Responsibilities |
|---|---|---|
| **Retail Investor** | Individual seeking price forecasts | Browse stocks, generate predictions, interpret confidence |
| **Day Trader** | Active trader needing quick forecasts | Batch predict, compare returns, view charts |
| **Finance Student** | Learner studying quantitative analysis | Explore data, understand indicators, study model behavior |
| **Data Analyst** | Technical user exploring market data | Use Streamlit for ad-hoc queries, dataset management |
| **Administrator** | System admin managing user accounts | Add/edit/delete users, manage permissions |

## 3.3 User Environment
- Users access MarketSight through a modern web browser (Chrome, Firefox, Edge, Safari)
- The React dashboard runs at the deployed URL or `http://localhost:5173` in development
- The Streamlit data explorer runs separately for analyst workflows
- Administrators need superuser credentials to access the admin panel
- No software installation is required for end users

## 3.4 Key Stakeholder Needs

| Need | Priority | Current Solution | Proposed Solution |
|---|---|---|---|
| Stock price predictions | HIGH | Manual analysis or paid tools | Automated ML predictions via XGBoost |
| Prediction reliability | HIGH | None (blind trust) | Confidence scoring (0-100%) with color coding |
| Data visualization | HIGH | Third-party charting tools | Built-in candlestick/line charts with overlays |
| Batch predictions | MEDIUM | Run predictions one at a time | "Predict All" feature for all tracked stocks |
| Automated data freshness | MEDIUM | Manual data downloads | Airflow DAGs for daily seeding and weekly retraining |
| Data exploration | MEDIUM | SQL queries | Streamlit frontend for visual exploration |

<div style="page-break-after: always;"></div>

# 4. Product Overview

## 4.1 Product Perspective
MarketSight is a standalone web application. It does not integrate with third-party trading platforms or broker APIs. Market data is sourced from the Financial Modeling Prep (FMP) API. The system consists of:

- **React 19 Frontend** - TypeScript, Vite, Tailwind CSS, TanStack Router
- **FastAPI Backend** - Python 3.12, SQLAlchemy 2.0, Pydantic v2
- **PostgreSQL 16 Database** - Market data, user accounts
- **XGBoost ML Model** - Native .ubj format, Optuna-optimized, 53 features
- **Apache Airflow** - Data seeding and model retraining DAGs
- **Nginx** - Reverse proxy with SSL termination
- **Streamlit** - Secondary frontend for data exploration
- **Docker Compose** - Container orchestration for all services

## 4.2 Product Context Diagram

```
  +---------+     +----------+     +---------+
  | FMP API |---->| Airflow  |---->| Postgres |
  +---------+     | (DAGs)   |     | DB      |
                  +----------+     +----+----+
                                        |
  +---------+     +----------+     +----+----+
  | DRAC    |---->| ML Model |---->| FastAPI |
  | HPC     |     | (.ubj)   |     | Backend |
  +---------+     +----------+     +----+----+
                                        |
                  +----------+     +----+----+
                  | Nginx    |<----| React   |
                  | (SSL)    |     | Frontend|
                  +----------+     +---------+
                                        |
                                   +---------+
                                   |Streamlit|
                                   |Frontend |
                                   +---------+
```

## 4.3 Assumptions and Dependencies
- FMP API remains available and within rate limits
- DRAC HPC cluster provides GPU access for model training
- DRI server remains available for production hosting
- Team has Docker and Docker Compose installed for local development
- PostgreSQL 16 is used as the sole database engine

<div style="page-break-after: always;"></div>

# 5. Product Features

| ID | Feature | Description | Priority | Status |
|---|---|---|---|---|
| F-01 | Stock Price Prediction | XGBoost model predicts prices using 53 technical indicators | HIGH | Delivered |
| F-02 | Confidence Scoring | Heuristic score (0-1) based on volatility, RSI, volume, return magnitude | HIGH | Delivered |
| F-03 | Interactive Charts | Candlestick/line charts with time range selection and prediction overlay | HIGH | Delivered |
| F-04 | Batch Prediction | "Predict All" generates forecasts for every tracked stock at once | HIGH | Delivered |
| F-05 | FMP Data Integration | Historical OHLCV data from Financial Modeling Prep API | HIGH | Delivered |
| F-06 | 53-Feature Pipeline | RSI, MACD, Bollinger Bands, SMA/EMA, lag features, volume metrics | HIGH | Delivered |
| F-07 | Automated Pipelines | Airflow DAGs for daily data seeding and weekly model retraining | MEDIUM | Delivered |
| F-08 | Admin Panel | Superuser-only user management (add/edit/delete users) | MEDIUM | Delivered |
| F-09 | User Settings | Profile editing, password change, account deletion | LOW | Delivered |
| F-10 | Streamlit Explorer | Secondary frontend for data analysis, inference testing, datasets | MEDIUM | Delivered |
| F-11 | DRI Deployment | Production server with SSL, Nginx, management scripts | HIGH | Delivered |
| F-12 | Training Monitor | Real-time training job logs and progress visualization | MEDIUM | Delivered |
| F-13 | Dark Mode | Light/dark/system theme switching | LOW | Delivered |
| F-14 | JWT Authentication | User login/signup with JWT tokens | HIGH | Backlog |
| F-15 | WebSocket Streaming | Real-time prediction updates via WebSocket | MEDIUM | Backlog |
| F-16 | Prediction History | Store and track prediction accuracy over time | MEDIUM | Backlog |

<div style="page-break-after: always;"></div>

# 6. Constraints

| Constraint | Description |
|---|---|
| **Technology Stack** | Must use Python (FastAPI), TypeScript (React), PostgreSQL as core technologies |
| **Timeline** | 3 construction sprints (~10 weeks) with fixed course deadlines |
| **Team Size** | 6 developers with varying availability and skill levels |
| **Compute** | GPU training limited to DRAC HPC cluster (shared resource, queue-based) |
| **Data** | FMP API has rate limits; historical data limited to available symbols |
| **Budget** | No monetary budget; all infrastructure is institution-provided |
| **Academic** | Must follow Agile/Scrum methodology with documented ceremonies |

# 7. Quality Ranges

| Quality Attribute | Target | Achieved |
|---|---|---|
| Performance (API p50) | < 100ms | ~80ms |
| Performance (API p95) | < 300ms | ~250ms |
| Inference Latency | < 50ms | ~35ms |
| Concurrent Users | 100+ | Tested at 150 |
| Backend Test Coverage | > 80% | ~75% |
| CI Pipeline Time | < 10 min | ~7 min |
| Model Load Time | < 2s | ~1.2s |
| Availability | 99.5% | DRI server deployed |

# 8. Precedence and Priority

Features are prioritized using MoSCoW:

| Priority | Features |
|---|---|
| **Must Have** | Prediction API, confidence scoring, charts, batch predict, FMP data, DRI deployment |
| **Should Have** | Airflow automation, admin panel, Streamlit explorer, training monitor |
| **Could Have** | Dark mode, user settings, dashboard optimization |
| **Won't Have (this release)** | JWT auth, WebSocket streaming, prediction history |

# 9. Other Product Requirements

- The system must run in Docker containers for consistent deployment
- All API endpoints must be documented via Swagger UI (`/docs`)
- The CI pipeline must run on every push and PR to `main`
- Model artifacts must be versioned with `meta.json` metadata
- All database schema changes must use Alembic migrations

<div style="page-break-after: always;"></div>

# 10. Documentation Requirements

## 10.1 User Manual
A comprehensive User's Manual has been prepared covering all user workflows, chart interactions, prediction interpretation, and account management. See `Documentation/Sprint4/Users_Manual.pdf`.

## 10.2 Online Help
- Swagger UI at `/docs` for interactive API documentation
- ReDoc at `/redoc` for formatted API reference
- In-app tooltips on chart controls, prediction cards, and confidence indicators
- Error messages with actionable descriptions

## 10.3 Installation Guide
A separate Installation Guide provides step-by-step instructions for Docker Compose setup, environment configuration, and production deployment. See `Documentation/Sprint5/12_Installation_Guide.pdf`.

## 10.4 Configuration and Read Me
- `README.md` in project root with quick start instructions
- `.env.example` with all required environment variables documented
- `development.md` with code quality tools and testing commands
- `docs_server_setup.md` for DRI production server configuration

## 10.5 Labelling and Packaging
- Docker images tagged with version numbers (e.g., `marketsight-backend:v1.1.0`)
- Model artifacts include `meta.json` with version, training date, feature names
- Release tags created in GitHub for each sprint milestone

<div style="page-break-after: always;"></div>

# Appendix: Glossary

| Term | Definition |
|---|---|
| **OHLCV** | Open, High, Low, Close, Volume - standard market data points per trading session |
| **XGBoost** | Extreme Gradient Boosting - the ML algorithm used for price prediction |
| **Optuna** | Hyperparameter optimization framework used to tune XGBoost parameters |
| **FMP** | Financial Modeling Prep - the API providing historical market data |
| **RSI** | Relative Strength Index - momentum indicator (values 0-100) |
| **MACD** | Moving Average Convergence Divergence - trend-following indicator |
| **Bollinger Bands** | Volatility indicator using moving average with standard deviation bands |
| **Confidence Score** | Heuristic measure (0-1) of prediction reliability based on market conditions |
| **Airflow** | Apache Airflow - workflow automation for data pipelines |
| **DAG** | Directed Acyclic Graph - Airflow's pipeline definition format |
| **DRAC** | Digital Research Alliance of Canada - provides HPC compute resources |
| **DRI** | Digital Research Infrastructure - production server hosting |
| **IOC** | Initial Operational Capability - milestone where system is ready for pre-production testing |
| **MVP** | Minimum Viable Product - first functional release with core features |
| **Ticker Symbol** | Short abbreviation for a publicly traded stock (e.g., AAPL) |
| **Sector** | Broad industry classification (e.g., Technology, Healthcare) |
| **Volatility** | Measure of price fluctuation magnitude |
| **SMA/EMA** | Simple / Exponential Moving Average - trend indicators |
| **ATR** | Average True Range - volatility indicator |
| **Lag Features** | Previous period values used as prediction inputs |
