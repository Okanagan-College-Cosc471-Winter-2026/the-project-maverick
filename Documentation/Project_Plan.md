# Project Plan

## Title Page
**Organization Name:** Okanagan College
**Course Name:** COSC 471
**Project Name:** the-project-maverick
**Year:** 2026

**Team Members:**
- Harsh kumar (Harshksaw)
- Parag Jindal (Paragjindal01)
- KavalS
- Guntash (guntash499)
- Foochini

---

## 1. Introduction
This Project Plan outlines the structural roadmap, workload distribution, and risk mitigation strategies required to successfully execute and deliver "the-project-maverick". The objective is to build a scalable Stock Market Prediction System utilizing XGBoost, React, FastAPI, and PostgreSQL.

## 2. Project Organization
The project follows Agile Scrum principles, utilizing two-week sprints.

**Roles:**
- **Scrum Master / Lead Backender:** Harsh kumar & Parag Jindal (FastAPI, Database, ML pipelines)
- **Frontend Lead / UI/UX:** KavalS & Guntash (React, Recharts, Streamlit prototyping)
- **DevOps & QA Engineer:** Foochini (Docker configuration, Pytest coverage, CI/CD, Documentation)

*Note: Roles are cross-functional; team members will assist outside their central roles as iteration demands dictate.*

## 3. Risk Analysis and Risk Mitigation Plan

| Risk ID | Risk Description | Probability | Impact | Mitigation Strategy |
|---|---|---|---|---|
| RSK-01 | **API Rate Limits:** Financial Data APIs throttle or block our IPs during mass historical polling. | High | High | Implement local caching, fallback mock data datasets, and rate limit tracking. |
| RSK-02 | **Model Stagnation:** The trained XGBoost model fails to predict accurately over long periods of time due to market shifts. | Med | High | Automate a pipeline for model retraining during cron-jobs, deploying newly versioned models without server restart. |
| RSK-03 | **Timeline Slippage:** Unforeseen asynchronous Python complexities delay backend completion. | Med | Med | Prioritize REST implementation first; push WebSocket latency integration to a lower priority "nice-to-have" status. |
| RSK-04 | **Database Overload:** Storing sub-second prediction data results in massive I/O bottlenecks or disk full errors. | Low | Critical | Optimize indexes or implement TimescaleDB integration to partition time-series polling data efficiently. |

## 4. Work Breakdown (WBS)
The work is divided into four major epics:

**Epic 1: Infrastructure & Scaffolding**
- Setup Git repositories, GitHub Actions (CI/CD workflows).
- Initialize Docker Compose networks (`docker-compose.yml`, `Dockerfile`).
- Configure Database schemas (`Alembic` initialization).

**Epic 2: Core Backend Engine**
- Build Financial API Polling worker.
- Construct Pandas DataFrame feature engineering (RSI, MACD).
- Integrate XGBoost Model singleton via `ModelManager`.
- Expose basic REST API (`fastapi dev`).

**Epic 3: Visualization & Client Interface**
- Scaffold React 19 Frontend using Vite + TypeScript.
- Build interactive StockChart using Recharts.
- Integrate user symbol selection and Axios/React-Query hooks.

**Epic 4: Finalization & Quality Assurance**
- Attain >80% Pytest code coverage.
- Prepare documentation endpoints, deployment manifests, and final project reports.

## 5. Project Schedule & Resource Allocation (Next Iteration)
**Sprint 3 Focus: Frontend-Backend Integration and Dashboard MVP**

| Task | Assignee | Est. Hours |
|---|---|---|
| Complete `poller.py` feature extraction pipeline | Harsh kumar | 8 |
| Configure Pydantic schemas for `/api/v1/predictions` | Parag Jindal | 5 |
| Create React components (`PriceChart.tsx`, `Dashboard.tsx`) | KavalS | 12 |
| Hook frontend charts to TanStack Query for live fetching | Guntash | 8 |
| Write initial test cases for `predictions.py` | Foochini | 10 |

## 6. Project Milestones

| Milestone | Target Date | Deliverable |
|---|---|---|
| **M1: Architecture Review** | Week 2 | Initial DB Schema, Dockerfiles operational, UML designs built. |
| **M2: Backend Beta** | Week 4 | Database fully mocked/seeded, API successfully predicting mock data, Swagger UI active. |
| **M3: Frontend Alpha** | Week 6 | MVP Dashboard interacting with backend, chart visually rendering predictions. |
| **M4: Production Ready** | Week 8 | Integration completely tested, Pytest coverage > 80%, all bugs patched. |
| **M5: Final Delivery** | Week 10 | Finalized Documentation, Demo scripts, and Academic Presentation. |

## 7. Gantt Chart (Diagram Representation)
*(Simplified text representation of project timeline flow)*
```text
[Week 01-02] ████████ M1: Scaffolding & Architecture
[Week 03-04]          ████████ M2: Backend & ML Engine
[Week 05-06]                   ████████ M3: Frontend & Dashboard
[Week 07-08]                            ████████ M4: Testing & Integration
[Week 09-10]                                     ████████ M5: Documentation & Final Polish
```

## 8. Monitoring and Reporting Mechanism
- **Daily Stand-ups:** Async standups via team messaging platform (Discord/Slack); 3 sentences outlining "What I did, What I will do, Blockers".
- **Sprint Retrospectives:** Bi-weekly 1-hour sessions to review burned-down tasks on GitHub Projects.
- **Issue Tracking:** GitHub Issues will be utilized for bug tracking, labeling (e.g., `bug`, `enhancement`), and assignment. Commits must reference issue IDs.
