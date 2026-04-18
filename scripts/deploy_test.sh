#!/bin/bash

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
if ! pytest tests/test_deployment.py -v; then
    echo "❌ Smoke tests failed."
    docker compose -f "$COMPOSE_FILE" logs
    exit 1
fi

echo "✅ Deployment tests passed successfully!"
exit 0

# Deployment Test Plan: TfL Underground Status MCP Server

## Services Tested
| Service | Port | Health Check |
|---------|------|--------------|
| app     | 8000 | GET /health  |

## Smoke Tests
| Test | Endpoint | Expected |
|------|----------|----------|
| Health check | GET /health | 200 OK, JSON with `status="healthy"` |
| OpenAPI Schema | GET /openapi.json | 200 OK, valid JSON schema with `/health` path |
| MCP Transport Mount | GET /mcp | 200/405/406 (not 404/500), confirms SSE routing |
| Not Found | GET /nonexistent | 404 Not Found |

## How to Run Locally
chmod +x scripts/deploy_test.sh
./scripts/deploy_test.sh

## CI Integration
These tests run in the `deploy-test` job in `.github/workflows/run-tests.yml`.