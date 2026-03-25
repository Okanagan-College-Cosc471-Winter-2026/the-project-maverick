# User's Manual

## the-project-maverick: Stock Market Prediction Platform

**Organization:** Okanagan College
**Course:** COSC 471 - Software Engineering (Winter 2026)
**Target Audience:** Retail Investors, Financial End-Users

---

## Welcome

"The Project Maverick" provides machine learning-powered stock price predictions through a simple, interactive dashboard interface. This manual guides you through using the platform effectively.

## 1. System Requirements

To use the dashboard, you need:

- A modern web browser (Chrome 100+, Firefox 90+, Safari 15+, Edge 100+)
- An active internet connection

Navigate to the application URL provided by your administrator (e.g., `http://localhost:5173` for local installations or the hosted web address for deployed instances).

## 2. Navigating the Interface

### 2.1 The Sidebar

The left sidebar displays the list of tracked stock symbols (29 stocks including AAPL, MSFT, GOOGL, TSLA, and more). Click any symbol to navigate to its detail page.

### 2.2 Stock Detail Page

Each stock detail page shows:

- **Stock Header:** Displays the currently selected symbol and company name with the most recently polled price.
- **Interactive Price Chart:** The main chart shows historical OHLCV data with candlestick or line visualization. You can zoom, pan, and hover for detailed data point inspection.
- **Prediction Overlay:** When predictions are available, the chart shows the next-day 15-minute predicted price path as an overlay, visually differentiated from historical data.

### 2.3 Changing Tracked Symbols

1. Click on a different stock symbol in the sidebar.
2. The dashboard navigates to that stock's detail page.
3. The chart updates with the selected stock's historical data and latest predictions.

Alternatively, use the URL directly: navigate to `/dashboard/stocks/TSLA` to view Tesla's data.

## 3. Understanding Predictions

### 3.1 How Predictions Work

The system uses an XGBoost machine learning model trained on historical market data and technical indicators. For each stock, it generates a predicted price path for the next trading day across 26 time intervals (15-minute bars).

### 3.2 Confidence Scores

Each prediction comes with a confidence score:

| Score Range | Meaning |
|------------|---------|
| Above 0.80 | High confidence - strong correlation with trained patterns |
| 0.60 to 0.79 | Moderate confidence - reasonable estimate with some market uncertainty |
| Below 0.60 | Low confidence - current price behavior is unusual relative to training data |

### 3.3 Technical Indicators

The predictions are informed by several technical indicators calculated from market data:

- **RSI (Relative Strength Index):** Measures momentum on a 0-100 scale. Above 70 suggests overbought conditions; below 30 suggests oversold.
- **MACD (Moving Average Convergence Divergence):** Shows trend-following momentum by comparing two moving averages.
- **Bollinger Bands:** Display price volatility using a moving average with upper and lower standard deviation bands.

## 4. Data Snapshots

For users who want to perform offline analysis, the platform supports data snapshot exports:

1. Use the data snapshot API (`POST /api/v1/data/build-snapshot`) to generate a snapshot.
2. Specify the ticker (or "ALL" for all stocks), date range, and format (Parquet, CSV, or both).
3. Download the generated file via the snapshots endpoint.

## 5. Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| Chart shows a loading spinner that does not resolve | Backend API connection may be down | Verify the backend is running and check your network connection |
| "Symbol Not Supported" error | The requested ticker is not in the tracked list | Use one of the 29 supported stock symbols listed in the sidebar |
| Prediction line appears flat | Market is closed (weekends/holidays) | This is normal; the system pauses inference when no trading data is available |
| Stale data displayed | Polling interval has not triggered yet | Refresh the page; the backend polls for new data at configured intervals |

## 6. Disclaimer

This tool models historical patterns using machine learning and technical indicators. No financial application provides guaranteed results. Predictions are probabilistic estimates and should not be used as the sole basis for investment decisions. Always consult with a qualified financial advisor before making investment decisions.
