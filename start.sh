#!/bin/sh
set -e

# Set default port if PORT is not set
if [ -z "$PORT" ]; then
    PORT=8000
fi

exec uvicorn app.main:app --host 0.0.0.0 --port $PORT
