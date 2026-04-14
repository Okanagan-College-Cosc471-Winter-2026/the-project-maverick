# Project Maverick

An end-to-end algorithmic trading intelligence platform: intraday market data → feature store → XGBoost training on HPC → live inference and simulation replay, served through a FastAPI backend and Streamlit dashboard.

**Demo:** [Loom walkthrough](https://www.loom.com/share/07f7584445dd41d389e720bd053ae7ea)

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        LOCAL DOCKER STACK                           │
│                                                                     │
│  ┌──────────┐    ┌──────────┐    ┌──────────────────────────────┐  │
│  │Streamlit │───▶│ FastAPI  │───▶│        PostgreSQL 16         │  │
│  │:8501     │    │ Backend  │    │                              │  │
│  └──────────┘    │ :8000    │    │  ml.market_data_15m          │  │
│                  └──────────┘    │  ml.macro_indicator_daily    │  │
│  ┌──────────┐         │          └──────────────────────────────┘  │
│  │ Airflow  │         │ model_artifacts/                           │
│  │Scheduler │         │  current_base/                             │
│  │:8081     │         │  current_simulation/                       │
│  └────┬─────┘         └──────────────────────────────────────────  │
│       │                                                             │
└───────┼─────────────────────────────────────────────────────────────┘
        │ SSH (ControlMaster socket, Duo MFA)
        ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   NIBI HPC (Alliance Canada / SHARCNET)             │
│                                                                     │
│   Slurm GPU queue (gpubase_b, H100)                                 │
│   ├── simulate_full_day.sbatch                                      │
│   │     • base model training  (XGBoost, 500+ symbols)             │
│   │     • warm simulation      (25 × 15-min prediction horizons)   │
│   └── artifacts rsync'd back → model_artifacts/                    │
└─────────────────────────────────────────────────────────────────────┘
```

### Data Flow

```
FMP API (intraday)
      │
      ▼
ml/scripts/fetch_new_date.py          ← manual one-off fetch
ml/scripts/backfill_market_data_15m_from_fmp.py  ← bulk/resume backfill
      │
      ▼  upsert + feature engineering
ml.market_data_15m  (PostgreSQL)
  • OHLCV bars (15-min, regular session)
  • lag features, SMAs, volatility, momentum
      │
      ├──▶ export_parquet ──▶ rsync to NIBI ──▶ XGBoost training
      │                                               │
      │                                        model artifacts
      │                                               │
      │                                        rsync back ──▶ model_artifacts/
      │                                                              │
      └──▶ FastAPI inference/simulation endpoints ◀─────────────────┘
                      │
                      ▼
              Streamlit dashboard
```

---

## Services

| Service | Port | Description |
|---------|------|-------------|
| `db` | 5432 | PostgreSQL 16 — feature store and app DB |
| `backend` | 8000 | FastAPI — inference, simulation, market data, ops |
| `streamlit` | 8501 | Streamlit — dashboard UI |
| `airflow-webserver` | 8081 | Airflow UI |
| `airflow-scheduler` | — | DAG scheduler (LocalExecutor) |
| `adminer` | 8082 | DB admin UI |
| `prestart` | — | One-shot: Alembic migrations + seed data |

---

## Repository Layout

```
the-project-maverick/
├── backend/
│   └── app/
│       ├── modules/
│       │   ├── market/        # stock list, OHLCV endpoints
│       │   ├── inference/     # live prediction endpoints + model loader
│       │   ├── simulation/    # replay/backtest endpoints
│       │   ├── training/      # training job status
│       │   ├── data/          # snapshot export
│       │   └── ops/           # pipeline status, SSH health, usage meter
│       ├── core/              # config, DB engine, auth
│       └── alembic/           # DB migrations
│
├── frontend_streamlit/
│   ├── app.py                 # Streamlit entrypoint (all pages)
│   └── api.py                 # typed client for backend API
│
├── ml/
│   ├── XG_boost_3_multigpu_final.py   # main training + simulation script
│   ├── scripts/
│   │   ├── backfill_market_data_15m_from_fmp.py   # bulk backfill (resumable)
│   │   ├── fetch_new_date.py                       # fetch a single new trading date
│   │   ├── refetch_market_data_15m_quality.py      # quality-focused re-fetch
│   │   └── init-db.sh                              # DB init script
│   └── nibi/
│       └── simulate_full_day.sbatch   # Slurm GPU job definition
│
├── airflow/
│   └── dags/                  # local Maverick DAGs (snapshots, retraining)
│
├── docker/
│   ├── backend/Dockerfile
│   ├── streamlit/Dockerfile
│   └── airflow/Dockerfile     # apache/airflow:2.9.3 + openssh + pip deps
│
├── model_artifacts/
│   ├── base_YYYY-MM-DD/       # XGBoost base model bundle
│   ├── simulation_YYYY-MM-DD/ # per-horizon simulation models (25+ steps)
│   ├── current_base -> ...    # symlink to active base model
│   └── current_simulation ->  # symlink to active simulation models
│
├── Documentation/             # project docs, DB inventory, user manual
├── docker-compose.yml
├── deployment.md
└── development.md
```

---

## Training Pipeline (Airflow DAG: `nibi_daily_warm_refresh`)

The main pipeline lives in the **Algo-trade-monorepo** Airflow DAGs folder and is mounted into the Airflow containers. It runs Mon–Fri at 10:00 UTC.

```
ssh_health_check
      │
      ├── check_nibi_libraries   (parallel)
      ├── sync_code_to_nibi      (parallel)
      ├── export_parquet         (parallel)
      └── sync_base_model        (parallel)
                    │
            sync_parquet_to_nibi
                    │
            clean_nibi_run_root
                    │
            submit_slurm_job          ← sbatch on NIBI H100
                    │
            poll_job_until_done       ← NibiJobSensor (reschedule mode)
                    │
            validate_artifacts
                    │
            rsync_artifacts_back
                    │
            promote_model             ← updates current_base / current_simulation symlinks
                    │
            reload_backend            ← POST /api/v1/inference/reload
```

**Runtime Airflow Variables:**

| Variable | Default | Effect |
|----------|---------|--------|
| `nibi_skip_base` | `false` | Skip base model training; use existing |
| `nibi_base_model_dir` | `current_base` | Override base model path to sync |

---

## NIBI HPC Access

SSH uses a **ControlMaster socket** to reuse a single Duo-authenticated session across all pipeline tasks. The socket lives at `~/.ssh/cm/nibi-harshsaw@nibi.sharcnet.ca:22`.

Before triggering a DAG run, ensure the socket is active:

```bash
ssh -M -o "ControlPath=~/.ssh/cm/nibi-harshsaw@nibi.sharcnet.ca:22" \
    -o "ControlPersist=8h" \
    -i ~/.ssh/nibi_key \
    harshsaw@nibi.sharcnet.ca

# Verify it works:
ssh -o "ControlPath=~/.ssh/cm/nibi-harshsaw@nibi.sharcnet.ca:22" \
    -o "ControlMaster=no" -o "BatchMode=yes" \
    -i ~/.ssh/nibi_key harshsaw@nibi.sharcnet.ca "echo ok"
```

The Airflow containers run as **uid 1000** (matching the host `ubuntu` user) so they can connect to the ControlMaster socket via `SO_PEERCRED`.

A cron job keeps permissions correct:

```
*/1 * * * * chmod 660 /home/ubuntu/.ssh/cm/nibi-* 2>/dev/null || true
```

---

## Stack

| Layer | Technology |
|-------|-----------|
| Database | PostgreSQL 16 |
| Backend | FastAPI, SQLModel, Alembic, psycopg |
| ML | XGBoost ≥ 2.0, pandas ≥ 2.0, scikit-learn ≥ 1.4 |
| Frontend | Streamlit |
| Orchestration | Apache Airflow 2.9.3 (LocalExecutor) |
| HPC | Slurm + H100 GPU (Alliance Canada / NIBI) |
| Market Data | FMP (Financial Modeling Prep) API |
| Containers | Docker Compose |

---

## Quick Start

```bash
# 1. Copy and fill environment variables
cp .env.example .env

# 2. Start the full stack
docker compose up -d --build

# 3. Open the dashboard
open http://localhost:8501

# Airflow UI
open http://localhost:8081   # admin / admin

# Swagger docs
open http://localhost:8000/docs
```

### Load historical market data

```bash
# Fetch a specific date (e.g. when adding a new trading day)
python ml/scripts/fetch_new_date.py --date 2026-04-08

# Bulk backfill (resumable)
python ml/scripts/backfill_market_data_15m_from_fmp.py
```

### Trigger a training run manually

```bash
# Ensure NIBI ControlMaster socket is active first (see above)
docker compose exec airflow-scheduler \
  airflow dags trigger nibi_daily_warm_refresh \
  --conf '{"trade_date": "2026-04-08"}'
```

---

## Key Data Tables

| Table | Description |
|-------|-------------|
| `ml.market_data_15m` | Core feature store: 15-min OHLCV bars + engineered features (lags, SMAs, volatility, momentum) for 500+ symbols |
| `ml.macro_indicator_daily` | Daily macro inputs (Treasury series, etc.) |

---

## Local Development

**Backend:**

```bash
cd backend
uv sync
uv run alembic upgrade head
uv run fastapi dev app/main.py --host 0.0.0.0 --port 8000
```

**Streamlit:**

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r frontend_streamlit/requirements.txt
API_BASE_URL=http://localhost:8000/api/v1 streamlit run frontend_streamlit/app.py
```

---

## Further Reading

- [`ml/README.md`](./ml/README.md) — ML pipeline details and mermaid flowchart
- [`ml/SIMULATION_APRIL7.md`](./ml/SIMULATION_APRIL7.md) — April 7 replay workstream notes
- [`Documentation/Current_Database_Inventory.md`](./Documentation/Current_Database_Inventory.md) — DB schema reference
- [`deployment.md`](./deployment.md) — Production deployment (Traefik, CI/CD)
- [`development.md`](./development.md) — Extended local dev guide
