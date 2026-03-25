# Use Case Specifications

**Organization:** Okanagan College
**Course:** COSC 471 - Software Engineering (Winter 2026)
**Project:** the-project-maverick

---

## Use Case 1: View Real-Time Stock Predictions

**Use Case Name:** View Real-Time Stock Predictions
**Primary Actor:** Retail Investor / User

**Brief Description:** The user navigates to the dashboard to monitor the current market state and view ML-generated future price predictions for selected stock symbols.

**Flow of Events:**

1. Basic Flow:
   1. The user launches the frontend application via their web browser.
   2. The system loads the default dashboard and requests the latest stock data from the FastAPI backend for the default symbol.
   3. The backend queries the PostgreSQL database for recent historical data and runs XGBoost inference to generate a next-day path prediction.
   4. The system renders an interactive chart displaying the historical price, technical indicators, and the predicted next-day 15-minute path with confidence intervals.
   5. The user interacts with the chart via hover tooltips and zooming to inspect specific data points.

2. Alternative Flow (Market Closed):
   If the market is closed (weekends/holidays), the system displays the last known prediction and flags the data state accordingly.

**Special Requirements:**

- The frontend visualization must render within 500ms.
- The UI must visually differentiate between historical actual data and predicted future data (e.g., dashed lines for predictions).

**Pre Conditions:**

- The application (frontend and backend) must be fully initialized.
- The PostgreSQL database must contain recently polled stock data.
- The XGBoost model artifacts must be loaded into memory.

**Post Conditions:**

- The user is presented with accurate and chronologically correct visualization data.
- The user session correctly holds its state for future symbol selections.

---

## Use Case 2: Change Stock Symbol

**Use Case Name:** Change Stock Symbol
**Primary Actor:** User

**Brief Description:** The user selects a different stock ticker to view its specific historical data and predictions.

**Flow of Events:**

1. Basic Flow:
   1. The user clicks on the symbol selector in the sidebar or dashboard.
   2. The user types or selects a new valid ticker symbol (e.g., "MSFT").
   3. The React frontend sends a REST API request (`GET /api/v1/inference/predict/MSFT`) to the backend.
   4. The backend validates the symbol, retrieves data, runs inference, and returns the prediction response.
   5. The dashboard clears the previous chart and renders the new symbol's data with predictions.

2. Alternative Flow (Invalid Symbol):
   1. The user enters a symbol that does not exist or is not tracked.
   2. The backend responds with a `404 Not Found` error.
   3. The UI presents an error message stating "Stock symbol not found or currently unsupported."

**Special Requirements:**

- Search inputs must be sanitized to prevent injection attacks.

**Pre Conditions:**

- The user must currently be viewing the interactive dashboard.

**Post Conditions:**

- The system focuses the chart on the newly selected stock symbol.

---

## Use Case 3: System Background Polling and Inference

**Use Case Name:** System Background Polling and Inference
**Primary Actor:** Backend Service (System Actor)

**Brief Description:** The backend polling service automatically fetches live market data, computes technical indicators, triggers model inference, and stores the results without human interaction.

**Flow of Events:**

1. Basic Flow:
   1. The scheduled polling task activates according to the configured interval.
   2. The background worker queries the external financial API (FMP) for new OHLCV data.
   3. The data is passed to the feature engineering pipeline for technical indicator calculation (MACD, RSI, Bollinger Bands, ATR, OBV).
   4. The processed feature array is fed to the XGBoost model ensemble to generate next-day path predictions across 26 time horizons.
   5. Prediction records are structured with predicted prices and confidence scores for each horizon.
   6. Both the fetched market data and new predictions are stored in the PostgreSQL database.

2. Alternative Flow (External API Down):
   1. The system attempts API fetching but receives a timeout or error response.
   2. The error is logged internally.
   3. The polling worker skips the inference event and schedules the next retry, ensuring the core server does not crash.

**Special Requirements:**

- The model loader must handle multiple horizon models efficiently to avoid excessive memory usage.

**Pre Conditions:**

- The FastAPI backend process is running.
- External internet connectivity exists and valid `.env` credentials are in place.

**Post Conditions:**

- The database contains the newly processed prediction records.
- Connected users receive updated data on their next chart refresh.

---

## Use Case 4: Build and Download Data Snapshot

**Use Case Name:** Build and Download Data Snapshot
**Primary Actor:** User / Data Analyst

**Brief Description:** The user requests a data export of stock data from the database as a Parquet or CSV file for offline analysis.

**Flow of Events:**

1. Basic Flow:
   1. The user sends a POST request to `/api/v1/data/build-snapshot` with optional parameters (ticker, date range, format).
   2. The backend queries the market schema for the requested tickers and date range.
   3. The data is concatenated and written to the specified file format (Parquet, CSV, or both).
   4. The user receives a response with the filename, row count, and processing time.
   5. The user can then download the file via `GET /api/v1/data/snapshots/download/{filename}`.

2. Alternative Flow (No Data Found):
   1. The requested ticker or date range has no data in the database.
   2. The backend returns a `404` response indicating no data was found.

**Special Requirements:**

- Date parameters must be handled via parameterized SQL queries to prevent injection.

**Pre Conditions:**

- The database must contain market data for the requested tickers.

**Post Conditions:**

- A snapshot file is saved to the server's snapshot directory and is available for download.

---

## Use Case 5: Initiate Model Training Job

**Use Case Name:** Initiate Model Training Job
**Primary Actor:** Administrator / Developer

**Brief Description:** An administrator triggers a model training job via the training API to retrain the XGBoost model with updated data.

**Flow of Events:**

1. Basic Flow:
   1. The administrator sends a POST request to `/api/v1/training/start` with job metadata.
   2. The backend launches a background training process.
   3. The administrator monitors progress via `/api/v1/training/status` or the training log stream.
   4. Upon completion, new model artifacts are saved and can be loaded by the inference service.

2. Alternative Flow (Training Fails):
   1. The training process encounters an error (insufficient data, configuration issue).
   2. The error is logged and the status endpoint reflects the failure.

**Special Requirements:**

- Training must not block the main API server thread.

**Pre Conditions:**

- Sufficient training data must be available in the database.
- The backend must be running with access to the ML scripts.

**Post Conditions:**

- Updated model artifacts are saved to the model artifacts directory.
- The training log is available for review.
