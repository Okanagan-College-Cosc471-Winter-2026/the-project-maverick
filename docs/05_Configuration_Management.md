# Configuration Management

**Organization:** Okanagan College
**Course:** COSC 471 - Software Engineering (Winter 2026)
**Project:** the-project-maverick

---

## 1. Introduction

This Configuration Management (CM) document details how the development team handles version control, system building, environmental synchronization, and change tracking for "the-project-maverick." Establishing rigorous CM practices mitigates environment inconsistency errors and preserves historical data for the stock prediction system's ML and API ecosystem.

## 2. Version Management (Version Control Standards)

### Repository Tooling

- Source code is hosted on GitHub under the Okanagan-College-Cosc471-Winter-2026 organization.
- Git is the sole version control system.

### Branching Strategy

The team uses a modified Git Flow:

| Branch Pattern | Purpose |
|---------------|---------|
| `main` | Single source of truth for production-ready code. Commits are tagged with release versions. |
| `ft-<feature-name>` | Feature branches for developing new features (e.g., `ft-fix-tests`, `ft-dri-migration`). |
| `dante_feature` | Developer-specific feature branches for individual work. |
| `hotfix/<desc>` | Urgent production fixes branched directly off main. |

### Commit Conventions

The team uses Conventional Commits for clear history:

| Prefix | Meaning |
|--------|---------|
| `feat:` | A new feature |
| `fix:` | A bug fix |
| `docs:` | Documentation only changes |
| `refactor:` | Code changes that neither fix a bug nor add a feature |
| `test:` | Adding or correcting tests |

## 3. System Building

### 3.1 Coding Standards

- **Python (Backend):** PEP 8 standards enforced by the `ruff` linter/formatter. Static type-checking via `mypy`.
- **TypeScript/React (Frontend):** Code formatting and linting via `Biome`. Strict mode enabled in `tsconfig.json`.

### 3.2 Build Environments

The system uses containerization and modern package managers to eliminate cross-platform issues:

**Backend (uv package manager):**

```bash
uv sync                       # Lock and install exact dependency versions
uv run alembic upgrade head   # Synchronize database schemas
uv run fastapi dev app/main.py  # Start API server with auto-reload
```

**Frontend (npm/bun):**

```bash
npm install    # Install Node.js dependencies from package-lock.json
npm run dev    # Start Vite dev server on port 5173
```

**Containerization (Docker):**

A `docker-compose.yml` orchestrates all services (PostgreSQL, Backend, Frontend, Adminer, Streamlit) ensuring consistent environments from local development to production.

### 3.3 License Information

The project is distributed under the MIT License, permitting academic demonstration and commercial derivation with attribution.

## 4. Release Management

The project uses Semantic Versioning (SemVer): `MAJOR.MINOR.PATCH`.

| Version Part | When to Increment |
|-------------|-------------------|
| MAJOR | Incompatible API overhauls or structural ML pipeline changes |
| MINOR | Features added in a backward-compatible manner |
| PATCH | Backward-compatible bug fixes or security patches |

**Release Pipeline (GitHub Actions CI/CD):**

1. A pull request is opened against `main`.
2. GitHub Actions runs the test suite, linters (Ruff, Mypy), and type checks automatically.
3. On merge, a version tag is cut (e.g., `v1.2.0`).
4. Docker images can be rebuilt from the tagged commit for deployment.

## 5. Change Management

### 5.1 Change Assessment

Any request that fundamentally alters the architecture must be submitted via the Change Request Protocol to prevent feature creep and ensure team alignment.

### 5.2 Change Request Format

```
CR ID:        [Auto-generated, e.g., CR-001]
Requestor:    [Name]
Date:         [Submission Date]

Proposed Change Description:
[Brief description of the architectural or feature change]

Reason for Change:
[Business or technical value justification]

Impact Analysis:
- Affected Components: [e.g., service.py, features.py, docker-compose.yml]
- Time/Schedule Impact: [e.g., Adds 5 hours to current sprint]
- Risk Assessment: [e.g., High risk of breaking existing API schemas]

Approval Status: [Pending / Approved / Rejected / Deferred]
Scrum Master Signature: [Name/Date]
```

### 5.3 Tracking System

Change Requests are managed using GitHub Issues with the `change-request` label. A weekly review meeting addresses pending CRs and allocates approved changes into the following sprint.
