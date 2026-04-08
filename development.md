# Development Guide

## Local Stack

Start the local services with Docker:

```bash
docker compose up -d --build
```

Main local URLs:

- Streamlit: `http://localhost:8501`
- Backend: `http://localhost:8000`
- Swagger: `http://localhost:8000/docs`
- Adminer: `http://localhost:8082`

## Services

The active Docker stack includes:

- `db`
- `adminer`
- `prestart`
- `backend`
- `streamlit`

The old React frontend is no longer part of the active development stack.

## Logs

View all logs:

```bash
docker compose logs -f
```

View one service:

```bash
docker compose logs -f backend
docker compose logs -f streamlit
```

## Backend Local Development

```bash
cd backend
uv sync
uv run alembic upgrade head
uv run fastapi dev app/main.py --host 0.0.0.0 --port 8000
```

## Streamlit Local Development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r frontend_streamlit/requirements.txt
API_BASE_URL=http://localhost:8000/api/v1 streamlit run frontend_streamlit/app.py
```

## Database

Local Postgres settings are read from `.env`.

Important tables used by the current ML flow:

- `ml.market_data_15m`
- `ml.macro_indicator_daily`

## Data Loading Scripts

Primary scripts:

- `ml/scripts/refetch_market_data_15m_quality.py`
- `ml/scripts/backfill_market_data_15m_from_fmp.py`
- `ml/scripts/fetch_raw_market_vendor_dataset.py`

The resumable bulk load path is:

```bash
python -u ml/scripts/refetch_market_data_15m_quality.py --mode simple-fmp --start-date YYYY-MM-DD --end-date YYYY-MM-DD
```

Resume from checkpoint:

```bash
python -u ml/scripts/refetch_market_data_15m_quality.py --mode simple-fmp --start-date YYYY-MM-DD --end-date YYYY-MM-DD --resume-from-checkpoint
```

Checkpoint file:

- `ml/data/quality_refetch_reports/simple_fmp_checkpoint.json`

## Verification

Backend checks:

```bash
cd backend
uv run ruff check .
uv run mypy app
uv run pytest tests/ -v
```

Streamlit sanity check:

```bash
python -m py_compile frontend_streamlit/app.py frontend_streamlit/api.py
```
