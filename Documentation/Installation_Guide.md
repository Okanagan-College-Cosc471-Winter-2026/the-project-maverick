# Installation Guide

## Overview

The active system consists of:

- PostgreSQL for market data and engineered features
- FastAPI for backend APIs, inference, simulation, and training status
- Streamlit for the user interface

## Prerequisites

- Git
- Docker with Docker Compose
- Python 3.10+ for local non-Docker development

## Recommended Setup: Docker

Clone the repo:

```bash
git clone <repo-url>
cd the-project-maverick
```

Create `.env` if needed and set the required secrets:

```bash
cp .env.example .env
```

Start the stack:

```bash
docker compose up -d --build
```

Open:

- Streamlit: `http://localhost:8501`
- Backend docs: `http://localhost:8000/docs`
- Adminer: `http://localhost:8082`

## Local Backend Setup

```bash
cd backend
uv sync
uv run alembic upgrade head
uv run fastapi dev app/main.py --host 0.0.0.0 --port 8000
```

## Local Streamlit Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r frontend_streamlit/requirements.txt
API_BASE_URL=http://localhost:8000/api/v1 streamlit run frontend_streamlit/app.py
```

## Data Loading

Bulk-load intraday market data:

```bash
python -u ml/scripts/refetch_market_data_15m_quality.py --mode simple-fmp --start-date 2024-03-25 --end-date 2026-04-07
```

## Teardown

```bash
docker compose down
```
