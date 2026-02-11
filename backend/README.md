# MarketSight Backend

High-performance Async Python API for real-time stock prediction.

## 🛠️ Tech Stack
-   **Framework**: FastAPI
-   **Database**: PostgreSQL + SQLAlchemy v2 (Async)
-   **Migrations**: Alembic
-   **ML**: XGBoost + Scikit-Learn
-   **Package Manager**: `uv`

## 🚀 Quick Start

### 1. Install Dependencies
```bash
uv sync
```

### 2. Setup Database
```bash
# Start Postgres (if not using Docker)
# Then run migrations:
uv run alembic upgrade head
```

### 3. Run Development Server
```bash
uv run fastapi dev app/main.py
```

## 🏗️ Project Structure
```
backend/
├── app/
│   ├── api/            # Route handlers (v1/api)
│   ├── core/           # Config, DB connection, Logging
│   ├── modules/        # Domain logic
│   │   ├── market/     # Stock data & CRUD
│   │   ├── inference/  # ML Model & Feature Engineering
│   ├── main.py         # App entry point
├── tests/              # Pytest suite
├── alembic/            # Database migrations
└── pyproject.toml      # Dependencies
```

## 🧪 Testing
```bash
# Run all tests
uv run pytest tests/ -v

# Run specific test
uv run pytest tests/modules/test_inference.py
```

## 🧠 ML Inference
The `inference` module handles stock price prediction:
1.  **Loading**: Singleton `ModelManager` loads `xgboost_model.joblib`.
2.  **Features**: `features.py` calculates RSI, MACD, etc. on the fly.
3.  **Prediction**: Returns predicted price + confidence interval.
