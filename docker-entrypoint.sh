#!/bin/sh
set -e

# Default to 8501 if PORT is not set
TARGET_PORT="${PORT:-8501}"

echo "Starting AGHR Streamlit Dashboard on port ${TARGET_PORT}..."

exec streamlit run dashboard/app.py \
    --server.port="${TARGET_PORT}" \
    --server.address="0.0.0.0" \
    --server.headless=true \
    --server.enableCORS=false \
    --server.fileWatcherType=none \
    --browser.gatherUsageStats=false \
    "$@"
