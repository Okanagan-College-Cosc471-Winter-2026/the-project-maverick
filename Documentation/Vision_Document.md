# Vision Document

## Title Page

**Organization Name:** Okanagan College
**Course Name:** COSC 471
**Project Name:** the-project-maverick (Real-Time ML-Powered Stock Price Prediction Platform)
**Year:** 2026

**Team Members:**
- Harsh kumar (Harshksaw)
- Parag Jindal (Paragjindal01)
- KavalS
- Guntash (guntash499)
- Foochini

---

## 1. Introduction
The purpose of this Vision Document is to provide a high-level overview of the Stock Market Prediction System ("the-project-maverick"). It defines the core problem, describes the target stakeholders and users, outlines product features, and sets constraints and documentation requirements. This document serves as a foundational contract between development team members and project stakeholders.

## 2. Stakeholder and User Descriptions
### 2.1 Stakeholders
- **Course Instructors/Evaluators:** Assess the project against Software Engineering constraints, agility, and overall quality of code and documentation.
- **Development Team:** The project creators responsible for planning, executing, and maintaining the software.
- **Financial APIs (e.g., FMP):** Providers of the market data stream; stakeholders in terms of acceptable use policies and rate limits.

### 2.2 Users
- **Retail Investors:** Users with limited technical skills seeking an accessible interface that translates complex market trends into actionable predictions.
- **Day Traders:** Power users who demand low-latency data and real-time visualization of technical indicators (MACD, RSI, etc.).

## 3. Product Overview
The Stock Market Prediction System is a production-ready application that leverages machine learning to forecast stock closing prices. The system continuously ingests market data, calculates complex technical indicators on-the-fly, and feeds this data into an XGBoost model. Users can view the outputs via a highly interactive React-based dashboard, allowing them to track model accuracy by comparing predicted prices with actual outcomes.

## 4. Product Features (Connected to IBM RP DB)
The following primary features are essential to the product's success:

* **FEA-01: Real-Time Data Ingestion** - The backend will consistently poll financial APIs for the latest OHLCV (Open, High, Low, Close, Volume) data.
* **FEA-02: Feature Engineering Engine** - The system will calculate technical indicators including Relative Strength Index (RSI), Moving Average Convergence Divergence (MACD), and Bollinger Bands dynamically using a Pandas pipeline.
* **FEA-03: Machine Learning Inference** - A pre-trained XGBoost Regressor will provide sub-second price predictions and calculate a confidence score.
* **FEA-04: Interactive Dashboard** - A React + TypeScript frontend featuring Recharts for plotting live stock prices, predictions, and confidence intervals.
* **FEA-05: Historical Accuracy Tracking** - The system will persist both predicted and actual prices to a PostgreSQL database to publicly demonstrate model validity over time.
* **FEA-06: API & WebSocket Streaming** - FastAPI endpoints will provide REST functionality and WebSocket streaming for low-latency live updates.

## 5. Constraints
- **Hardware/Environment:** Must be deployable via Docker and functional within local virtual environments for academic grading. The backend uses Python 3.10+, and the frontend uses React 19.
- **Data Limitations:** Predictions are only as good as the incoming data; the system is constrained by the rate limits of the external API provider.
- **Latency constraint:** Prediction inference combined with API response time must remain consistently below 100ms for a seamless user experience.
- **Compliance:** Sensitive data (e.g., API keys, database credentials) must not be statically committed but injected via `.env` files.

## 6. Precedence and Priority
The development will follow iterations based on priority:
1. **High Priority (Core functionality):** Data fetching, ML inference (XGBoost integration), REST API creation, and baseline React Dashboard.
2. **Medium Priority (Enhancements):** Advanced technical indicator integration, User Confidence Intervals plotting, and PostgreSQL persistence routing.
3. **Low Priority (Future Roadmap):** WebSocket streaming, Advanced TimescaleDB optimization, and Authentication capabilities.

## 7. Other Product Requirements
- **Performance:** System must handle up to 100+ concurrent requests.
- **Security:** All endpoints validated via Pydantic v2; prevention of SQL Injection through the use of SQLAlchemy 2.0 ORM.
- **Testing:** The system shall maintain at least 80% code coverage measured via Pytest.

## 8. Documentation Requirements
Comprehensive documentation will be provided alongside the software to ensure usability and maintainability.

### 8.1 User Manual (or User's Guide)
Detailed instructions on how to navigate the dashboard, interpret the prediction charts, and customize the symbols tracked by the system.

### 8.2 Online Help
Embedded tooltips and a dedicated 'Help' page within the React application guiding users on terminology (e.g., what MACD or RSI means within the platform context).

### 8.3 Installation Guides, Configuration, Read Me File
A comprehensive `README.md` and `DEPLOYMENT.md` containing `uv`, `docker-compose`, and Node.js build instructions. It covers setting up the PostgreSQL database and populating the `.env` settings.

### 8.4 Labelling and Packaging
The product will be packaged into scalable Docker containers utilizing `docker-compose.yml`. Node and Python virtual environments are supported as a secondary fallback. 

### 8.5 Glossary (Appendix)
- **OHLCV:** Open, High, Low, Close, Volume data.
- **RSI:** Relative Strength Index, a momentum indicator.
- **MACD:** Moving Average Convergence Divergence.
- **XGBoost:** eXtreme Gradient Boosting, a scalable machine learning system used for the platform's regression mapping.
- **ORM:** Object-Relational Mapping (e.g., SQLAlchemy).
