#!/bin/bash
# deploy_test.sh - Starts stack, waits for health, runs smoke tests, tears down.
# Exits 0 on success, non-zero on failure.

set -o pipefail

COMPOSE_FILE="docker-compose.test.yml"
BASE_URL="${BASE_URL:-http://localhost:8000}"
HEALTH_ENDPOINT="${BASE_URL}/health"
MAX_RETRIES=30
RETRY_INTERVAL=2

# Ensure cleanup runs regardless of success/failure
cleanup() {
    echo "🧹 Tearing down test stack..."
    docker compose -f "$COMPOSE_FILE" down -v --remove-orphans 2>/dev/null || true
}
trap cleanup EXIT

echo "🚀 Building and starting deployment test stack..."
docker compose -f "$COMPOSE_FILE" up -d --build

echo "⏳ Waiting for services to become healthy..."
RETRY_COUNT=0
until curl -sf "$HEALTH_ENDPOINT" > /dev/null 2>&1 || [ $RETRY_COUNT -eq $MAX_RETRIES ]; do
    echo "   Waiting... ($((RETRY_COUNT + 1))/$MAX_RETRIES)"
    sleep $RETRY_INTERVAL
    RETRY_COUNT=$((RETRY_COUNT + 1))
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo "❌ Health check timed out after $MAX_RETRIES attempts."
    echo "--- Container Logs ---"
    docker compose -f "$COMPOSE_FILE" logs --tail=50
    exit 1
fi

echo "✅ Services are healthy. Running smoke tests..."
pytest tests/test_deployment.py -v --tb=short
TEST_EXIT_CODE=$?

if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo "🎉 All smoke tests passed!"
else
    echo "❌ Smoke tests failed!"
fi

exit $TEST_EXIT_CODE

# Deployment Test Plan: Docker Compose Setup for Test and Deployment

## Services Tested
| Service | Port | Health Check |
|---------|------|--------------|
| mcp-server | 8000 | GET /health |
| mock-tfl-api | 8080 | GET /health |

## Smoke Tests
| Test | Endpoint | Expected |
|------|----------|----------|
| Health check | GET /health | 200 OK, `{"status": "ok"}` |
| Line Status API | GET /Line/Status | 200 OK, JSON array |
| Line Disruption API | GET /Line/victoria/Disruption | 200 OK, `{"disruptions": [...]}` |
| Unknown Route | GET /api/nonexistent-route-v2 | 404 Not Found |

## How to Run Locally
chmod +x scripts/deploy_test.sh
./scripts/deploy_test.sh

## CI Integration
These tests run in the `deploy-test` job in `.github/workflows/run-tests.yml`. The script automatically handles stack lifecycle, health polling, and test execution. Override `BASE_URL` in CI if the service is exposed on a different host/port. Ensure `pytest` and `httpx` are available in the CI runner environment.