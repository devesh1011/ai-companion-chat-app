# Stage 1: Build Stage (deps only)
FROM python:3.12-slim AS builder

WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Create virtual environment and install dependencies
RUN python3 -m venv /app/.venv && \
    /app/.venv/bin/pip install --upgrade pip && \
    /app/.venv/bin/pip install -r requirements.txt


# Stage 2: Runtime Stage
FROM python:3.12-slim

WORKDIR /app

# Copy the entire virtual environment from the builder stage
COPY --from=builder /app/.venv /app/.venv

# Copy the application source code (e.g., main.py, etc.)
COPY . .

# Environment variables
ENV PATH="/app/.venv/bin:$PATH" \
    VIRTUAL_ENV="/app/.venv" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UVICORN_WORKERS=2

EXPOSE 5000

# Run the app
CMD ["sh", "-c", "exec /app/.venv/bin/python -m uvicorn main:app --host 0.0.0.0 --port 5000"]