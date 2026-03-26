# Online Help Document

**Project:** the-project-maverick
**Version:** 1.0.0
**Course:** COSC 471

---

## 1. Frequently Asked Questions (FAQ)

### What is 'The Project Maverick'?
"The Project Maverick" is an automated, real-time stock price prediction platform. Utilizing complex backend modeling (built upon XGBoost), the system ingests live market data continuously and mathematically forecasts where the stock will likely close next, offering investors probabilistic confidence ratings backing the prediction.

### Where does the data come from?
Our backend integrates tightly with authoritative financial data providers (e.g., Financial Modeling Prep - FMP API) mapping accurate market volume structures identically matching real-world stock exchanges.

### Why does the predictive line sometimes stay completely horizontal?
You are observing a standard flatline. This behavior specifically signifies that the stock market is currently *closed* (such as weekends, evenings, or statutory holidays), halting algorithmic inference since no incoming trading volume exists.

### What do the acronyms "MACD" and "RSI" stand for?
* **MACD (Moving Average Convergence Divergence):** Highlights trend-following momentum changes showing the relationship traversing two moving averages of a specific stock's active price.
* **RSI (Relative Strength Index):** Evaluates momentum oscillators measuring the exact velocity of price directional swings, scaling primarily between bounds (0-100).

## 2. Platform Navigation Reference

### How to use the Graph Symbol Picker
1. Click the input box labeled **"Search Symbol"** situated prominently on the upper-right corner of the Dashboard.
2. Select your desired tracking target.
3. Observe the chart update; previous UI charts clear entirely enabling an isolated view of the refreshed metric structures.

### Accessing Tooltips
Place your cursor onto any intersection point alongside the plotted arrays on your primary display. A high-contrast floating overlay box will instantly render, listing the exact price matching your indicated intersection moment alongside precision confidence intervals denoting machine learning estimations.

## 3. Reporting System Issues

### The Page Won't Load
The Frontend UI functions entirely separate from the Backend ML service. If your page layout paints but displays infinite loading icons, your connection to the specific `FastAPI` instance hosting the endpoints is missing. Try verifying your `.env` parameters if you are self-hosting, confirming `VITE_API_URL` routes logically to `http://localhost:8000`.

### Blank Charting Data Instances (Missing Nodes)
If certain dates yield zero data while requesting historical stock tracking, this signifies standard API throttling limitations executed gracefully by the database; the poller will patch the blank structures upon next available interval window resets.

## 4. Understanding Confidence Scores
The inference engine assigns an attribute `confidence_score` dynamically computed to every single generated prediction point mapping.
* **> 0.80 (High Confidence):** Deep mathematical correlation recognized directly mirroring heavily trained modeling paths.
* **0.60 - 0.79 (Moderate Confidence):** Significant market fluctuation implies generic estimations standardly traversing accepted bounds.
* **< 0.60 (Weak Confidence):** The current price path acts extremely unprecedented and the machine acts merely as an observational guesser contextually. User caution highly dictated during active trading maneuvers.
