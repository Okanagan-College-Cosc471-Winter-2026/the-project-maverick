# Vision Document

**Organization:** Okanagan College
**Course:** COSC 471 - Software Engineering (Winter 2026)
**Project:** the-project-maverick (Real-Time ML-Powered Stock Price Prediction Platform)
**Year:** 2026

**Team Members:**

- Dante Bertolutti
- Harsh Kumar
- Parag Jindal
- Kaval S
- Guntash Brar
- Zane Tessmer (Foochini)

---

## 1. Introduction

The purpose of this Vision Document is to provide a high-level overview of the Stock Market Prediction System ("the-project-maverick"). It defines the core problem, describes the target stakeholders and users, outlines product features, and sets constraints and documentation requirements. This document serves as a foundational contract between the development team and project stakeholders.

## 2. Stakeholder and User Descriptions

### 2.1 Stakeholders

- **Course Instructors and Evaluators:** Assess the project against software engineering constraints, agility, and overall quality of code and documentation.
- **Development Team:** The project creators responsible for planning, executing, and maintaining the software.
- **Financial APIs (FMP):** Providers of the market data stream; stakeholders in terms of acceptable use policies and rate limits.

### 2.2 Users

- **Retail Investors:** Users with limited technical skills seeking an accessible interface that translates complex market trends into actionable predictions.
- **Day Traders:** Power users who demand low-latency data and real-time visualization of technical indicators (MACD, RSI, Bollinger Bands).

## 3. Product Overview

The Stock Market Prediction System is a production-ready application that leverages machine learning to forecast stock price paths. The system continuously ingests market data, calculates complex technical indicators on the fly, and feeds this data into an ensemble of XGBoost models. Users can view the outputs via a highly interactive React-based dashboard, allowing them to track model accuracy by comparing predicted prices with actual outcomes.

The system supports 29 tracked stock symbols and provides next-day 15-minute interval path predictions across 26 time bars, giving users a granular view of expected intraday price movement.

## 4. Product Features (Connected to IBM RP DB)

The following primary features are essential to the product's success:

| Feature ID | Feature | Description |
|-----------|---------|-------------|
| FEA-01 | Real-Time Data Ingestion | The backend polls financial APIs for the latest OHLCV data and stores it in the market schema |
| FEA-02 | Feature Engineering Engine | Calculates technical indicators including RSI, MACD, Bollinger Bands, ATR, and OBV dynamically using a Pandas pipeline |
| FEA-03 | Machine Learning Inference | Pre-trained XGBoost models provide sub-second next-day path predictions across 26 time horizons with confidence scores |
| FEA-04 | Interactive Dashboard | React + TypeScript frontend featuring Recharts and Lightweight Charts for plotting live stock prices and predictions |
| FEA-05 | Historical Accuracy Tracking | The system persists both predicted and actual prices to a PostgreSQL database to demonstrate model validity over time |
| FEA-06 | Data Snapshot Export | Users can build, list, and download Parquet or CSV snapshots of stock data for offline analysis |
| FEA-07 | Model Training Pipeline | Airflow DAGs and DRAC integration for automated model retraining with Optuna hyperparameter optimization |

## 5. Constraints

- **Hardware/Environment:** Must be deployable via Docker and functional within local virtual environments for academic grading. The backend uses Python 3.10+, and the frontend uses React 19.
- **Data Limitations:** Predictions are only as good as the incoming data; the system is constrained by the rate limits of the external API provider (FMP).
- **Latency Constraint:** Prediction inference combined with API response time must remain consistently below 100ms for a seamless user experience.
- **Compliance:** Sensitive data (API keys, database credentials) must not be statically committed but injected via `.env` files.

## 6. Precedence and Priority

The development follows iterations based on priority:

1. **High Priority (Core Functionality):** Data fetching, ML inference (XGBoost integration), REST API creation, and baseline React dashboard.
2. **Medium Priority (Enhancements):** Advanced technical indicator integration, confidence interval plotting, data snapshot exports, and PostgreSQL persistence.
3. **Low Priority (Future Roadmap):** WebSocket streaming, Streamlit alternative frontend, and authentication capabilities.

## 7. Other Product Requirements

- **Performance:** The system must handle up to 100 or more concurrent requests.
- **Security:** All endpoints validated via Pydantic v2; prevention of SQL injection through the use of SQLAlchemy parameterized queries.
- **Testing:** The system shall maintain at least 80% code coverage measured via Pytest.

## 8. Documentation Requirements

### 8.1 User Manual

Detailed instructions on how to navigate the dashboard, interpret the prediction charts, and customize the symbols tracked by the system.

### 8.2 Online Help

Embedded tooltips and a dedicated FAQ section within the application guiding users on terminology (what MACD or RSI means) and common troubleshooting steps.

### 8.3 Installation Guides, Configuration, Read Me File

A comprehensive `README.md` and deployment documentation containing `uv`, `docker-compose`, and Node.js build instructions. Covers setting up the PostgreSQL database and populating the `.env` settings.

### 8.4 Labelling and Packaging

The product is packaged into scalable Docker containers utilizing `docker-compose.yml`. Node and Python virtual environments are supported as a secondary fallback.

## Appendix A: Glossary

| Term | Definition |
|------|-----------|
| OHLCV | Open, High, Low, Close, Volume - standard market data format |
| RSI | Relative Strength Index - a momentum indicator measuring the speed of price changes (0-100 scale) |
| MACD | Moving Average Convergence Divergence - a trend-following momentum indicator |
| XGBoost | eXtreme Gradient Boosting - a scalable machine learning system used for the platform's predictive models |
| ORM | Object-Relational Mapping (SQLAlchemy) |
| ATR | Average True Range - a volatility indicator |
| OBV | On-Balance Volume - a cumulative volume-based indicator |
| Bollinger Bands | A volatility indicator consisting of a moving average and two standard deviation bands |
| FMP | Financial Modeling Prep - the external financial data API provider |
| Parquet | A columnar storage file format optimized for analytical workloads |
