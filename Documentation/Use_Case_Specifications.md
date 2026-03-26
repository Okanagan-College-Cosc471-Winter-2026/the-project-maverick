# Use Case Specifications

**Title:** the-project-maverick Use Cases
**Course:** COSC 471

The following Use Case Specifications apply to the primary interactions within the Stock Market Prediction System.

---

## Use Case 1: View Real-Time Stock Predictions

**Use Case Name:** View Real-Time Stock Predictions
**Primary Actor:** Retail Investor / User
**Brief Description:** The user navigates to the dashboard to monitor the current market state and view ML-generated future price predictions for selected stock symbols.

**Flow of Events:**
1. **Basic Flow:**
   1. The user launches the frontend application via their web browser.
   2. The system loads the default dashboard and initiates a request to the FastAPI application for the latest stock data for default symbols (e.g., AAPL).
   3. The FastAPI backend queries the PostgreSQL database for recent historical data and the latest XGBoost prediction.
   4. The system renders an interactive chart displaying the historical price, technical indicators, and the predicted next closing price with its confidence interval.
   5. The user interacts with the chart via hovers and zooming to inspect specific data points.

2. **Alternative Flow (Data Unchanging/Weekend):**
   If the market is closed, the system recognizes the timestamp and displays the last known prediction, flagging the data state as "Market Closed".

**Special Requirements:**
- The frontend visualization must render seamlessly (<500ms paint time) leveraging Recharts.
- The UI must visually differentiate between historical actual data lines and future prediction data lines (e.g., dashed lines for predictions).

**Pre Conditions:**
- The application (Frontend and Backend) must be fully initialized.
- The PostgreSQL database must contain recently polled stock data.
- The XGBoost Model must be loaded into memory.

**Post Conditions:**
- The user is presented with accurate and chronologically correct visualization data.
- The user session correctly holds its state for future symbol selections.

---

## Use Case 2: Change Stock Symbol

**Use Case Name:** Change Stock Symbol
**Primary Actor:** User
**Brief Description:** The user selects a different stock ticker to view its specific historical data and predictions.

**Flow of Events:**
1. **Basic Flow:**
   1. The user clicks on the "Symbol Selector" dropdown/input field on the dashboard.
   2. The user types or selects a new valid ticker symbol (e.g., "MSFT").
   3. The React frontend sends a REST API (`GET /api/v1/predictions/latest?symbol=MSFT`) request to the backend.
   4. The backend validates the symbol, retrieves standard data and predictions for the symbol, and returns a JSON response.
   5. The dashboard clears the previous chart context and animates the rendering of the new symbol's data.

2. **Alternative Flow (Invalid Symbol):**
   If the user enters a symbol that doesn't exist or isn't tracked:
   1. The frontend invokes the API endpoint.
   2. The backend responds with a `404 Not Found` or invalid symbol error.
   3. The UI presents an error toast/message stating "Stock symbol not found or currently unsupported."

**Special Requirements:**
- Search inputs must be sanitized to prevent malicious inputs.

**Pre Conditions:**
- The user must currently be viewing the interactive dashboard.

**Post Conditions:**
- The system focuses the chart on the newly selected stock parameter, and future polling cycles will request updates for this specific symbol.

---

## Use Case 3: System Background Polling & Inference

**Use Case Name:** System Background Polling & Inference
**Primary Actor:** Backend Service (System Actor)
**Brief Description:** The backend polling service automatically fetches live market data, computes indicators, triggers inferences, and stores the results without human interaction.

**Flow of Events:**
1. **Basic Flow:**
   1. The scheduled polling task activates according to `POLL_INTERVAL_SECONDS`.
   2. The background worker queries the external financial API for new OHLCV data.
   3. The data is passed to the Pandas pipeline for feature engineering (MACD, RSI, etc.).
   4. The sanitized feature array is given to the `ModelManager` (XGBoost Regressor) to infer the next price.
   5. A prediction record is structured with `predicted_price` and `confidence_score`.
   6. Both the fetched real data and new prediction are stored in the PostgreSQL database matching the current timestamp.
   7. (Optional WebSocket Path) The system broadcasts the new prediction node to any connected frontend clients.

2. **Alternative Flow (External API Down):**
   1. The system attempts external API fetching but receives a 5xx timeout.
   2. The error is securely logged using internal logging.
   3. The polling worker gracefully skips the inference event and schedules for the next retry interval, ensuring the core server does not crash.

**Special Requirements:**
- The ModelManager must be a Singleton to ensure memory efficiency and avoid race conditions upon continuous parallel executions.

**Pre Conditions:**
- The FastAPI backend process is running.
- External internet connectivity exists, and valid `.env` credentials are in place.

**Post Conditions:**
- The Database contains the newly processed row.
- Connected Users automatically receive new nodes on their graphs via REST refresh or WebSocket push.
