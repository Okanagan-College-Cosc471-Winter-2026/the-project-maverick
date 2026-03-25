# Product Packaging

**Organization:** Okanagan College
**Course:** COSC 471 - Software Engineering (Winter 2026)
**Project:** the-project-maverick

---

## Packaging Strategy

The Stock Market Prediction Platform is delivered as a digital package. All components are containerized and can be deployed via a single `docker-compose up` command.

## 1. Delivery Format

**Primary:** Git repository hosted on GitHub
**Secondary:** ZIP archive for offline distribution

**Filename Convention:** `the-project-maverick_v1.0.0.zip`

## 2. Package Contents

| Directory | Contents |
|-----------|----------|
| `backend/` | Python FastAPI application with XGBoost inference engine |
| `frontend/` | React 19 + Vite + TypeScript dashboard application |
| `frontend_streamlit/` | Alternative Streamlit frontend for data exploration |
| `ml/` | Machine learning notebooks, training scripts, and utilities |
| `model_artifacts/` | Pre-trained XGBoost model files (26 horizon models + metadata) |
| `airflow/` | Airflow DAG definitions for automated workflows |
| `docker/` | Nginx and proxy configuration files |
| `scripts/` | Setup and management shell scripts |
| `docs/` | Complete project documentation in Markdown format |
| `docker-compose.yml` | Multi-service orchestration configuration |
| `.env.example` | Template for environment variable configuration |
| `README.md` | Project overview and quick start instructions |

## 3. Deployment

To deploy the complete application from the package:

```bash
# 1. Extract or clone
unzip the-project-maverick_v1.0.0.zip
cd the-project-maverick

# 2. Configure environment
cp .env.example .env
# Edit .env with your database password and FMP API key

# 3. Launch all services
docker-compose up -d --build
```

All services (database, backend, frontend) start automatically and are accessible via the browser.

## 4. System Requirements

| Requirement | Minimum |
|-------------|---------|
| RAM | 4 GB |
| Disk Space | 5 GB (including Docker images) |
| Docker | Version 20.0+ |
| Docker Compose | Version 2.0+ |
| Network | Internet access for FMP API data |
