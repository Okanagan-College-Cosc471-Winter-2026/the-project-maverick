#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="${1:-${ROOT_DIR}/.env.server}"
VENV_DIR="${ROOT_DIR}/myenv"

if [[ ! -f "${ENV_FILE}" ]]; then
  echo "Missing env file: ${ENV_FILE}"
  echo "Create it first with: cp ${ROOT_DIR}/server.env.example ${ROOT_DIR}/.env.server"
  exit 1
fi

if [[ ! -x "${VENV_DIR}/bin/streamlit" ]]; then
  echo "Missing virtualenv at ${VENV_DIR}"
  echo "Run: bash ${ROOT_DIR}/scripts/setup-myenv.sh"
  exit 1
fi

set -a
source "${ENV_FILE}"
set +a

exec "${VENV_DIR}/bin/streamlit" run "${ROOT_DIR}/frontend_streamlit/app.py" \
  --server.address 0.0.0.0 \
  --server.port "${STREAMLIT_PORT:-8501}"
