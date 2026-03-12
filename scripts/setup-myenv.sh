#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="${ROOT_DIR}/myenv"

python3 -m venv "${VENV_DIR}"
"${VENV_DIR}/bin/pip" install --upgrade pip
"${VENV_DIR}/bin/pip" install -r "${ROOT_DIR}/backend/requirements.txt"
"${VENV_DIR}/bin/pip" install -r "${ROOT_DIR}/frontend_streamlit/requirements.txt"

echo
echo "Created virtualenv: ${VENV_DIR}"
echo "Activate with: source ${VENV_DIR}/bin/activate"
