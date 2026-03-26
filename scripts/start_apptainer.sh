#!/bin/bash
set -e

echo "========================================="
echo "Starting MarketSight in Apptainer!"
echo "========================================="

# 1. Setup Database
echo "Starting PostgreSQL..."
mkdir -p apptainer-db-data

# Check if instance is already running
if apptainer instance list | grep -q "maverick-db"; then
    echo "maverick-db instance is already running."
else
    apptainer instance start \
        --bind apptainer-db-data:/var/lib/postgresql/data \
        --env POSTGRES_USER=postgres \
        --env POSTGRES_PASSWORD=changethis \
        --env POSTGRES_DB=app \
        postgres.sif maverick-db
    
    echo "Waiting for PostgreSQL to start..."
    sleep 10
fi

# 2. Restore DB if it's empty
if [ ! -f "apptainer-db-data/PG_VERSION" ]; then
    echo "First time setup: Restoring database from parts..."
    if ls db_backup/backup.sql.gz.part-* 1> /dev/null 2>&1; then
        cat db_backup/backup.sql.gz.part-* > /tmp/backup.sql.gz
        apptainer exec postgres.sif zcat /tmp/backup.sql.gz | apptainer exec postgres.sif psql -h 127.0.0.1 -U postgres app
        rm /tmp/backup.sql.gz
        echo "Database restored successfully!"
    else
        echo "Warning: No backup parts found in db_backup/. Starting with an empty DB."
    fi
fi

# 3. Start Backend
echo "Starting Backend..."
if apptainer instance list | grep -q "maverick-backend"; then
    echo "maverick-backend instance is already running."
else
    # We bind current dir or just run it. The container has the code baked in.
    apptainer instance start \
        --env POSTGRES_SERVER=127.0.0.1 \
        --env POSTGRES_PORT=5432 \
        --env POSTGRES_USER=postgres \
        --env POSTGRES_PASSWORD=changethis \
        --env POSTGRES_DB=app \
        --env ENVIRONMENT=local \
        --env SECRET_KEY=changethis \
        --env DOMAIN=localhost \
        --env FRONTEND_HOST=http://localhost:8501 \
        --env BACKEND_CORS_ORIGINS="http://localhost:8501" \
        backend.sif maverick-backend \
        uvicorn app.main:app --host 0.0.0.0 --port 8000
fi

# 4. Start Streamlit
echo "Starting Streamlit..."
if apptainer instance list | grep -q "maverick-streamlit"; then
    echo "maverick-streamlit instance is already running."
else
    # Streamlit points to backend at localhost:8000
    apptainer instance start \
        --env API_BASE_URL=http://localhost:8000/api/v1 \
        streamlit.sif maverick-streamlit \
        streamlit run frontend_streamlit/app.py
fi

echo "========================================="
echo "All systems GO!"
echo "Backend: http://localhost:8000/docs"
echo "Streamlit GUI: http://localhost:8501"
echo "To stop everything, run: ./scripts/stop_apptainer.sh"
echo "========================================="
