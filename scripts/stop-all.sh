#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUN_DIR="${ROOT_DIR}/run"

for pid_file in "${RUN_DIR}/backend.pid" "${RUN_DIR}/streamlit.pid"; do
  if [[ -f "${pid_file}" ]]; then
    kill "$(cat "${pid_file}")" 2>/dev/null || true
    rm -f "${pid_file}"
  fi
done

pkill -f "uvicorn app.main:app" 2>/dev/null || true
pkill -f "streamlit run ${ROOT_DIR}/frontend_streamlit/app.py" 2>/dev/null || true

echo "Stopped backend and Streamlit."
