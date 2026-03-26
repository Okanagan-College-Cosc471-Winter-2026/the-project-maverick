# Configuration Management

**Title:** Configuration Management Plan
**Project:** the-project-maverick
**Course:** COSC 471

---

## 1. Introduction
This Configuration Management (CM) document details how the development team will handle version control, system building, environmental synchronization, and change tracking for the "the-project-maverick" application. Establishing rigorous CM mitigates the risk of "it works on my machine" errors and preserves historical data for the Stock Price Prediction system's intricate ML and API ecosystem.

## 2. Version Management (Version Control Standards)

**Repository Tooling:**
- Source Code is hosted exclusively on GitHub.
- Git is the sole version control system utilized.

**Branching Strategy:**
The team adheres to a modified **Git Flow**.
- `main`: The single source of truth for production-ready code. Commits here must be tagged with release versions.
- `develop`: The primary integration branch. All feature branches merge into here.
- `feature/<issue-id>-<short-desc>`: Used for developing new features locally (e.g., `feature/12-add-rsi-indicator`).
- `bugfix/<issue-id>-<short-desc>`: Used for rectifying non-critical bugs found in develop.
- `hotfix/<issue-id>-<short-desc>`: Urgent production fixes branched directly off `main`.

**Commit Conventions:**
We employ Conventional Commits to easily scan history:
- `feat:` A new feature.
- `fix:` A bug fix.
- `docs:` Documentation only changes.
- `refactor:` Code changes that neither fix a bug nor add a feature.
- `test:` Adding missing tests or correcting existing ones.

## 3. System Building

### 3.1 Coding Standards
- **Python (Backend):** Adherence to PEP 8 standards. The `ruff` linter/formatter is configured globally for automated consistency. Static type-checking is enforced via `mypy`.
- **TypeScript/React (Frontend):** Adherence to Airbnb's style guide via `Biome` standard formatting rules. Usage of Strict Mode in `tsconfig.json`.

### 3.2 Compilation & Build Environments
The system utilizes robust containerization and modern environments to eliminate cross-platform discrepancies:

1. **Backend Construction (`uv` Manager):**
   The backend relies on Astral's `uv` for instantaneous environment synchronization.
   ```bash
   uv sync # Locks precise dependency versions in uv.lock
   uv run alembic upgrade head # Ensures database schematics are synchronized
   ```
2. **Frontend Construction:**
   Vite acts as the build bundler. `package-lock.json` secures exact Node module versions.
3. **Containerization (Docker):**
   A `docker-compose.yml` orchestrates the entire fleet (DB, Backend, Frontend) assuring synchronized environment injection spanning from local dev into production staging.

### 3.3 License Information
The project is distributed under the underlying **MIT License**, legally permitting robust academic demonstration and commercial derivation without explicit restrictions, provided attribution is maintained (as seen in `LICENSE` file).

## 4. Release Management

We use Semantic Versioning (SemVer) format: `MAJOR.MINOR.PATCH`.
- **MAJOR:** Incompatible API design overhauls or structural ML pipeline alterations.
- **MINOR:** Features added in a backward-compatible manner.
- **PATCH:** Backward-compatible bug fixes or security patches.

**Release Pipeline (GitHub Actions CI/CD):**
1. When a PR is merged into `main`, a tag is cut marking the version (e.g., `v1.2.0`).
2. GitHub Actions intercepts the tag generation.
3. The Action builds testing suites, ensures linter passes, and generates an automated Release snippet matching commit history.

## 5. Change Management

### 5.1 Change Assessment
Any requests fundamentally altering architectures must be submitted via the **Change Request Protocol** to prevent feature creep.

### 5.2 Change Request Format (Template)

```markdown
# Change Request Form

**CR ID:** [Auto-generated, e.g., CR-001]
**Requestor:** [Name]
**Date:** [Submission Date]

**Proposed Change Description:**
[Brief 1-paragraph description of the architectural or feature change]

**Reason for Change (Business/Technical Value):**
[Why do we need this? E.g., The raw Pandas pipeline was too slow; we need to add PySpark for parallel feature mapping.]

**Impact Analysis:**
- **Affected Components:** [e.g., poller.py, features.py, requirements.txt]
- **Time/Schedule Impact:** [e.g., Adds 5 hours to current sprint, delays Milestone 3]
- **Risk Assessment:** [e.g., High risk of breaking existing API schemas]

**Approval Status:** [Pending / Approved / Rejected / Deferred]
**Scrum Master Signature:** [Name/Date]
```

### 5.3 Tracking System
Change Requests are managed using GitHub Issues designated with the `change-request` label. A weekly review meeting specifically addresses pending CRs to officially reject or allocate them mapping into the following sprint's Work Breakdown Structure.
