# Stage 1: Build stage
FROM python:3.12-slim AS builder

WORKDIR /app

COPY requirements.txt .

RUN python3 -m venv /app/.venv && \
    /app/.venv/bin/pip install --upgrade pip && \
    /app/.venv/bin/pip install -r requirements.txt

# Stage 2: Runtime stage
FROM python:3.12-slim

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv

COPY . .

# Set environment variables
ENV PATH="/app/.venv/bin:$PATH" \
    VIRTUAL_ENV="/app/.venv" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UVICORN_WORKERS=2

# Expose port
EXPOSE 8003

# Run the app
CMD ["sh", "-c", "exec /app/.venv/bin/python -m uvicorn main:app --host 0.0.0.0 --port 8003"]