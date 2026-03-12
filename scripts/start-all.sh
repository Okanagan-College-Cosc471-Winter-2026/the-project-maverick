#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="${1:-${ROOT_DIR}/.env.server}"
RUN_DIR="${ROOT_DIR}/run"

mkdir -p "${RUN_DIR}"

pkill -f "uvicorn app.main:app" 2>/dev/null || true
pkill -f "streamlit run ${ROOT_DIR}/frontend_streamlit/app.py" 2>/dev/null || true

nohup "${ROOT_DIR}/scripts/start-backend.sh" "${ENV_FILE}" > "${RUN_DIR}/backend.log" 2>&1 &
echo $! > "${RUN_DIR}/backend.pid"

sleep 3

nohup "${ROOT_DIR}/scripts/start-streamlit.sh" "${ENV_FILE}" > "${RUN_DIR}/streamlit.log" 2>&1 &
echo $! > "${RUN_DIR}/streamlit.pid"

echo "Started backend and Streamlit."
echo "Backend log:   ${RUN_DIR}/backend.log"
echo "Streamlit log: ${RUN_DIR}/streamlit.log"
