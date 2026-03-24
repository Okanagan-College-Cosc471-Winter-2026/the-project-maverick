#!/bin/bash
set -e

echo "Stopping all MarketSight Apptainer instances..."

apptainer instance stop maverick-streamlit || true
apptainer instance stop maverick-backend || true
apptainer instance stop maverick-db || true

echo "Done!"
