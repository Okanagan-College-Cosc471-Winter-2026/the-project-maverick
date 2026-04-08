# User Manual

## What This System Is

The Project Maverick is a stock prediction platform with:

- a Postgres data store
- a FastAPI backend
- a Streamlit dashboard

The dashboard lets you inspect market data, predictions, and simulation output.

## Access

When running locally:

- Streamlit dashboard: `http://localhost:8501`
- Backend API docs: `http://localhost:8000/docs`

## Main Things You Can Do

- browse supported stock symbols
- view recent market history
- overlay predictions on charts
- inspect simulation and replay views
- review training and snapshot-related outputs when exposed by the backend

## What The Charts Show

- historical market prices
- model prediction paths
- side-by-side actual vs predicted behavior
- simulation playback based on saved model artifacts

## Troubleshooting

- If the dashboard cannot load data, check that the backend is running on `http://localhost:8000`.
- If backend calls fail, verify `API_BASE_URL` for Streamlit.
- If charts are blank for a symbol, the backend may not have enough stored data for that symbol yet.
