# Developer's Guide

## 1. Introduction
Welcome to the Developer's Guide for `the-project-maverick`. This comprehensive guide gives software engineers navigating the codebase a foundational understanding of the project's Analysis Models, Design Models, architectural layout, and code structures required to expand upon the Stock Prediction Platform.

---

## 2. Analysis Models

### 2.1 Use Case Diagram (Textual Representation)
The system revolves around three central actors: **User (Retail Investor/Trader)**, **System Backend Poller**, and the **External Financial API Provider**.

* **Retail Investor** -> Views Dashboard
* **Retail Investor** -> Changes Stock Symbol to Track
* **System Poller** -> Fetches Latest OHLCV Market Data from **External Financial API**
* **System Poller** -> Generates ML Predictions (Includes calculating Technical Indicators)
* **System Poller** -> Broadcasts Real-Time Updates via WebSockets to **Retail Investor**

### 2.2 Domain Model
The logical business domain focuses on the flow of Time Series Financial Data translating into Predicted Valuations.

**Core Entities:**
- `Stock` (Symbol [e.g. AAPL], CompanyName)
- `MarketData` (FK_Stock, Timestamp, Open, High, Low, Close, Volume)
- `Prediction` (FK_Stock, PredictedTimestamp, PredictedPrice, ConfidenceScore, ModelVersion)

**Relationships:**
- A `Stock` has many `MarketData` instances over time.
- A `MarketData` iteration triggers exactly one `Prediction` iteration.
- The `UI Dashboard` subscribes to the stream of combined `MarketData` and `Prediction` arrays.

### 2.3 Activity Diagram (Optionally representable via flow logic)
**Activity Flow: Polling Execution**
1. [Start Node: Internal Cron Triggers]
2. Action: Poll external API for data.
3. Decision: Is the market closed?
   - If YES -> Log "Market Closed", Skip inference.
   - If NO -> Continue to Action: Extract latest OHLCV.
4. Action: Append technical signals (RSI, MACD) inside Pandas.
5. Action: Request inference vector from XGBoost Object.
6. Action: Save `actual_data` and `prediction_data` into PostgreSQL table.
7. [End Node]

---

## 3. Design Models

### 3.1 Architecture Overview
The system follows a classic decoupled 3-tier architecture, completely Dockerized for scalability and seamless networking.

- **Presentation Layer (Tier 1):** Built on React 19 and Vite. Utilizes standard functional components and global state querying via TanStack React Query.
- **Application Layer (Tier 2):** Developed via FastAPI using Python's async core. Houses the predictive machine learning engine logic heavily intertwined with the server-side logic routing.
- **Data Layer (Tier 3):** Scalable relational mapping via PostgreSQL (capable of ingesting Timescale extension for production time-series scale).

### 3.2 Class Diagram Concept (Core Backend Implementation)
```python
class DatabaseSessionManager:
    # Handles SQLAlchemy Engine and isolated session connections.
    def get_db(): yields AsyncSession

class PollerService:
    # Orchestrates the fetch -> process -> infer pipeline
    def execute_polling_cycle(symbol: str) -> None:

class FeatureExtractor:
    # Data Engineering specific class
    def compute_macd(df: pd.DataFrame) -> pd.DataFrame:
    def compute_rsi(df: pd.DataFrame) -> pd.DataFrame:

class ModelManager (Singleton):
    # ML wrapping layer for the XGBoost core
    def load_model(path: str) -> XGBRegressor:
    def predict(features: List[float]) -> float:
```

### 3.3 Sequence and Collaboration Diagrams
**Sequence: API Fetch Scenario**
1. `Dashboard (React)` calls `GET /api/v1/predictions/latest?symbol=AAPL` on `FastAPI`.
2. `FastAPI Route` initiates an AsyncSession via `DatabaseSessionManager`.
3. `DatabaseSessionManager` queries `PostgreSQL`.
4. `PostgreSQL` returns an array of serialized predictions.
5. `FastAPI Route` formats models using Pydantic Validation (`PredictionSchema`).
6. `FastAPI` returns JSON to `React`.
7. `Dashboard` re-renders `PriceChart.tsx` via `Recharts`.

---

## 4. Code Structure & Navigation

### 4.1 Project Source Code Attachments and Map
```text
the-project-maverick/
├── backend/                   
│   ├── app/
│   │   ├── main.py            # Primary HTTP Application Instance (FastAPI)
│   │   ├── poller.py          # Background task implementation
│   │   ├── features.py        # Logic for FeatureExtractor (Pandas)
│   │   ├── model.py           # Logic for ModelManager Singleton
│   │   ├── database.py        # SQLAlchemy mapping
│   │   ├── api/               # REST Route Handlers
│   │   └── schemas/           # Pydantic JSON validation interfaces
│   ├── models/                # Static serialized ML object storage (.pkl)
│   └── tests/                 # Execution directory for Pytest
├── frontend/                  
│   ├── src/
│   │   ├── components/        # Isolated modular React UI logic
│   │   ├── hooks/             # Abstractions for API client/Websocket
│   │   └── App.tsx            # Core Router Component
```

### 4.2 Test Source Code Integration
The developer must maintain 80% coverage. Tests are segregated in `backend/tests/`.
* `test_api.py` utilizes Pytest Asyncio and a mock HTTP client to simulate frontend interaction against endpoints.
* `test_model.py` inputs static dummy arrays to ensure the XGBoost algorithm yields identical, non-drifting results after builds.
* `test_db.py` utilizes SQLite memory instances to ensure ORM mapping behaves gracefully under migration.

### 4.3 Setting Up Development Workspaces
We mandate using `uv` for python to minimize environment issues.
```bash
# Backend
cd backend
uv sync
uv run alembic upgrade head
uv run fastapi dev app/main.py

# Frontend
cd frontend
npm install
npm run dev
```
New code must strictly be typed. MyPy checking acts as an automated block on our CI workflows.

---

*(Note: Developer configurations for Docker environments and deployments are appended distinctly in DEPLOYMENT.md and README.md provided directly in the repository root.)*
