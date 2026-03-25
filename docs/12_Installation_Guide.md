# Installation Guide

**Organization:** Okanagan College
**Course:** COSC 471 - Software Engineering (Winter 2026)
**Project:** the-project-maverick
**Version:** 1.0.0

---

## 1. Overview

The Project Maverick is a multi-service application consisting of:

- **React/Vite Frontend** - Interactive dashboard for viewing stock data and predictions
- **FastAPI Backend** - REST API with ML inference engine
- **PostgreSQL Database** - Market data and prediction storage
- **Adminer** - Optional database administration UI

The application supports two installation methods: Docker (recommended) or native local setup.

## 2. Prerequisites

Ensure the following tools are installed on your machine:

| Tool | Version | Required For |
|------|---------|-------------|
| Git | Any recent version | Cloning the repository |
| Docker and Docker Compose | 20.0+ | Method A (Recommended) |
| Node.js and npm | 20.x+ | Method B (Local frontend) |
| Python and uv | 3.10+ | Method B (Local backend) |

## 3. Method A: Docker Installation (Recommended)

This method runs the entire stack in containers without installing local dependencies.

### Step 1: Clone the Repository

```bash
git clone https://github.com/Okanagan-College-Cosc471-Winter-2026/the-project-maverick.git
cd the-project-maverick
```

### Step 2: Configure Environment Variables

Copy the environment template and edit it with your credentials:

```bash
cp .env.example .env
```

Open `.env` in any text editor and set the following values:

| Variable | Description | Example |
|----------|------------|---------|
| `POSTGRES_PASSWORD` | Database password | `your_secure_password` |
| `FMP_API_KEY` | Financial Modeling Prep API key | `your_fmp_key` |
| `POSTGRES_SERVER` | Database host (use `db` for Docker) | `db` |

### Step 3: Build and Start Services

```bash
docker-compose up -d --build
```

The first build takes 2-5 minutes to download dependencies and build the ML inference image.

### Step 4: Verify Services

Open your browser and navigate to:

| Service | URL |
|---------|-----|
| Frontend Dashboard | http://localhost:5173 |
| Backend API Docs (Swagger) | http://localhost:8000/docs |
| Adminer (DB Admin) | http://localhost:8080 |

## 4. Method B: Native Local Installation (Developers)

Use this method if you need to modify code with faster feedback loops than Docker volumes provide.

### Backend Setup

```bash
cd backend

# Install the uv package manager (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install Python dependencies
uv sync

# Run database migrations
uv run alembic upgrade head

# Start the API server with auto-reload
uv run fastapi dev app/main.py --host 0.0.0.0 --port 8000
```

### Frontend Setup

Open a separate terminal:

```bash
cd frontend

# Install Node.js dependencies
npm install

# Start the Vite development server
npm run dev
```

The frontend will be available at http://localhost:5173.

### Database Setup

You need a running PostgreSQL 16 instance. Either:

- Use Docker for just the database: `docker-compose up -d db`
- Or install PostgreSQL locally and create a database named `app`

Update the `.env` file with your database connection details.

## 5. Configuration

### Environment Variables Reference

| Variable | Default | Description |
|----------|---------|-------------|
| `POSTGRES_USER` | `postgres` | Database username |
| `POSTGRES_PASSWORD` | `changethis` | Database password |
| `POSTGRES_DB` | `app` | Database name |
| `POSTGRES_SERVER` | `db` | Database host |
| `POSTGRES_PORT` | `5432` | Database port |
| `FMP_API_KEY` | (none) | Financial Modeling Prep API key |
| `ACTIVE_MODEL` | `nextday_15m_path_final` | Which model to use for inference |

## 6. Verifying the Installation

After starting all services, verify the installation:

1. Open http://localhost:8000/docs - you should see the Swagger API documentation.
2. Open http://localhost:5173 - you should see the dashboard with the stock list sidebar.
3. Try the prediction endpoint: `GET http://localhost:8000/api/v1/inference/predict/AAPL`

## 7. Teardown

### Docker

To stop all services:

```bash
docker-compose down
```

To stop and remove all data volumes (resets the database):

```bash
docker-compose down -v
```

### Native

Stop the backend and frontend processes with `Ctrl+C` in their respective terminals.

## 8. Read Me

For additional development information, see:

- `README.md` - Project overview and quick start
- `development.md` - Development workflow and code quality tools
- `deployment.md` - Production deployment guide
