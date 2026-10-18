# ==============================================================================
# Backend Dockerfile — FastAPI + Python 3.13
# ==============================================================================
FROM python:3.13-slim

WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install curl for container health check
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy backend source code
COPY app ./app

# Expose FastAPI port
EXPOSE 8000

# Run uvicorn server bound to 0.0.0.0 so external machines/containers can connect
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
