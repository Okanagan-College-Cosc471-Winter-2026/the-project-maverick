# Sprint Review — Feb 18 – Mar 4, 2026

> Auto-generated summary of all activity across every branch in the two weeks leading up to **2026-03-04**.

---

## 📋 Closed Issues

| # | Title | Closed |
|---|-------|--------|
| [#46](https://github.com/Okanagan-College-Cosc471-Winter-2026/the-project-maverick/issues/46) | Create Prediction Quality Estimate Feature | 2026-02-25 |

---

## 🔀 Open Pull Requests (created this sprint)

| # | Title | Author | Created |
|---|-------|--------|---------|
| [#45](https://github.com/Okanagan-College-Cosc471-Winter-2026/the-project-maverick/pull/45) | feat: Add confidence scores, build predictions page, and align frontend types | Dante-Bertolutti | 2026-02-25 |

---

## 🛠️ Work Completed by Area

### ML / Data Pipeline (`ft-Ml-training` branch — Harshksaw)

#### FMP Data Integration
- Replaced `yfinance` with **Financial Modeling Prep (FMP)** API for historical data downloads.
- Added a script to **fill 5-minute OHLCV data gaps** (2020–2023) from the FMP API.
- Refactored FMP data download to handle API rate limits via **chunking**.

#### Feature Engineering & Model Training
- Implemented a **53-feature engineering pipeline** for inference (technical indicators, lag features, etc.).
- Built an initial **ML pipeline**: PostgreSQL data extraction → feature engineering → XGBoost training with **Optuna HPO**.
- Added an `XG_BOOST_2` notebook with rsync-based data pull and advanced modelling experiments.
- Updated XGBoost model hyper-parameters and added analysis plots to the training notebook.

#### DRAC End-to-End Pipeline
- Implemented a full **DRAC model training pipeline**: data extraction, feature engineering, model training, backend API endpoint, Airflow DAG, and a new frontend dashboard.
- Added scripts and documentation for **serving processed Parquet data to DRAC** over HTTP.
- Uploaded model artefacts to **Google Drive** via a dedicated upload script.
- Centralised ML model metadata into `meta.json` files per model.

#### Backend & Infrastructure
- Added a **data snapshot API** (build / list / download dataset files from the database).
- Added an **API endpoint** for retrieving stock data coverage.
- Expanded `stock_registry` ORM columns for compatibility with the new schema.
- Created a **daily dataset snapshot Airflow DAG**.
- Configured **Nginx** as a DB proxy with SSL and as a static file server.
- Consolidated ML database configuration into the main `docker-compose.yml`; removed the standalone `ml/docker-compose.yml`.
- Updated default database connection parameters in the import script.
- Added `FMP_API_KEY` to the project environment variables.

---

### Frontend Predictions Page (`dante_feature` branch — Dante-Bertolutti)

- **Predictions page** (`frontend/src/routes/dashboard/predictions.tsx`): replaced empty placeholder with a fully functional interface including a stock selector dropdown, prediction table, and confidence display.
- **Confidence scores**: added `confidence` field to the inference API response and surfaced it in the frontend UI.
- **Type alignment**: updated frontend TypeScript types to match the updated backend Pydantic schemas.

---

## 📊 Commit Activity (Feb 18 – Mar 4, 2026)

| Date | SHA | Author | Branch | Summary |
|------|-----|--------|--------|---------|
| 2026-03-03 | `28aad7b` | Harshksaw | ft-Ml-training | Add FMP API key and expand stock registry columns |
| 2026-03-03 | `98a692e` | Harshksaw | ft-Ml-training | Script to fill 5-min OHLCV data gaps from FMP |
| 2026-03-03 | `a924d2e` | Harshksaw | ft-Ml-training | API endpoint for stock data coverage |
| 2026-03-03 | `78b20ce` | Harshksaw | ft-Ml-training | 53-feature engineering for inference; optimise OHLC retrieval |
| 2026-03-03 | `f7757b6` | Harshksaw | ft-Ml-training | Centralise ML model metadata with `meta.json`; Google Drive upload; Nginx config |
| 2026-03-03 | `6503bb7` | Harshksaw | ft-Ml-training | Initial ML pipeline: Postgres extraction, feature engineering, XGBoost + Optuna HPO |
| 2026-03-03 | `5a7ab70` | Harshksaw | ft-Ml-training | End-to-end DRAC pipeline: data, training, API, Airflow DAG, frontend dashboard |
| 2026-03-03 | `3a090e6` | Harshksaw | ft-Ml-training | XG_BOOST_2 notebook with rsync data pull and advanced modelling |
| 2026-03-03 | `808bf7f` | Harshksaw | ft-Ml-training | Update ML environment and notebook; generate daily dataset snapshots |
| 2026-03-03 | `6d5ce7b` | Harshksaw | ft-Ml-training | Daily dataset snapshot Airflow DAG; backend volume mount; FMP key |
| 2026-03-03 | `b524168` | Harshksaw | ft-Ml-training | Data snapshot API (build / list / download) |
| 2026-03-03 | `28ffa4d` | Harshksaw | ft-Ml-training | FMP API key; update default DB connection params for import script |
| 2026-03-03 | `95ee1a1` | Harshksaw | ft-Ml-training | Consolidate ML DB config into main `docker-compose.yml` |
| 2026-03-03 | `dbe828b` | Harshksaw | ft-Ml-training | FMP data fetching for 2020–2023 historical gap; unified 5-min dataset |
| 2026-03-02 | `8986c26` | Harshksaw | ft-Ml-training | FMP download chunking for API limits; update XGBoost params and plots |
| 2026-02-27 | `6ffba0f` | Harshksaw | ft-Ml-training | Script and docs for serving processed data to DRAC; new XGBoost notebook |
| 2026-02-27 | `a2d0d75` | Harshksaw | ft-Ml-training | Download FMP historical data; process and merge; host Parquet via HTTP |
| 2026-02-27 | `43e8659` | Harshksaw | ft-Ml-training | Nginx DB proxy with SSL; shift ML data loading to local files; update model |
| 2026-02-27 | `e57c251` | Harshksaw | ft-Ml-training | Enhanced feature engineering; update DB connection; global model training infra |
| 2026-02-25 | `9036d57` | Dante-Bertolutti | dante_feature | Build predictions page; add confidence display; align frontend types |
| 2026-02-23 | `76485dc` | Dante-Bertolutti | dante_feature | Add prediction confidence scores to inference API |
