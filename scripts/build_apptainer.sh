#!/bin/bash
set -e

echo "========================================="
echo "Building Apptainer images from Docker..."
echo "========================================="

echo "1. Building Docker Compose images to ensure they are up to date..."
docker compose build backend streamlit

echo "2. Building postgres.sif..."
apptainer build --force postgres.sif docker-daemon://postgres:16

echo "3. Building backend.sif..."
apptainer build --force backend.sif docker-daemon://backend:latest

echo "4. Building streamlit.sif..."
apptainer build --force streamlit.sif docker-daemon://maverick-streamlit:latest

echo "========================================="
echo "Done! You now have the Apptainer images."
echo "You can move these .sif files and the startup scripts to your cluster."
echo "========================================="
