# Change Requests (Printed Submissions)

**Project:** the-project-maverick
**Course:** COSC 471

*The following outlines the registered Change Requests tracking structural pivots during the sprint iteration cycles as dictated by the Configuration Management framework.*

---

## CR-001: Migration to Asynchronous SQLAlchemy Engine

**CR ID:** CR-001
**Requestor:** Harsh kumar
**Date:** [Week 3 of Project]

**Proposed Change Description:**
Transition the entire database schema interaction from the synchronous `psycopg2` driver logic to the `asyncpg` combined with SQLAlchemy version 2.0 AsyncSessions.

**Reason for Change (Business/Technical Value):**
The original system utilized block-wait networking structures during API calls. Considering stock market dashboards are highly concurrent, maintaining synchronous API calls was causing threads to bottleneck during simultaneous dashboard reloads by multiple users, yielding latency spikes north of 800ms. Asynchronous connections return the capability for the single-threaded Python event loop to service thousands of open socket requests.

**Impact Analysis:**
- **Affected Components:** `database.py`, all files in `/api/`, `requirements.txt`.
- **Time/Schedule Impact:** Requires ~8 hours of refactoring existing operational code. Pauses Milestone 2 API completion by 1 day.
- **Risk Assessment:** High risk. Changing ORM session logic implies refactoring all `db.query` statements into equivalent `select()` statements.

**Approval Status:** APPROVED 
**Scrum Master Signature:** _Parag Jindal_ (Approved via GitHub Pull Request Review)

---

## CR-002: Switching Frontend Bundler to Vite

**CR ID:** CR-002
**Requestor:** KavalS
**Date:** [Week 4 of Project]

**Proposed Change Description:**
Ditch `create-react-app (CRA)` and Webpack in favor of Vite utilizing the ESBuild ecosystem. 

**Reason for Change (Business/Technical Value):**
CRA represents legacy infrastructure that drastically inflates build times on local workstations (Dev server taking > 15 seconds to hot reload). By moving to Vite, Local modules are preserved and served near-instantaneously natively, providing the frontend devs a substantially faster iterative workflow.

**Impact Analysis:**
- **Affected Components:** `/frontend/package.json`, root HTML structures, environment variable syntax (`REACT_APP_` shifting to `VITE_`).
- **Time/Schedule Impact:** Minimal structural impact. Requires ~2 hours for migration script mapping.
- **Risk Assessment:** Low risk securely isolated locally. 

**Approval Status:** APPROVED
**Scrum Master Signature:** _Harsh kumar_

---

## CR-003: Removal of Real-Time TimescaleDB Requirement for MVP

**CR ID:** CR-003
**Requestor:** Foochini
**Date:** [Week 6 of Project]

**Proposed Change Description:**
Drop TimescaleDB containerization and rely solely on vanilla Postgres 16 tables for storing Time Series metric data during the core academic presentation cycle.

**Reason for Change (Business/Technical Value):**
Adding TimescaleDB mandates specific image sizes, chunk chunking partitions, and hyper-table routing which exponentially increased Docker context complexities and was breaking initial database seed scripts on Windows machines. Since this application simulates historical fetches without truly ingesting 100k+ rows simultaneously, standard relational SQL is computationally adequate. 

**Impact Analysis:**
- **Affected Components:** `docker-compose.yml`, `seed_data.py`.
- **Time/Schedule Impact:** *Recovers* lost scheduling time by stripping off unnecessary enterprise deployment architectures.
- **Risk Assessment:** Negligible for MVP, though missing long-term hyper-scale capabilities.

**Approval Status:** APPROVED
**Scrum Master Signature:** _Parag Jindal_
