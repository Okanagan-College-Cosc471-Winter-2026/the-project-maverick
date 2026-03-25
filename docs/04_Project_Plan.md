# Project Plan

**Organization:** Okanagan College
**Course:** COSC 471 - Software Engineering (Winter 2026)
**Project:** the-project-maverick
**Year:** 2026

**Team Members:**

- Dante Bertolutti
- Harsh Kumar
- Parag Jindal
- Kaval S
- Guntash Brar
- Zane Tessmer (Foochini)

---

## 1. Introduction

This Project Plan outlines the structural roadmap, workload distribution, and risk mitigation strategies required to successfully deliver "the-project-maverick." The objective is to build a scalable Stock Market Prediction System utilizing XGBoost, React, FastAPI, and PostgreSQL.

## 2. Project Organization

The project follows Agile Scrum principles, utilizing two-week sprints.

**Roles:**

| Team Member | Primary Role | Responsibilities |
|-------------|-------------|-----------------|
| Dante Bertolutti | Project Lead / Full-Stack Developer | Project coordination, full-stack integration, code reviews, testing, documentation |
| Harsh Kumar | Lead Backend Developer / ML Engineer | FastAPI core, XGBoost model training and integration, feature engineering pipelines |
| Parag Jindal | Backend Developer / Scrum Master | API endpoint development, Pydantic schemas, sprint planning, WebSocket research |
| Kaval S | Frontend Lead / Architecture | React dashboard scaffolding, TanStack Query integration, Tailwind UI design |
| Guntash Brar | Frontend Developer / Visualization | Recharts and Lightweight Charts implementation, UI components, interaction design |
| Zane Tessmer (Foochini) | DevOps and QA Engineer | Docker configuration, Pytest coverage, CI/CD pipelines, documentation, data API |

Roles are cross-functional; team members assist outside their central roles as iteration demands dictate.

## 3. Risk Analysis and Risk Mitigation Plan

| Risk ID | Risk Description | Probability | Impact | Mitigation Strategy |
|---------|-----------------|-------------|--------|-------------------|
| RSK-01 | API Rate Limits: Financial data APIs throttle or block requests during mass historical polling | High | High | Implement local caching, fallback data, and rate limit tracking |
| RSK-02 | Model Stagnation: The trained XGBoost model fails to predict accurately due to market shifts | Medium | High | Automate pipeline for model retraining via Airflow DAGs and DRAC integration |
| RSK-03 | Timeline Slippage: Unforeseen async Python complexities delay backend completion | Medium | Medium | Prioritize REST implementation first; push WebSocket to lower priority |
| RSK-04 | Database Overload: Storing high-frequency data results in I/O bottlenecks | Low | High | Optimize indexes and use raw SQL for performance-critical queries |
| RSK-05 | Environment Inconsistency: Different OS setups cause "works on my machine" errors | Medium | Medium | Mandate Docker Compose for development; use `uv` for reproducible Python environments |

## 4. Work Breakdown Structure

**Epic 1: Infrastructure and Scaffolding**

- Set up Git repository and GitHub Actions CI/CD workflows
- Initialize Docker Compose networks and service definitions
- Configure database schemas with Alembic migrations
- Set up `uv` workspace and coding standards (Ruff, Mypy, Biome)

**Epic 2: Core Backend Engine**

- Build financial API polling worker (FMP integration)
- Construct Pandas feature engineering pipeline (RSI, MACD, Bollinger Bands, ATR, OBV)
- Integrate XGBoost model inference with multi-horizon prediction support
- Expose REST API endpoints for market data, inference, training, and data snapshots

**Epic 3: Visualization and Client Interface**

- Scaffold React 19 frontend using Vite and TypeScript
- Build interactive stock chart using Recharts and Lightweight Charts
- Integrate symbol selection, sidebar navigation, and TanStack Query data fetching
- Build training dashboard for monitoring model training jobs

**Epic 4: ML Pipeline and Model Training**

- Develop data extraction and feature engineering scripts
- Build XGBoost model training pipeline with Optuna hyperparameter optimization
- Set up Airflow DAGs for automated daily training and data snapshots
- Integrate DRAC (Digital Research Alliance of Canada) for GPU-accelerated training

**Epic 5: Finalization and Quality Assurance**

- Achieve 80%+ Pytest code coverage
- Conduct integration testing across all API endpoints
- Prepare all project documentation and final deliverables
- Build Streamlit alternative frontend for data exploration

## 5. Project Schedule and Resource Allocation

| Sprint | Focus | Key Deliverables |
|--------|-------|-----------------|
| Sprint 1 (Weeks 1-2) | Infrastructure and scaffolding | Docker Compose, database schemas, CI/CD, project structure |
| Sprint 2 (Weeks 3-4) | Backend core and ML engine | API endpoints, feature engineering, XGBoost integration |
| Sprint 3 (Weeks 5-6) | Frontend dashboard MVP | React dashboard, stock charts, API integration |
| Sprint 4 (Weeks 7-8) | Testing and integration | Pytest coverage, end-to-end testing, bug fixes |
| Sprint 5 (Weeks 9-10) | Documentation and polish | Final documentation, Streamlit frontend, presentation prep |

## 6. Project Milestones

| Milestone | Target Date | Deliverable |
|-----------|------------|-------------|
| M1: Architecture Review | Week 2 | Database schema, Dockerfiles operational, UML designs |
| M2: Backend Beta | Week 4 | Database seeded, API predicting, Swagger UI active |
| M3: Frontend Alpha | Week 6 | MVP dashboard connected to backend, charts rendering predictions |
| M4: Production Ready | Week 8 | Integration tested, Pytest coverage above 80%, bugs patched |
| M5: Final Delivery | Week 10 | Finalized documentation, demo scripts, academic presentation |

## 7. Gantt Chart

```
Sprint 1 (Wk 1-2)  ████████  M1: Scaffolding & Architecture
Sprint 2 (Wk 3-4)           ████████  M2: Backend & ML Engine
Sprint 3 (Wk 5-6)                    ████████  M3: Frontend & Dashboard
Sprint 4 (Wk 7-8)                             ████████  M4: Testing & Integration
Sprint 5 (Wk 9-10)                                      ████████  M5: Docs & Final Polish
```

## 8. Monitoring and Reporting Mechanism

- **Daily Stand-ups:** Async standups via team messaging platform (Discord). Each member posts what they did, what they will do, and any blockers.
- **Sprint Retrospectives:** Bi-weekly sessions to review completed tasks on GitHub Projects board.
- **Issue Tracking:** GitHub Issues for bug tracking with labels (`bug`, `enhancement`, `change-request`). Commits reference issue IDs.
- **Pull Request Reviews:** All code changes go through PR review before merging to main. CI/CD runs automated tests on every PR.
