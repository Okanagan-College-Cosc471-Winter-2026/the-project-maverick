# Project Report by Scrum Master

## Title Page
**Organization Name:** Okanagan College
**Course Name:** COSC 471
**Project Name:** the-project-maverick
**Year:** 2026
**Scrum Masters / Managers:** Harsh kumar & Parag Jindal

---

## 1. Executive Summary
This document encapsulates the outcomes, structural metrics, and addressed risks associated with the recent iterations of the `the-project-maverick` Stock Market Prediction System. The primary goal of the evaluated sprint was establishing the core integration connecting the FastAPI backend, the XGBoost inference mechanism, and the React frontend dashboard.

## 2. Project Issues and Risk Management

Managing an asynchronous micro-service architecture required stringent technical and team-based issue tracking. We utilized a GitHub Board for transparent lifecycle tracking. 

### Resolved Issues (Iteration Assessment)
* **ISSUE-11 (Data Flow Blocking):** *Resolved.* The Pandas DataFrame transformation delayed API responses to 800ms. 
  * *Resolution:* The pipeline was migrated to an asynchronous mapping format, dropping latency to <100ms. Assigned: Harsh kumar.
* **ISSUE-14 (Database Schema Drift):** *Resolved.* ORM properties diverged from actual SQLAlchemy columns. 
  * *Resolution:* Re-initialized Alembic and generated locked revisions utilizing `uv`. Assigned: Foochini.
* **ISSUE-18 (Over-eager React Query Hooks):** *Resolved.* The frontend chart re-rendered continuously creating browser memory leaks. 
  * *Resolution:* Implemented debouncing and dependent query keys. Assigned: KavalS.

### Active/Pending Issues
* **ISSUE-22 (WebSocket Integration):** Currently active. Pushing live data updates directly to the frontend lacks reliable handshake closure. 
  * *Due Date:* Next Sprint (End of Week 8). 
  * *Accountability:* Parag Jindal.
* **ISSUE-25 (Docker Build Size):** Currently active. The ML backend container approaches 2.5GB.
  * *Due Date:* Week 9. 
  * *Accountability:* Foochini.

## 3. Iteration Assessment & Lessons Learned

**Evaluation Criteria Met:**
1. ✅ Minimum Viable API connected to external mock data endpoints.
2. ✅ React interactive dashboard successfully plotting historical data adjacent to ML predictions.
3. ✅ Code coverage thresholds hit 81%.

**Process Problems Addressed ("The sooner you fall behind, the more time you will have to catch up"):**
During the initial week, setting up virtual environments using standard Python `pip` caused desynchronization amongst team members depending on OS (Windows vs Linux). The team paused active feature development for 2 days specifically to research and migrate the entire monolithic workspace into a modernized `uv` and Docker-Compose workflow. This initial setback yielded a 10x multiplier in consistency for the remainder of the iteration, perfectly showcasing that early restructuring saves later debugging.

## 4. Finished Tasks & Accomplished Project Work

**Backend API Component:** Both core entities (MarketData, Prediction) have been modeled and serialized. Polling workers are actively inserting simulated real-time data seamlessly into a PostgreSQL context volume.
**Frontend Chart Component:** TanStack Query reliably captures the REST JSON endpoints. Recharts is mapped conditionally to show 'future' values accurately on dynamic axes.
**ML Framework:** The legacy static model was replaced with an actively instantiable Singleton wrapping the XGBoost Regressor object, preventing excessive memory reload overheads.

## 5. Workload Information (Team Member Hours)

*The exact hour-by-hour breakdown per member is available in the subsequent Individual Project Report documentation.* 

| Name | Role Summary | Hours (Sprint 3) |
|---|---|---|
| Harsh kumar (Harshksaw) | API Core, ML Integration | 38 hrs |
| Parag Jindal (Paragjindal01) | API Endpoints, Pydantic Schema | 30 hrs |
| KavalS | React Hooks, Architecture | 35 hrs |
| Guntash (guntash499) | Components Layout, Recharts | 28 hrs |
| Foochini | DevOps, Pytest, Documentation | 34 hrs |

**Total Team Effort:** 165 hours.
