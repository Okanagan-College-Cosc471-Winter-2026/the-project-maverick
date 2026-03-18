---
pdf_options:
  format: Letter
  margin: 22mm
  displayHeaderFooter: false
stylesheet: https://cdnjs.cloudflare.com/ajax/libs/github-markdown-css/5.5.1/github-markdown.min.css
body_class: markdown-body
css: |-
  body { font-size: 12px; line-height: 1.7; }
  h1 { color: #1a5276; border-bottom: 2px solid #2980b9; padding-bottom: 6px; }
  h2 { color: #1a5276; margin-top: 16px; }
  h3 { color: #2c3e50; margin-top: 12px; }
---

# MarketSight - Release Notes

## v1.1.0 (March 17, 2026) - IOC Release

### New Features
- **Streamlit Frontend:** New data exploration interface for browsing market data, running inference tests, and managing dataset snapshots
- **DRI Production Deployment:** Application deployed on DRI server with SSL, Nginx reverse proxy, and management scripts
- **Native XGBoost Model Format:** Migrated from JSON to native .ubj binary format with meta.json metadata. Model loading time reduced from ~3s to ~1.2s
- **Centralized Feature Engineering:** New module calculates all 53 technical indicators, ensuring training/inference parity
- **Data Warehouse Sync:** Script to sync remote DRI PostgreSQL data to local instances via SSH tunnel
- **Stock Detail UI Improvements:** Removed stock list table, streamlined layout, added chart range breaks for weekends/holidays
- **UTC DateTime Standardization:** All frontend timestamps now display in UTC format

### Restored Features
- **Prediction Confidence Scoring:** Re-integrated with 53-feature pipeline after Sprint 4 merge conflict
- **Predictions Page UI:** Full predictions page restored with stock selector, Predict/Predict All, and confidence display

### Known Issues
- No user authentication (open access to all endpoints)
- No real-time WebSocket streaming
- No prediction history or accuracy tracking
- PR #45 (dante_feature) still open - needs rebase onto main

---

## v1.0.0 (March 3, 2026) - MVP Release

### New Features
- Stock price prediction with Optuna HPO-optimized XGBoost model
- 53-feature engineering pipeline (RSI, MACD, Bollinger Bands, lag features, volume metrics)
- FMP data integration replacing yfinance with chunked downloads and gap filling
- Prediction confidence scoring (4-factor heuristic)
- Interactive OHLC charts (candlestick + line modes) with prediction overlay
- Batch prediction ("Predict All") for all tracked stocks
- Full DRAC end-to-end training pipeline
- Automated data seeding and model retraining via Airflow
- Dashboard with summary statistics
- Admin user management (superusers only)
- User settings (profile, password, account deletion)
- Training monitor page with log streaming

---

## v0.1.0 (February 9, 2026) - Initial Release

### New Features
- Project scaffold with Docker Compose (backend, frontend, PostgreSQL, Nginx)
- XGBoost model training notebook
- PostgreSQL database schema with Alembic migrations
- React 19 frontend with TanStack Router
- CI/CD pipeline with GitHub Actions (6 jobs)
- Market data seeding scripts
- System architecture diagrams
- Project README and development guide
