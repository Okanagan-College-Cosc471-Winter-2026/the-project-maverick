# Project Summary — Stock Market Prediction System

> Quick reference for team members. Full details live in [README.md](README.md), [development.md](development.md), and each sub-folder's own `README.md`.

---

## What Does This Project Do?

A **real-time ML-powered stock price prediction platform** that:

1. Stores historical OHLCV (Open/High/Low/Close/Volume) data for 29 major stocks in PostgreSQL.
2. Calculates technical indicators (RSI, MACD, Bollinger Bands) on the fly.
3. Runs an **XGBoost model** to predict the next-day closing price with a confidence score.
4. Exposes a **FastAPI REST backend** consumed by two frontends: a React 19 UI and a Streamlit dashboard.

---

## Backend (`backend/`)

**Stack:** Python 3.10+, FastAPI (async), SQLAlchemy 2.0, PostgreSQL 16, XGBoost, Alembic, Pydantic v2

### Key Modules

| Module | What it does |
|--------|-------------|
| `modules/market/` | CRUD for stocks and OHLCV data |
| `modules/inference/` | Loads the XGBoost model and runs predictions |
| `modules/data/` | Builds and serves Parquet/CSV data snapshots |
| `modules/training/` | Streams live training logs via Server-Sent Events (SSE) |

### Most-Used Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/v1/market/stocks` | GET | List all tracked stocks |
| `/api/v1/market/stocks/{symbol}/ohlc` | GET | Historical OHLCV bars (`?days=30`) |
| `/api/v1/inference/predict/{symbol}` | GET | XGBoost next-day price prediction |
| `/api/v1/data/build-snapshot` | POST | Export stock data to Parquet/CSV |
| `/api/v1/training/log/stream` | GET | SSE stream of live training logs |
| `/api/v1/utils/health-check/` | GET | Health check (`true`) |

### Running the Backend

```bash
cd backend
uv sync
uv run uvicorn app.main:app --reload --port 8000
# Interactive API docs: http://localhost:8000/docs
```

Or via Docker Compose (starts db + backend together):

```bash
docker compose up db backend
```

---

## Streamlit Frontend (`frontend_streamlit/`)

**Stack:** Python, Streamlit 1.44, Plotly 6, Pandas 2.2, Requests

An in-progress replacement for the React frontend — simpler to run locally without Docker.

### Pages

| Page | What it shows |
|------|--------------|
| **Overview** | API health, total stocks tracked, sector breakdown |
| **Stocks** | Search/filter stocks, candlestick chart, optional XGBoost prediction overlay |
| **Predictions** | Select a ticker → generate prediction → see forecast price, return %, confidence score, model version |
| **Snapshots** | Export stock data to Parquet/CSV and download the files |

### Running the Streamlit App

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r frontend_streamlit/requirements.txt

# Point it at a running backend
API_BASE_URL=http://localhost:8000/api/v1 streamlit run frontend_streamlit/app.py
# Opens at http://localhost:8501
```

---

## Other Components

| Folder | Purpose |
|--------|---------|
| `frontend/` | React 19 + TypeScript + Vite UI (primary web frontend) |
| `ml/` | XGBoost training pipeline, Jupyter notebooks, feature engineering |
| `model_artifacts/` | Pre-trained model files loaded by the backend |
| `airflow/` | Scheduled DAGs for data ingestion (Apache Airflow) |
| `docker/` | Dockerfiles for every service |

---

## Quick Architecture Diagram

```
Browser / Streamlit
        │
        ▼
 FastAPI Backend (:8000)
        │
   ┌────┴────┐
   ▼         ▼
PostgreSQL  XGBoost
  (OHLCV)   (Inference)
```

---

## Useful Links

- **Backend API docs (Swagger):** `http://localhost:8000/docs`
- **Streamlit UI:** `http://localhost:8501`
- **React UI:** `http://localhost:5173`
- **DB Admin (Adminer):** `http://localhost:8082`
- **Full dev setup guide:** [development.md](development.md)
- **Deployment guide:** [deployment.md](deployment.md)
