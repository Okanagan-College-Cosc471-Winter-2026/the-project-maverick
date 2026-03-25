# Business Case

## the-project-maverick: Real-Time ML-Powered Stock Price Prediction Platform

**Organization:** Okanagan College
**Course:** COSC 471 - Software Engineering (Winter 2026)
**Project:** the-project-maverick
**Year:** 2026

**Team Members:**

- Dante Bertolutti
- Harsh Kumar
- Parag Jindal
- Kaval S
- Guntash Brar
- Zane Tessmer (Foochini)

---

## 1. Executive Summary

The modern stock market relies heavily on data-driven decision-making. Traders and financial analysts face overwhelming volumes of data and struggle to extract actionable insights in real time. "The Project Maverick" is a real-time ML-powered stock price prediction platform designed to provide users with accurate, low-latency stock price forecasts. By leveraging XGBoost machine learning models, live data ingestion, and technical indicators such as RSI, MACD, and Bollinger Bands, the project empowers users to make informed trading decisions with quantified confidence intervals.

## 2. Problem Statement

Individual investors and small analytical firms often lack access to sophisticated, institutional-grade prediction tools. They rely on lagging indicators or delayed data, leading to suboptimal trading strategies. The specific problems include:

1. **Latency:** Delayed data ingestion and prediction computation reduce the viability of short-term trades.
2. **Complexity:** Existing quantitative tools are difficult to set up, unapproachable, and require significant data engineering expertise.
3. **Accuracy Tracking:** Competitor platforms often fail to persist their predictions against actual closing prices to transparently present model accuracy to users.

## 3. Proposed Solution

The-project-maverick offers an accessible, end-to-end web application featuring a React-based frontend and FastAPI backend. Key features of the solution include:

- **Real-Time Predictions:** Automated polling and processing of external market data at configurable intervals.
- **Machine Learning Inference:** XGBoost models deployed as a high-performance, thread-safe service providing next-day 15-minute path predictions across 26 time bars.
- **Interactive Visualizations:** A dynamic dashboard built with Recharts and Lightweight Charts, enabling users to visually compare predicted vs. actual prices alongside confidence scores.
- **Data Persistence:** Leveraging PostgreSQL to store market data, predictions, and track the model's accuracy continuously.
- **Data Snapshots:** Users can build and download Parquet/CSV data snapshots of any tracked stock for offline analysis.

## 4. Market Analysis and Target Audience

**Target Audience:**

- Retail investors seeking data-driven insights.
- Day traders who require sub-second inference models.
- Financial analysts looking for supplementary automated technical analysis.

**Competitive Advantage:**

The system stands out through its transparent accuracy tracking, displaying historical model predictions against real-world outcomes. The use of modern frameworks like FastAPI and React 19 ensures responsiveness below 100ms API response time, offering an institutional-level experience to retail investors.

## 5. Cost-Benefit Analysis

**Costs (Development and Hosting):**

- Development Time: Approximately 4 months of team resources (academic project).
- Hosting and Infrastructure: Managed within standard cloud free tiers or low-cost student credits during academic duration.
- APIs: Free or freemium financial data APIs (Financial Modeling Prep).

**Benefits:**

- **Educational Value:** The team gains production-level experience with distributed systems, MLOps, and modern web frameworks.
- **User Value:** Potential to save investors substantial time in technical analysis and improve their trading strategies via actionable alerts and insights.

## 6. Project Risks

| Risk | Mitigation |
|------|-----------|
| Free-tier API rate limits or downtime from the financial data provider | Implement robust caching, fallback data, and rate limit tracking |
| Model drift causing accuracy degradation over time due to market volatility | Build pipelines for periodic model retraining with the latest data |
| Performance bottlenecks from high-frequency data polling | Utilize scalable asynchronous polling and optimized database queries |

## 7. Strategic Alignment and Conclusion

This project aligns with the educational goals of COSC 471, practically applying software engineering principles, agile methodologies, and full-stack development to solve a real-world problem. By delivering a scalable and interactive prediction platform, the-project-maverick establishes a strong foundation showcasing the team's ability to handle complex data engineering and machine learning deployment tasks.
