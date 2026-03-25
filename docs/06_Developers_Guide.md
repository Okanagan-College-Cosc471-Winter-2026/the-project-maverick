# Developer's Guide

**Organization:** Okanagan College
**Course:** COSC 471 - Software Engineering (Winter 2026)
**Project:** the-project-maverick

---

## 1. Introduction

This guide provides software engineers navigating the codebase with a foundational understanding of the project's analysis models, design models, architectural layout, and code structures required to work on the Stock Prediction Platform.

---

## 2. Analysis Models

### 2.1 Use Case Diagram

The system revolves around three central actors:

```
[Retail Investor / Trader]
    |-- Views Dashboard
    |-- Changes Stock Symbol
    |-- Downloads Data Snapshot
    |-- Monitors Training Jobs

[System Backend (Automated)]
    |-- Fetches Latest OHLCV Data from External Financial API (FMP)
    |-- Generates ML Predictions (includes technical indicator calculation)
    |-- Stores predictions and market data in PostgreSQL

[Administrator / Developer]
    |-- Initiates Model Training
    |-- Reviews Training Logs
```

### 2.2 Domain Model

**Core Entities:**

| Entity | Key Attributes |
|--------|---------------|
| Stock | Symbol (e.g., AAPL), Company Name |
| MarketData | FK_Stock, Timestamp, Open, High, Low, Close, Volume |
| Prediction | FK_Stock, Timestamp, Horizon (0-25), Predicted Price, Confidence Score |
| DataSnapshot | Filename, Ticker, Format (Parquet/CSV), Row Count, Timestamp |

**Relationships:**

- A `Stock` has many `MarketData` records over time.
- A `MarketData` set triggers a `Prediction` set across 26 horizons.
- The `Dashboard` subscribes to combined `MarketData` and `Prediction` data via REST API.

### 2.3 Activity Diagram: Inference Pipeline

```
[Start: API request received for /predict/{symbol}]
    |
    v
[Query PostgreSQL for latest OHLCV data for symbol]
    |
    v
[Decision: Sufficient data available?]
    |-- No --> Return 400 "Insufficient data"
    |-- Yes --> Continue
    |
    v
[Calculate technical indicators (RSI, MACD, Bollinger Bands, ATR, OBV)]
    |
    v
[Build feature vector from engineered indicators]
    |
    v
[Load XGBoost model ensemble (26 horizon models)]
    |
    v
[Run inference across all 26 horizons]
    |
    v
[Structure response with predicted prices, timestamps, and confidence scores]
    |
    v
[Return NextDayPredictionResponse to client]
    |
[End]
```

---

## 3. Design Models

### 3.1 Architecture Overview

The system follows a decoupled 3-tier architecture, fully containerized with Docker:

| Layer | Technology | Responsibility |
|-------|-----------|---------------|
| Presentation (Tier 1) | React 19, Vite, TypeScript, TanStack Query | User interface, charting, data fetching |
| Application (Tier 2) | FastAPI, Python 3.10+, SQLAlchemy 2.0 | REST API, ML inference, feature engineering |
| Data (Tier 3) | PostgreSQL 16 | Market data storage, prediction persistence |

### 3.2 Class Diagram (Core Backend)

```
InferenceService (Static)
    predict_stock_price(session, symbol) -> NextDayPredictionResponse

ModelLoader (Singleton)
    load_model(model_name) -> dict of XGBRegressor
    predict(features, model_name) -> list[float]

FeatureEngineering
    compute_rsi(series, period) -> Series
    compute_macd(series) -> DataFrame
    compute_bollinger(series, period) -> DataFrame
    compute_atr(df, period) -> Series
    compute_obv(df) -> Series

MarketCRUD (Static)
    get_stock_by_symbol(session, symbol) -> StockRecord
    get_daily_prices(session, symbol, limit) -> list
    get_ohlc(session, symbol, period) -> dict

DataAPI (Router)
    build_snapshot(req: SnapshotRequest) -> dict
    list_snapshots() -> dict
    download_snapshot(filename) -> FileResponse
```

### 3.3 Sequence Diagram: Prediction Request

```
Dashboard (React)                FastAPI Router              InferenceService           ModelLoader          PostgreSQL
      |                               |                           |                        |                    |
      |-- GET /predict/AAPL --------->|                           |                        |                    |
      |                               |-- predict_stock_price --->|                        |                    |
      |                               |                           |-- get_ohlc ------------|---------------->  |
      |                               |                           |<-- OHLCV data ---------|------------------  |
      |                               |                           |                        |                    |
      |                               |                           |-- compute indicators -->|                    |
      |                               |                           |<-- feature vector ------|                    |
      |                               |                           |                        |                    |
      |                               |                           |-- predict(features) --->|                    |
      |                               |                           |<-- 26 predictions ------|                    |
      |                               |                           |                        |                    |
      |                               |<-- NextDayPrediction -----|                        |                    |
      |<-- JSON Response -------------|                           |                        |                    |
      |                               |                           |                        |                    |
```

---

## 4. Code Structure and Navigation

### 4.1 Project Source Code Map

```
the-project-maverick/
├── backend/
│   ├── app/
│   │   ├── main.py                    # FastAPI application instance
│   │   ├── api/
│   │   │   ├── main.py                # API router registration
│   │   │   └── deps.py                # Dependency injection (SessionDep)
│   │   ├── core/
│   │   │   └── config.py              # Environment configuration (Settings)
│   │   ├── modules/
│   │   │   ├── inference/
│   │   │   │   ├── api.py             # /predict/{symbol} endpoint
│   │   │   │   ├── service.py         # Inference orchestration logic
│   │   │   │   ├── model_loader.py    # XGBoost model loading singleton
│   │   │   │   ├── features.py        # Technical indicator calculations
│   │   │   │   └── schemas.py         # Pydantic response models
│   │   │   ├── market/
│   │   │   │   ├── api.py             # Market data endpoints
│   │   │   │   ├── crud.py            # Raw SQL queries for market data
│   │   │   │   ├── service.py         # Market service logic
│   │   │   │   └── schemas.py         # Market data schemas
│   │   │   ├── data/
│   │   │   │   └── api.py             # Data snapshot build/list/download
│   │   │   └── training/
│   │   │       └── api.py             # Training job management
│   │   └── models/                    # SQLAlchemy ORM models
│   └── tests/                         # Pytest test suite
├── frontend/
│   └── src/
│       ├── components/                # React UI components (Charts, Sidebar)
│       ├── routes/dashboard/          # Dashboard pages (stocks, training)
│       └── client/                    # Auto-generated API client
├── ml/
│   ├── notebooks/                     # Jupyter notebooks and training scripts
│   ├── scripts/                       # Data prep, training, and inference scripts
│   ├── drac/                          # DRAC cluster training scripts
│   └── training/                      # Production training pipeline
├── model_artifacts/                   # Pre-trained XGBoost model files
│   └── nextday_15m_path_final/        # 26 horizon models + metadata
├── airflow/dags/                      # Airflow DAG definitions
└── docker-compose.yml                 # Multi-service orchestration
```

### 4.2 Test Source Code

Tests are in `backend/tests/` organized by module:

- `tests/modules/test_market.py` - Market API endpoint tests
- `tests/modules/test_market_crud.py` - CRUD operation tests
- `tests/modules/test_market_service.py` - Service layer tests
- `tests/api/` - General API endpoint tests
- `tests/utils/` - Utility function tests

### 4.3 Setting Up a Development Workspace

**Backend:**

```bash
cd backend
uv sync
uv run alembic upgrade head
uv run fastapi dev app/main.py
```

**Frontend:**

```bash
cd frontend
npm install
npm run dev
```

**Full Stack (Docker):**

```bash
docker-compose up -d --build
```

All new code must be typed. Mypy and Ruff checks run automatically in CI workflows on every pull request.
