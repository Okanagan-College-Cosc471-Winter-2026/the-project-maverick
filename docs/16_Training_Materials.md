# Training Materials

**Organization:** Okanagan College
**Course:** COSC 471 - Software Engineering (Winter 2026)
**Project:** the-project-maverick
**Target Audience:** Onboarding Software Engineers and Support Staff

---

## 1. Training Outline

### Module 1: Architecture Overview (Day 1)

**Goal:** Understand the data flow from external financial APIs through the FastAPI backend, into PostgreSQL, through the XGBoost inference engine, and out to the React dashboard.

**Topics:**

- Three-tier architecture: Presentation, Application, and Data layers
- Docker Compose service topology (db, backend, frontend, adminer)
- API request lifecycle from frontend to database and back
- How the ML inference pipeline works (data fetch, feature engineering, prediction)

**Reference:** `docs/06_Developers_Guide.md`, `README.md`

### Module 2: Frontend Development (Day 2)

**Goal:** Understand the React frontend architecture, component structure, and data fetching patterns.

**Topics:**

- Vite + React 19 + TypeScript project structure
- TanStack Query for API data fetching and caching
- TanStack Router for page navigation
- Recharts and Lightweight Charts for data visualization
- Tailwind CSS and Radix UI for styling
- How to add a new dashboard page or chart component

**Reference:** `frontend/README.md`, `frontend/src/routes/dashboard/`

### Module 3: Backend and API Development (Day 3)

**Goal:** Understand the FastAPI backend structure, module organization, and how to add or modify endpoints.

**Topics:**

- FastAPI application structure and router registration
- Module organization (inference, market, data, training)
- SQLAlchemy 2.0 ORM and Alembic migrations
- Pydantic v2 for request/response validation
- Writing parameterized SQL queries to prevent injection

**Reference:** `backend/README.md`, `backend/app/modules/`

### Module 4: ML Model Operations (Day 4)

**Goal:** Understand how XGBoost models are trained, deployed, and used for inference.

**Topics:**

- Training pipeline: data extraction, feature engineering, Optuna HPO
- Model artifact structure (26 horizon models, metadata, manifest)
- How the ModelLoader singleton loads and caches models
- Feature engineering module: RSI, MACD, Bollinger Bands, ATR, OBV
- DRAC integration for GPU-accelerated training
- Airflow DAGs for automated retraining

**Reference:** `ml/README.md`, `backend/app/modules/inference/`

---

## 2. Presentation Slide Outline

**Slide 1:** Title - "Welcome to The Project Maverick - Developer Training"

**Slide 2:** Mission - What the prediction platform achieves and who it serves

**Slide 3:** Architecture Diagram - How Docker Compose orchestrates the three-tier stack

**Slide 4:** Database Design - The market schema with OHLCV data tables and prediction storage

**Slide 5:** ML Pipeline - From raw data to 26-horizon XGBoost predictions with confidence scores

**Slide 6:** Frontend Dashboard - Live demo of the React dashboard with chart interactions

**Slide 7:** Development Workflow - Git Flow branching, PR reviews, CI/CD pipeline, coding standards

**Slide 8:** Q&A and Troubleshooting Basics

---

## 3. Quick Reference Card

| Task | Command |
|------|---------|
| Start all services | `docker-compose up -d --build` |
| Stop all services | `docker-compose down` |
| Run backend locally | `cd backend && uv sync && uv run fastapi dev app/main.py` |
| Run frontend locally | `cd frontend && npm install && npm run dev` |
| Run backend tests | `cd backend && uv run pytest` |
| View API docs | Open `http://localhost:8000/docs` |
| View dashboard | Open `http://localhost:5173` |
| Check test coverage | `cd backend && uv run pytest --cov` |
