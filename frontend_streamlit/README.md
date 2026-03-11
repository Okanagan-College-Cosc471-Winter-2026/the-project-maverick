# Streamlit Frontend

This directory contains the replacement frontend for the project. It talks to the existing FastAPI backend and covers the currently mounted APIs for:

- market overview and stock browsing
- per-symbol OHLC charts
- prediction requests
- dataset snapshot generation and downloads

The terminal-style training log UI from the React app is intentionally excluded from this Streamlit version.

## Local run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r frontend_streamlit/requirements.txt
API_BASE_URL=http://localhost:8000/api/v1 streamlit run frontend_streamlit/app.py
```

If you want the app to listen on a fixed port locally:

```bash
API_BASE_URL=http://localhost:8000/api/v1 streamlit run frontend_streamlit/app.py --server.port 8501
```

This Streamlit app is intentionally set up to run directly from a local Python virtual environment. It does not require Docker to start.
