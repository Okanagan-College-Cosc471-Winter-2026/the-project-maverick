FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/app /app/app
COPY backend/scripts /app/scripts

# Set python path
ENV PYTHONPATH=/app

CMD ["fastapi", "run", "--workers", "4", "app/main.py"]
