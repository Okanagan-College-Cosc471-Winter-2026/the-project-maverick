# User's Manual

## the-project-maverick: Stock Market Prediction Platform

**Organization:** Okanagan College
**Target Audience:** Retail Investors, Financial End-users
**Course:** COSC 471

---

### Welcome to "the-project-maverick"
"The Project Maverick" provides institutional-grade Machine Learning predictions distilled into a simple, beautiful, and interactive dashboard interface.

### 1. System Requirements & Access
To leverage the dashboard, you will require:
- A modern Web Browser (e.g., Google Chrome v100+, Firefox v90+, Safari v15+).
- An active internet connection.

Simply navigate to the official domain string (e.g., `http://localhost:5173` or your hosted web address) provided by your system administrator.

### 2. Navigating the Interface

Upon launching the application, you will be presented with the primary UI overlay:

#### The Main Dashboard Canvas
- **Stock Ticker Header:** Displays the currently selected tracking symbol (e.g., "**AAPL** - Apple Inc.") and the most recently polled stock price updating dynamically.
- **Interactive Price Chart:** The massive centered graph is an interactive display representing both history and future estimations.
    - **Solid Line:** Represents actual, historical closing prices on market days.
    - **Dashed Line:** Emulates the XGBoost inference logic predicting tomorrow's (or the next chronological step) potential stock closing price.
    - **Shaded Area Context:** Acts as the Model Confidence bound—meaning the algorithmic math states with X% certainty that the price will remain between the uppermost border and lowermost border of the shade.

#### Changing Tracked Symbols
On the top right quadrant of the screen, you will locate a drop-down labeled "Search Symbol".
1. Click the text field.
2. Type your requested ticker (e.g., type "TSLA").
3. Select the valid company from the list dropdown.
4. The backend API will be called, rapidly refreshing the chart to draw specific historical context mapped directly to the newly requested symbol.

### 3. Understanding Context and Algorithms
*Note that no financial application provides guaranteed results; this tool models historical patterns mapping against RSI/MACD indices, generating simulated momentum potentials.*
- Hovering your cursor over *any node* along the main line chart reveals a precisely timed tooltip. This tooltip demonstrates exactly what value the stock held contextually per date.
- Hovering over predictive nodes displays exactly what probability metric the XGBoost backend has allocated to this distinct jump direction.

### 4. Technical Indicator Controls (Advanced Users)
Beneath the core chart layout exists parameter toggles altering visual outputs:
- **Checkbox: RSI View:** Turning this on injects a secondary visual trace mapping momentum vectors between bounds of 0-100 indicating computationally over-bought (>70) or over-sold (<30) territories.
- **Checkbox: MACD View:** Truncates average distributions giving clearer volatility insights.

### 5. Troubleshooting Common User Errors

* **"Chart Data Loading..." Spinner fails to disappear:**
  Your connection to the backend REST API may be severed. Ensure you are connected to the network, or contact administration indicating an HTTP 500 block.
* **"Symbol Not Supported" Error:**
  Our external data provider (FMP API) may not map all international exchanges. Ensure you are specifically requesting localized, recognized ticker symbols (e.g., matching standard NASDAQ outputs).
* **Flatlining Predictive Lines:**
  If the market is closed (e.g., Weekends/Holidays), the backend intentionally bypasses predictive inferences causing a 'flatline' effect. This is normal functionality representing paused time.
