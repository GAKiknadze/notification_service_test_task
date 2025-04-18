#!/bin/bash

set -e

mkdir -p /app/logs
chown -R appuser:appuser /app/logs

if [ "$1" = "rest" ]; then
    echo "Starting REST API server..."
    uvicorn src.rest:app --host 0.0.0.0 --port 8000
elif [ "$1" = "worker" ]; then
    echo "Starting Celery worker..."
    celery -A src.tasks worker --loglevel=info
else
    echo "Invalid argument. Use 'rest' or 'worker'"
    exit 1
fi