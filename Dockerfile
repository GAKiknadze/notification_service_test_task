FROM python:3.10-slim as builder

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    libyaml-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

FROM python:3.10-slim

WORKDIR /app

LABEL maintainer="GAKiknadze" \
    description="Notification Service" \
    version="1.0"

RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/* && \
    groupadd -r appuser && \
    useradd -r -g appuser appuser

RUN mkdir -p /app/logs && \
    touch /app/logs/app.json && \
    chown -R appuser:appuser /app/logs && \
    chmod -R 755 /app/logs

COPY --from=builder /app/wheels /wheels
RUN pip install --no-cache /wheels/*

COPY src/ src/
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

USER appuser

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app

HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/v1/health/ || exit 1

CMD ["./entrypoint.sh", "rest"]