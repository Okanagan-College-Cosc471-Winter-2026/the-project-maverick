---
pdf_options:
  format: Letter
  margin: 22mm
  headerTemplate: '<div style="font-size:8px;width:100%;text-align:center;color:#888;">MarketSight - Installation Guide</div>'
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
  code { background: #eef3f7; padding: 1px 5px; border-radius: 3px; font-size: 11px; }
  pre code { background: none; }
---

<div class="cover">

# MarketSight

## Stock Market Prediction System

<div class="line"></div>

## Installation Guide

**Prepared by:** Zane Tessmer

COSC 471 - Winter 2026 | Okanagan College

March 17, 2026

</div>

<div style="page-break-after: always;"></div>

# 1. System Requirements

## 1.1 Hardware Requirements

| Component | Minimum | Recommended |
|---|---|---|
| CPU | 2 cores | 4+ cores |
| RAM | 4 GB | 8+ GB |
| Disk Space | 10 GB | 20+ GB |
| GPU | Not required for inference | NVIDIA GPU for model training |

## 1.2 Software Requirements

| Software | Version | Purpose |
|---|---|---|
| **Docker** | 24.0+ | Container runtime |
| **Docker Compose** | v2.20+ | Multi-container orchestration |
| **Git** | 2.40+ | Source code management |
| **Web Browser** | Chrome/Firefox/Edge (latest) | Accessing the application |

## 1.3 Optional (for development without Docker)

| Software | Version | Purpose |
|---|---|---|
| Python | 3.12 | Backend development |
| Node.js | 20+ (or Bun) | Frontend development |
| PostgreSQL | 16 | Database |
| uv | Latest | Python package manager |

<div style="page-break-after: always;"></div>

# 2. Installation (Docker - Recommended)

## Step 1: Clone the Repository

```bash
git clone https://github.com/Okanagan-College-Cosc471-Winter-2026/the-project-maverick.git
cd the-project-maverick
```

## Step 2: Configure Environment Variables

Copy the example environment file and edit it:

```bash
cp .env.example .env
```

Edit `.env` with your settings. The key variables are:

| Variable | Description | Example |
|---|---|---|
| `POSTGRES_USER` | Database username | `marketsight` |
| `POSTGRES_PASSWORD` | Database password | `your_password` |
| `POSTGRES_DB` | Database name | `marketsight` |
| `POSTGRES_HOST` | Database host | `postgres` (Docker) or `localhost` |
| `POSTGRES_PORT` | Database port | `5432` |
| `FMP_API_KEY` | Financial Modeling Prep API key | `your_fmp_key` |
| `SECRET_KEY` | Application secret key | `your_secret_key` |

## Step 3: Build and Start All Services

```bash
docker compose up --build
```

This will start the following services:

| Service | Port | URL |
|---|---|---|
| Frontend (React) | 5173 | `http://localhost:5173` |
| Backend (FastAPI) | 8000 | `http://localhost:8000` |
| API Documentation | 8000 | `http://localhost:8000/docs` |
| PostgreSQL | 5432 | `localhost:5432` |
| Nginx | 80/443 | `http://localhost` |
| Airflow Webserver | 8080 | `http://localhost:8080` |
| Streamlit | 8501 | `http://localhost:8501` |

## Step 4: Verify Installation

1. Open `http://localhost:5173` in your browser - you should see the MarketSight welcome page
2. Open `http://localhost:8000/docs` - you should see the Swagger API documentation
3. Click "Start exploring" on the welcome page to access the dashboard

## Step 5: Seed Market Data (First Run)

On the first run, you need to seed the database with stock data. This can be done via:

**Option A: Airflow DAG**
1. Open `http://localhost:8080` (Airflow)
2. Trigger the `seed_market_data` DAG

**Option B: Manual Script**
```bash
docker compose exec backend python -m app.modules.market.seed
```

<div style="page-break-after: always;"></div>

# 3. Development Setup (Without Docker)

## 3.1 Backend Setup

```bash
# Install uv (Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Navigate to backend
cd backend

# Create virtual environment and install dependencies
uv sync

# Run database migrations
uv run alembic upgrade head

# Start the backend server
uv run fastapi dev app/main.py
```

## 3.2 Frontend Setup

```bash
# Navigate to frontend
cd frontend

# Install dependencies (using npm or bun)
npm install
# or
bun install

# Start the development server
npm run dev
# or
bun dev
```

## 3.3 Database Setup

```bash
# Start PostgreSQL (if not using Docker)
# Ensure PostgreSQL 16 is installed and running

# Create the database
createdb marketsight

# Run migrations
cd backend
uv run alembic upgrade head
```

<div style="page-break-after: always;"></div>

# 4. Configuration

## 4.1 Environment Variables Reference

| Variable | Required | Default | Description |
|---|---|---|---|
| `POSTGRES_USER` | Yes | - | Database username |
| `POSTGRES_PASSWORD` | Yes | - | Database password |
| `POSTGRES_DB` | Yes | `marketsight` | Database name |
| `POSTGRES_HOST` | Yes | `postgres` | Database host |
| `POSTGRES_PORT` | No | `5432` | Database port |
| `FMP_API_KEY` | Yes | - | FMP API key for market data |
| `SECRET_KEY` | Yes | - | Application secret key |
| `ENVIRONMENT` | No | `development` | `development` or `production` |
| `CORS_ORIGINS` | No | `*` | Allowed CORS origins |

## 4.2 Nginx Configuration

The Nginx reverse proxy is configured in `docker/nginx/nginx.conf`. In production, update:
- SSL certificate paths
- Server name
- Upstream backend URL

## 4.3 Airflow Configuration

Airflow DAGs are located in `airflow/dags/`. Key DAGs:
- `seed_market_data` - Daily market data seeding
- `retrain_model` - Weekly model retraining
- `snapshot_datasets` - Dataset snapshot creation

<div style="page-break-after: always;"></div>

# 5. Production Deployment (DRI Server)

For production deployment on the DRI server, refer to `docs_server_setup.md` in the project root. Key steps:

1. SSH into the DRI server
2. Clone the repository
3. Configure `.env` with production credentials
4. Run `docker compose up -d` for detached mode
5. Configure SSL certificates for Nginx
6. Use management scripts for service lifecycle:
   - Start services
   - Stop services
   - Restart services
   - Check status

# 6. Troubleshooting

| Issue | Solution |
|---|---|
| `docker compose up` fails | Ensure Docker Desktop is running and ports are not in use |
| Database connection refused | Check `POSTGRES_HOST` matches your setup (`postgres` for Docker, `localhost` otherwise) |
| Frontend shows blank page | Clear browser cache, ensure backend is running at correct port |
| `alembic upgrade head` fails | Ensure database exists and connection string is correct |
| FMP API errors | Verify your `FMP_API_KEY` is valid and not rate-limited |
| Model loading fails | Ensure model artifacts exist in `ml/models/` with `meta.json` |
| Airflow DAGs not visible | Check that `airflow/dags/` is mounted correctly in Docker Compose |
| Port already in use | Stop conflicting services or change ports in `.env` / `docker-compose.yml` |

# 7. Uninstallation

```bash
# Stop and remove all containers, networks, and volumes
docker compose down -v

# Remove the project directory
cd ..
rm -rf the-project-maverick
```
