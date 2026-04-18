#!/bin/bash

set -euo pipefail

COMPOSE_FILE="docker-compose.test.yml"
SERVICE_URL="http://localhost:8000"
MAX_RETRIES=30
RETRY_INTERVAL=2

# Ensure cleanup runs on exit regardless of success/failure
cleanup() {
    echo "🧹 Tearing down test stack..."
    docker compose -f "$COMPOSE_FILE" down -v --remove-orphans 2>/dev/null || true
}
trap cleanup EXIT

echo "🚀 Building and starting test stack..."
docker compose -f "$COMPOSE_FILE" up -d --build

echo "⏳ Waiting for service to become healthy..."
for i in $(seq 1 $MAX_RETRIES); do
    if curl -sf "${SERVICE_URL}/health" > /dev/null 2>&1; then
        echo "✅ Service is healthy!"
        break
    fi
    echo "   Attempt $i/$MAX_RETRIES. Waiting ${RETRY_INTERVAL}s..."
    sleep $RETRY_INTERVAL
done

if ! curl -sf "${SERVICE_URL}/health" > /dev/null 2>&1; then
    echo "❌ Service failed to become healthy within timeout."
    docker compose -f "$COMPOSE_FILE" logs
    exit 1
fi

echo "🧪 Running deployment smoke tests..."
export BASE_URL="${SERVICE_URL}"
export RUN_DEPLOYMENT_TESTS=1
if ! python -m pytest tests/test_deployment.py -v; then
    echo "❌ Smoke tests failed."
    docker compose -f "$COMPOSE_FILE" logs
    exit 1
fi

echo "✅ Deployment tests passed successfully!"
exit 0
