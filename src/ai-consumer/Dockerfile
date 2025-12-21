# Stage 1: Build Stage (deps only)
FROM python:3.12-alpine AS builder

WORKDIR /app

COPY requirements.txt .

RUN python3 -m venv /app/.venv && \
    /app/.venv/bin/pip install --upgrade pip && \
    /app/.venv/bin/pip install -r requirements.txt

# Stage 2: Runtime Stage
FROM python:3.12-alpine

WORKDIR /app


COPY --from=builder /app/.venv /app/.venv
COPY consumer.py redis_config.py models.py ./
COPY character_response ./character_response

ENV PATH="/app/.venv/bin:$PATH" \
    VIRTUAL_ENV="/app/.venv" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UVICORN_WORKERS=2


CMD ["python", "consumer.py"]