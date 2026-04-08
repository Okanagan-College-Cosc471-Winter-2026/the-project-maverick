# The Project Maverick

Market prediction platform built around a Postgres feature store, a FastAPI backend, trained model artifacts, and a Streamlit frontend.

## Current Stack

- Data layer: PostgreSQL
- Backend: FastAPI
- ML: XGBoost + pandas/scikit-learn tooling
- Frontend: Streamlit in `frontend_streamlit/`
- Artifacts: saved model bundles used for inference and simulation

## What The System Does

1. Collects and stores historical market data.
2. Computes engineered features used by the ML pipeline.
3. Trains base models and stores model artifacts.
4. Loads saved artifacts for inference and replay/simulation.
5. Displays predictions, charts, and side-by-side comparisons in Streamlit.

## Main Data Tables

- `ml.market_data_15m`
  Regular-session 15-minute OHLCV bars plus engineered feature columns.
- `ml.macro_indicator_daily`
  Daily macro inputs such as Treasury series when loaded.

The `ml.market_data_15m` table is the core training and inference feature store.

## Backend Responsibilities

The backend is responsible for:

- market data access
- engineered feature preparation
- training job status endpoints
- inference endpoints
- simulation/replay endpoints
- snapshot and export endpoints

Relevant backend areas:

- `backend/app/modules/market`
- `backend/app/modules/inference`
- `backend/app/modules/training`
- `backend/app/modules/simulation`
- `backend/app/modules/data`

## Frontend Responsibilities

The active frontend is Streamlit:

- `frontend_streamlit/app.py`
- `frontend_streamlit/api.py`

It provides:

- stock browsing
- OHLC chart views
- prediction overlays
- simulation playback
- training/snapshot workflow views

## Local URLs

When the local stack is running:

- Streamlit: `http://localhost:8501`
- Backend API: `http://localhost:8000`
- Swagger docs: `http://localhost:8000/docs`
- Adminer: `http://localhost:8082`

## Docker

Start the local stack:

```bash
docker compose up -d --build
```

The compose stack includes:

- `db`
- `adminer`
- `prestart`
- `backend`
- `streamlit`

The old React frontend has been removed from the active Docker stack.

## Streamlit Local Development

Run Streamlit without Docker:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r frontend_streamlit/requirements.txt
API_BASE_URL=http://localhost:8000/api/v1 streamlit run frontend_streamlit/app.py
```

## Backend Local Development

```bash
cd backend
uv sync
uv run alembic upgrade head
uv run fastapi dev app/main.py --host 0.0.0.0 --port 8000
```

## Data Loading

The market data loaders live under `ml/scripts/`.

Important scripts:

- `ml/scripts/refetch_market_data_15m_quality.py`
- `ml/scripts/backfill_market_data_15m_from_fmp.py`
- `ml/scripts/fetch_raw_market_vendor_dataset.py`

The current bulk-loading workflow uses a resumable `simple-fmp` mode that:

- fetches FMP intraday data in larger chunks
- writes each symbol directly to Postgres
- recomputes features per committed symbol
- stores progress in `ml/data/quality_refetch_reports/simple_fmp_checkpoint.json`

## Project Structure

```text
the-project-maverick/
├── backend/                 # FastAPI application
├── frontend_streamlit/      # Active Streamlit frontend
├── ml/                      # Data and ML scripts
├── model_artifacts/         # Saved model bundles
├── docker/                  # Container definitions
├── docker-compose.yml       # Main local stack
└── Documentation/           # Supporting project docs
```

## Notes

- Historical course/project documents in `Documentation/` may describe earlier implementation phases.
- The active runtime stack is Postgres + FastAPI + Streamlit.
