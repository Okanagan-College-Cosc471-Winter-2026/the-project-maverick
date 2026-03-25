# Individual Project Reports and Workload Information

**Organization:** Okanagan College
**Course:** COSC 471 - Software Engineering (Winter 2026)
**Project:** the-project-maverick
**Year:** 2026

---

## 1. Dante Bertolutti

**Role:** Project Lead / Full-Stack Developer
**Total Hours:** 98

| Task | Description | Hours | Status |
|------|------------|-------|--------|
| Project Coordination | Led sprint planning sessions, managed GitHub project board, and coordinated cross-team dependencies | 12 | Completed |
| Full-Stack Integration | Connected frontend dashboard to backend inference and market data APIs, resolved type mismatches | 20 | Completed |
| Schema Migration | Migrated market data queries to new database schemas and standardized inference endpoints | 18 | Completed |
| Testing and QA | Built prediction confidence display, aligned frontend types with backend schemas, wrote integration tests | 16 | Completed |
| Security Fixes | Identified and fixed SQL injection vulnerability in data snapshot API by parameterizing date queries | 8 | Completed |
| Code Reviews | Reviewed 12 pull requests, provided architectural feedback, and enforced coding standards | 14 | Completed |
| Documentation | Consolidated and rewrote all project documentation for final submission | 10 | Completed |

---

## 2. Harsh Kumar

**Role:** Lead Backend Developer / ML Engineer
**Total Hours:** 113

| Task | Description | Hours | Status |
|------|------------|-------|--------|
| ML Pipeline | Developed end-to-end XGBoost training pipeline with Optuna hyperparameter optimization | 25 | Completed |
| Feature Engineering | Built technical indicator calculation module (RSI, MACD, Bollinger Bands, ATR, OBV) with 53 features | 18 | Completed |
| Model Training | Trained and validated next-day 15-minute path prediction model across 26 horizons for 29 stocks | 20 | Completed |
| DRAC Integration | Set up training scripts and batch jobs for execution on the Digital Research Alliance cluster | 12 | Completed |
| Backend Core | Set up `uv` workspace, integrated GitHub Actions, configured Ruff and Mypy | 10 | Completed |
| Data Engineering | Built FMP data fetching pipeline, gap-filling scripts, and data synchronization tools | 16 | Completed |
| Code Reviews | Reviewed pull requests and guided architectural decisions | 12 | Completed |

---

## 3. Parag Jindal

**Role:** Backend Developer / Scrum Master
**Total Hours:** 83

| Task | Description | Hours | Status |
|------|------------|-------|--------|
| API Development | Engineered prediction and market data API controllers with Pydantic v2 validation | 18 | Completed |
| Schema Design | Designed and implemented Pydantic response models for inference, market, and training endpoints | 12 | Completed |
| Sprint Management | Led sprint planning, daily standups, and retrospective meetings as Scrum Master | 15 | Completed |
| WebSocket Research | Researched and prototyped Starlette WebSocket streaming for live updates | 10 | In Progress |
| Database Configuration | Configured Alembic migrations and database connection settings across environments | 12 | Completed |
| Airflow Integration | Set up Airflow DAGs for daily dataset snapshots and training orchestration | 10 | Completed |
| Testing | Wrote unit tests for API endpoints and schema validation | 6 | Completed |

---

## 4. Kaval S

**Role:** Frontend Lead / Architecture
**Total Hours:** 93

| Task | Description | Hours | Status |
|------|------------|-------|--------|
| Dashboard Architecture | Scaffolded Vite + React 19 environment with TypeScript strict mode and Biome linting | 10 | Completed |
| State Management | Implemented TanStack Query data caching layers for efficient API polling | 18 | Completed |
| UI/UX Design | Designed Tailwind CSS templates with Radix UI component library for consistent styling | 15 | Completed |
| Stock Detail Page | Built the stock detail view with interactive price charts and symbol navigation | 16 | Completed |
| Sidebar Navigation | Implemented app sidebar with stock list and navigation routing via TanStack Router | 12 | Completed |
| API Client Generation | Set up OpenAPI client generation to keep frontend types in sync with backend schemas | 10 | Completed |
| Branch Management | Coordinated feature branch merging and resolved merge conflicts | 12 | Completed |

---

## 5. Guntash Brar

**Role:** Frontend Developer / Visualization Specialist
**Total Hours:** 90

| Task | Description | Hours | Status |
|------|------------|-------|--------|
| Chart Implementation | Built interactive stock price charts using Recharts and Lightweight Charts with zoom and tooltips | 22 | Completed |
| Prediction Visualization | Implemented dashed-line prediction overlays and confidence interval shading on charts | 14 | Completed |
| Training Dashboard | Built the training monitor page with job status polling, log streaming, and controls | 16 | Completed |
| Streamlit Frontend | Developed alternative Streamlit frontend for data exploration and inference testing | 18 | Completed |
| Component Library | Created reusable UI components (loading spinners, error states, data tables) | 10 | Completed |
| Sprint Retrospectives | Documented sprint retrospective notes and process improvement suggestions | 6 | Completed |
| Manual Testing | Performed cross-browser UI testing and reported visual bugs | 4 | Completed |

---

## 6. Zane Tessmer (Foochini)

**Role:** DevOps and QA Engineer
**Total Hours:** 101

| Task | Description | Hours | Status |
|------|------------|-------|--------|
| Docker Configuration | Built and maintained `docker-compose.yml` linking all services (Frontend, Backend, PostgreSQL, Adminer) | 16 | Completed |
| CI/CD Pipeline | Configured GitHub Actions workflows for automated testing, linting, and type checking on PRs | 14 | Completed |
| Test Suite | Built Pytest test suite with mock database sessions, achieving 81% code coverage | 22 | Completed |
| Data API Development | Developed the data snapshot build, list, and download endpoints | 14 | Completed |
| Nginx Configuration | Set up Nginx reverse proxy and database proxy configurations for production deployment | 10 | Completed |
| Documentation | Co-authored configuration management documentation and README overviews | 12 | Completed |
| Server Setup | Wrote server setup documentation and management scripts for VPS deployment | 8 | Completed |
| Database Admin | Managed database schema validation and Alembic migration consistency | 5 | Completed |
