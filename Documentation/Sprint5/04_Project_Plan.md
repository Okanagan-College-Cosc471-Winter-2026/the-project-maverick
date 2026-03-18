---
pdf_options:
  format: Letter
  margin: 22mm
  headerTemplate: '<div style="font-size:8px;width:100%;text-align:center;color:#888;">MarketSight - Project Plan</div>'
  footerTemplate: '<div style="font-size:8px;width:100%;text-align:center;color:#888;"><span class="pageNumber"></span> / <span class="totalPages"></span></div>'
  displayHeaderFooter: true
stylesheet: https://cdnjs.cloudflare.com/ajax/libs/github-markdown-css/5.5.1/github-markdown.min.css
body_class: markdown-body
css: |-
  body { font-size: 11.5px; line-height: 1.65; }
  h1 { color: #1a5276; border-bottom: 2px solid #2980b9; padding-bottom: 6px; }
  h2 { color: #1a5276; border-bottom: 1px solid #bdc3c7; padding-bottom: 4px; margin-top: 18px; }
  h3 { color: #2c3e50; margin-top: 12px; }
  table { font-size: 10.5px; width: 100%; border-collapse: collapse; }
  th { background-color: #2980b9; color: white; padding: 5px 8px; }
  td { padding: 4px 8px; border: 1px solid #ddd; }
  tr:nth-child(even) { background-color: #f4f8fb; }
  .cover { text-align: center; margin-top: 80px; }
  .cover h1 { font-size: 32px; border: none; }
  .cover h2 { font-size: 16px; border: none; color: #7f8c8d; font-weight: 400; }
  .cover .line { border-top: 3px solid #2980b9; width: 100px; margin: 20px auto; }
---

<div class="cover">

# MarketSight

## Stock Market Prediction System

<div class="line"></div>

## Project Plan

**Prepared by:** Zane Tessmer (Scrum Master)

COSC 471 - Winter 2026 | Okanagan College

March 17, 2026

</div>

<div style="page-break-after: always;"></div>

## Table of Contents

1. Introduction
2. Project Organisation
3. Risk Analysis and Mitigation
4. Work Breakdown Structure
5. Project Schedule and Resource Allocation
6. Project Milestones
7. Gantt Chart
8. Monitoring and Reporting

<div style="page-break-after: always;"></div>

# 1. Introduction

## 1.1 Project Overview
MarketSight is a web-based stock market prediction platform developed for COSC 471 at Okanagan College. The system leverages machine learning (XGBoost with Optuna HPO) to predict stock prices using 53 technical indicators, presenting results through a React dashboard and Streamlit data explorer.

## 1.2 Project Objectives
- Deliver an end-to-end ML prediction pipeline from data ingestion to user interface
- Provide prediction confidence scores to help users assess forecast reliability
- Deploy to production infrastructure (DRI server) with automated pipelines
- Achieve Initial Operational Capability (IOC) by end of Sprint 5

## 1.3 Methodology
The project follows the **Agile Unified Process (AUP)** with Scrum ceremonies. Development is organized into 1-3 week sprints with XP pair programming. The team conducts sprint planning, daily standups, backlog grooming, sprint reviews, and retrospectives.

# 2. Project Organisation

## 2.1 Team Structure

| Role | Member | Responsibilities |
|---|---|---|
| **Scrum Master** | Zane Tessmer | Sprint ceremonies, documentation, coordination, impediment removal |
| **Product Owner** | Harsh Kumar | Backlog prioritization, architecture decisions, stakeholder communication |
| **Lead Developer** | Harsh Kumar | Backend, ML pipeline, infrastructure, DevOps |
| **Developer** | Dante Bertolutti | Confidence scoring, predictions UI, acceptance testing |
| **Developer** | Parag Jindal | Frontend routing, API client, type safety |
| **Developer** | Kaval S | User settings, dashboard optimization |
| **Developer** | Guntash | Dashboard cards, UI polish, accessibility |

## 2.2 XP Pairs by Sprint

### Sprint 3 (Jan 20 - Feb 9, 2026)
| Pair | Members | Focus |
|---|---|---|
| Pair 1 | Harsh & Parag | Backend API + Frontend scaffold |
| Pair 2 | Dante & Kaval | ML notebook + Database schema |
| Pair 3 | Guntash & Zane | CI/CD + Documentation |

### Sprint 4 (Feb 10 - Mar 3, 2026)
| Pair | Members | Focus |
|---|---|---|
| Pair 1 | Harsh & Dante | Inference API + Confidence scoring |
| Pair 2 | Parag & Guntash | Frontend routing + Dashboard cards |
| Pair 3 | Kaval & Zane | User settings + Documentation |

### Sprint 5 (Mar 4 - Mar 17, 2026)
| Pair | Members | Focus |
|---|---|---|
| Pair 1 | Harsh & Dante | ML pipeline integration + Confidence rebase |
| Pair 2 | Parag & Kaval | Frontend cleanup + Dashboard optimization |
| Pair 3 | Guntash & Zane | UI polish + Documentation + Testing |

<div style="page-break-after: always;"></div>

# 3. Risk Analysis and Mitigation

| ID | Risk | Probability | Impact | Severity | Mitigation Strategy | Owner |
|---|---|---|---|---|---|---|
| R-01 | Model accuracy insufficient for useful predictions | Medium | Medium | Medium | 53-feature pipeline, Optuna HPO, continuous tuning | Harsh |
| R-02 | No authentication exposes endpoints | Medium | High | High | CORS restriction now; JWT auth in backlog | Harsh |
| R-03 | DRI/DRAC server downtime | Low | High | Medium | Management scripts, monitoring, local fallback | Harsh |
| R-04 | FMP API rate limiting or outage | Low | Medium | Low | Chunked downloads, gap-filling scripts, cached data | Harsh |
| R-05 | Merge conflicts between major feature branches | Medium | Medium | Medium | Merge coordination meetings, branch protection | Zane |
| R-06 | Team member availability fluctuations | Medium | Medium | Medium | Cross-training via XP pairs, documented code | Zane |
| R-07 | Scope creep from stakeholder requests | Low | Medium | Low | Product backlog prioritization, sprint boundaries | Harsh |
| R-08 | Database growth exceeding storage | Low | Low | Low | Data retention policies, indexing, monitoring | Harsh |
| R-09 | Frontend/backend API contract mismatches | Medium | Low | Low | TypeScript types matching Pydantic schemas | Parag |
| R-10 | CI pipeline failures blocking merges | Low | Medium | Low | Fix-forward policy, parallel job execution | Harsh |

### Risk Severity Matrix

```
              Low Impact    Medium Impact    High Impact
High Prob     |             |                |
Medium Prob   | R-09        | R-01, R-05,    | R-02
              |             | R-06, R-07     |
Low Prob      | R-04, R-08  | R-03, R-08,    |
              |             | R-10           |
```

<div style="page-break-after: always;"></div>

# 4. Work Breakdown Structure

## 4.1 WBS Hierarchy

```
MarketSight
|
+-- 1. Backend
|   +-- 1.1 API Layer (routers, health check, dependency injection)
|   +-- 1.2 Market Module (stock models, CRUD, service, endpoints)
|   +-- 1.3 Inference Module (model loading, features, confidence, prediction API)
|   +-- 1.4 Training Module (training jobs API, log streaming)
|   +-- 1.5 Data Module (snapshot API: build, list, download)
|   +-- 1.6 Core (config, database, security)
|
+-- 2. Frontend (React)
|   +-- 2.1 Dashboard (summary cards, layout)
|   +-- 2.2 Stocks (list, search, detail, charts)
|   +-- 2.3 Predictions (selector, predict, batch, cards)
|   +-- 2.4 Training Monitor (log viewer, progress)
|   +-- 2.5 Admin (user management)
|   +-- 2.6 Settings (profile, password, account)
|   +-- 2.7 Services & Hooks (API clients, state management)
|
+-- 3. Frontend (Streamlit)
|   +-- 3.1 Market Data Explorer
|   +-- 3.2 Inference Testing
|   +-- 3.3 Dataset Management
|
+-- 4. ML Pipeline
|   +-- 4.1 Data Ingestion (FMP API, gap filling)
|   +-- 4.2 Feature Engineering (53 indicators)
|   +-- 4.3 Model Training (XGBoost, Optuna HPO)
|   +-- 4.4 Model Artifacts (native .ubj, meta.json)
|   +-- 4.5 DRAC Pipeline (end-to-end training)
|
+-- 5. Infrastructure
|   +-- 5.1 Docker Compose (all services)
|   +-- 5.2 Nginx (reverse proxy, SSL)
|   +-- 5.3 Airflow (DAGs: seed, retrain, snapshot)
|   +-- 5.4 CI/CD (GitHub Actions)
|   +-- 5.5 DRI Server (deployment, management scripts)
|
+-- 6. Testing
|   +-- 6.1 Backend Unit Tests
|   +-- 6.2 Backend Integration Tests
|   +-- 6.3 Acceptance Tests
|   +-- 6.4 CI Pipeline Validation
|
+-- 7. Documentation
    +-- 7.1 Sprint Ceremonies & Backlogs
    +-- 7.2 Technical Documentation
    +-- 7.3 User Support (Manual, Help, Installation)
    +-- 7.4 Developer's Guide
```

<div style="page-break-after: always;"></div>

# 5. Project Schedule and Resource Allocation

## 5.1 Sprint Schedule

| Sprint | Phase | Duration | Dates | Velocity |
|---|---|---|---|---|
| Sprint 3 | Construction 1 | 3 weeks | Jan 20 - Feb 9, 2026 | 30 pts |
| Sprint 4 | Construction 2 | 3 weeks | Feb 10 - Mar 3, 2026 | 73 pts |
| Sprint 5 | Construction 3 | 2 weeks | Mar 4 - Mar 17, 2026 | 62 pts |

## 5.2 Resource Allocation (Sprint 5 - Current)

| Team Member | Hours/Week | Sprint 5 Total | Stories | Points |
|---|---|---|---|---|
| Harsh Kumar | 25 hrs | 50 hrs | US-32 to US-38 | 36 |
| Dante Bertolutti | 15 hrs | 30 hrs | US-30, US-31, US-40 | 15 |
| Zane Tessmer | 12 hrs | 25 hrs | US-39, US-40 | 8 |
| Parag Jindal | 10 hrs | 20 hrs | US-41 | 3 |
| Kaval S | 7 hrs | 15 hrs | US-42 | 3 |
| Guntash | 7 hrs | 15 hrs | US-43 | 2 |
| **Total** | **76 hrs** | **155 hrs** | **14 stories** | **67 pts** |

## 5.3 Cumulative Story Points

| Sprint | Planned | Completed | Cumulative |
|---|---|---|---|
| Sprint 3 | 30 | 30 | 30 |
| Sprint 4 | 73 | 73 | 103 |
| Sprint 5 | 62 | 62 | 165 |

<div style="page-break-after: always;"></div>

# 6. Project Milestones

| Milestone | Date | Description | Status |
|---|---|---|---|
| **M1: Project Kickoff** | Jan 13, 2026 | Team formed, roles assigned, repo created | Achieved |
| **M2: Architecture Baseline** | Jan 20, 2026 | Tech stack selected, Docker env running | Achieved |
| **M3: Sprint 3 Complete** | Feb 9, 2026 | Core infrastructure, ML notebook, initial frontend | Achieved |
| **M4: Sprint 4 Complete** | Mar 3, 2026 | Inference API, confidence scoring, Airflow, FMP pipeline | Achieved |
| **M5: Sprint 5 Complete (IOC)** | Mar 17, 2026 | Production deployment, acceptance tests, client sign-off | Achieved |
| **M6: Final Submission** | Mar 18, 2026 | All deliverables submitted to Moodle | Pending |

# 7. Gantt Chart

```
Task                           Jan    Feb             Mar
                               W3 W4  W1 W2 W3 W4    W1 W2 W3
Sprint 3                       |======|======|======|
  Backend scaffold             |======|
  ML training notebook               |======|
  Frontend scaffold                   |======|
  CI/CD pipeline               |======|
  Docker environment           |======|

Sprint 4                                     |======|======|======|
  Inference API                              |======|
  Market module                              |======|
  FMP data integration                       |======|======|
  53-feature pipeline                               |======|
  Confidence scoring                                |======|
  Predictions page                                         |======|
  Airflow DAGs                               |======|
  Optuna HPO + DRAC                                 |======|======|
  Backend tests                              |======|

Sprint 5                                                          |======|======|
  Confidence rebase                                               |======|
  Predictions restore                                                    |======|
  Streamlit frontend                                              |======|
  DRI server migration                                            |======|======|
  Model format migration                                          |======|
  Feature eng refactor                                            |======|======|
  DW sync scripts                                                        |======|
  Documentation                                                   |======|======|
  Acceptance testing                                                     |======|
```

<div style="page-break-after: always;"></div>

# 8. Monitoring and Reporting

## 8.1 Scrum Ceremonies

| Ceremony | Frequency | Duration | Facilitator |
|---|---|---|---|
| Daily Standup | Daily (class days) | 15 min | Zane Tessmer |
| Sprint Planning | Start of sprint | 20 min | Zane Tessmer |
| Backlog Grooming | Mid-sprint | 20 min | Zane Tessmer |
| Sprint Review | End of sprint | 15 min | Zane Tessmer |
| Sprint Retrospective | End of sprint | 15 min | Zane Tessmer |

## 8.2 Reporting Mechanisms

| Report | Frequency | Audience | Format |
|---|---|---|---|
| Daily Scrum report | Per standup | Moodle submission | PDF (pair-based) |
| Sprint backlog burndown | Weekly | Team | Screenshot |
| Sprint review notes | End of sprint | Client + Professor | PDF |
| Performance schedule | Per sprint | Assistant Instructor | Email |
| Individual report | End of sprint | Moodle | PDF |

## 8.3 Issue Tracking

- **Platform:** GitHub Issues (labels: `ml-pipeline`, `frontend`, `testing`, `api`)
- **PR Reviews:** Required before merge to `main`
- **CI Dashboard:** GitHub Actions (6 jobs: lint, typecheck, test, lint, build, docker)

## 8.4 Communication Channels

| Channel | Purpose |
|---|---|
| GitHub Issues | Bug tracking, feature requests |
| GitHub Pull Requests | Code review, merge coordination |
| In-class meetings | Standup, sprint ceremonies |
| Direct messages | Urgent blockers, pair coordination |
