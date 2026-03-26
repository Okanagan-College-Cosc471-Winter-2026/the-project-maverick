# Installation Guide

**Project:** the-project-maverick
**Version:** 1.0.0
**Course:** COSC 471

---

## 1. Overview and Architecture Principles
"The Project Maverick" involves deploying a multi-tier microservice architecture encompassing a React/Vite frontend scaling, a FastAPI backend, an encapsulated XGBoost inferencer, and scalable PostgreSQL database services. The application provides flexible environments tailored towards completely Dockerized ecosystems or explicit native installations suitable for developers and evaluators utilizing local tooling.

## 2. Prerequisites
Ensure the following tools are present globally mapped on your target deployment machine:
- **Git** (Required for accessing source control).
- **Docker & Docker Compose** (version > 20.0). *Recommended path for evaluators.*
- **Node.js** (version 20.x+) & **npm/bun**. *Only required for local native builds.*
- **Python** (version 3.10+) & **uv/pip**. *Only required for local native builds.*

## 3. Method A: Rapid Docker Integration (Recommended)
This method bridges the entire stack instantaneously without cluttering the native machine with local libraries.

### Step 3.1: Cloning the Application
```bash
git clone https://github.com/organization/the-project-maverick.git
cd the-project-maverick
```

### Step 3.2: Configuration Injecting
Copy our preset environment template to inject sensitive parameters:
```bash
cp .env.example .env
```
*(Open the `.env` file via any text editor—such as nano/vim/VSCode—and change password mapping fields such as `POSTGRES_PASSWORD` and `FMP_API_KEY` to validated secrets).*

### Step 3.3: Compose Initializing
Execute the docker orchestrator globally triggering builds traversing all three linked containers.
```bash
docker-compose up -d --build
```
> The `-d` parameter initiates detachment modes permitting standard terminal utilization. The initial `--build` parameter spans exactly 2-5 minutes downloading the heavy baseline XGBoost dependencies structuring the ML inference image layer.

### Step 3.4: Checking Service Uptime Routes
Verify operational states by navigating your favorite web browser cleanly over to the listed exposed web routes:
- **Frontend App:** `http://localhost:5173`
- **Backend Swagger Docs:** `http://localhost:8000/docs`

## 4. Method B: Standard Local Native (Developers)
If you require code-mutating capabilities devoid of Docker's volume mapping caching constraints.

### Backend Setup:
```bash
cd backend

# Install the ultra-fast Python manager resolving dependencies
curl -LsSf https://astral.sh/uv/install.sh | sh

# Initialize localized Python dependency environments
uv sync

# Instantiate database schemas migrating logic directly mapping to SQLite or Local Postgres instances
uv run alembic upgrade head

# Boot the API server enabling auto-reloading
uv run fastapi dev app/main.py --host 0.0.0.0 --port 8000
```

### Frontend Setup:
Open a completely fresh secondary terminal process:
```bash
cd frontend

# Install node_modules traversing the package.json maps
npm install

# Instantly trigger Vite build-chains routing logic towards Port 5173 
npm run dev
```

## 5. Teardown
To cleanly exit docker container states freeing memory bindings gracefully:
```bash
docker-compose down -v
```
> Supplying the `-v` parameter aggressively tears down the PostgreSQL data volume arrays specifically mapped during container build initialization (All mocked internal state resets to void mappings).
