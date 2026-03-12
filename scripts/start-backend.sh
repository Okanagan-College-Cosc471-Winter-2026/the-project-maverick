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

if [[ ! -x "${VENV_DIR}/bin/uvicorn" ]]; then
  echo "Missing virtualenv at ${VENV_DIR}"
  echo "Run: bash ${ROOT_DIR}/scripts/setup-myenv.sh"
  exit 1
fi

mkdir -p "${ROOT_DIR}/datasets" "${ROOT_DIR}/run"
set -a
source "${ENV_FILE}"
set +a

exec "${VENV_DIR}/bin/uvicorn" app.main:app \
  --app-dir "${ROOT_DIR}/backend" \
  --host 0.0.0.0 \
  --port "${BACKEND_PORT:-8000}"
