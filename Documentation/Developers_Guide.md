# Developer Guide

## Architecture

The current runtime architecture has three active layers:

1. Data layer
   PostgreSQL stores historical market bars and engineered feature data.
2. Backend layer
   FastAPI serves market, inference, simulation, training, and data endpoints.
3. Frontend layer
   Streamlit consumes backend APIs and renders charts, predictions, and simulations.

## Main Backend Modules

- `backend/app/modules/market`
  Market listings, OHLC retrieval, and feature-store access.
- `backend/app/modules/inference`
  Loads model bundles and produces predictions from engineered features.
- `backend/app/modules/simulation`
  Replay and warm-refresh simulation endpoints.
- `backend/app/modules/training`
  Training status and log streaming endpoints.
- `backend/app/modules/data`
  Snapshot building and download endpoints.

## Main Frontend Files

- `frontend_streamlit/app.py`
  Main Streamlit app and UI flow.
- `frontend_streamlit/api.py`
  Thin HTTP client for backend API calls.

## Main ML/Data Scripts

- `ml/scripts/refetch_market_data_15m_quality.py`
  Bulk refetch loader with quality and simple-FMP modes.
- `ml/scripts/backfill_market_data_15m_from_fmp.py`
  Targeted repair/backfill helper.
- `ml/scripts/fetch_raw_market_vendor_dataset.py`
  Vendor dataset fetch helper.

## Important Tables

- `ml.market_data_15m`
  15-minute bars plus engineered ML features.
- `ml.macro_indicator_daily`
  Daily macro indicators.

## End-to-End Flow

1. Market data is fetched and written into Postgres.
2. Engineered features are computed and stored with the market rows.
3. Training jobs build model artifacts from warehouse data.
4. Inference endpoints load saved artifacts and score fresh features.
5. Streamlit displays predictions, history, and simulation charts.

## Development Notes

- The old React frontend has been removed from the active stack.
- Streamlit is now the only supported UI path in Docker.
- The resumable `simple-fmp` loader writes each symbol directly to Postgres and checkpoints progress after each commit.
