#!/bin/sh
# scripts/run_tests.sh
# Entrypoint for test container; waits for server readiness, executes pytest, reports exit code

set -u

SERVER_URL="${MCP_SERVER_URL:-http://mcp-server:8000}"
HEALTH_ENDPOINT="${SERVER_URL}/health"
MAX_RETRIES=30
RETRY_INTERVAL=2
ATTEMPT=0

echo "========================================="
echo "  TfL MCP Server Integration Test Runner"
echo "========================================="
echo "Target server: ${HEALTH_ENDPOINT}"
echo "Waiting for MCP server to become ready..."

# Wait for the MCP server health endpoint to respond
while [ $ATTEMPT -lt $MAX_RETRIES ]; do
    if wget --no-verbose --tries=1 --spider "${HEALTH_ENDPOINT}" 2>/dev/null; then
        echo "✅ MCP server is ready."
        break
    fi
    ATTEMPT=$((ATTEMPT + 1))
    echo "⏳ Attempt ${ATTEMPT}/${MAX_RETRIES} failed. Retrying in ${RETRY_INTERVAL}s..."
    sleep $RETRY_INTERVAL
done

if [ $ATTEMPT -eq $MAX_RETRIES ]; then
    echo "❌ ERROR: MCP server did not become ready after ${MAX_RETRIES} attempts."
    exit 1
fi

echo ""
echo "Running integration tests..."
pytest tests/integration/ -v --tb=short
TEST_EXIT_CODE=$?

echo ""
if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo "✅ All tests passed successfully."
else
    echo "❌ Tests failed with exit code ${TEST_EXIT_CODE}."
fi

exit $TEST_EXIT_CODE