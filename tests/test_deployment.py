import os
import pytest
import httpx

BASE_URL = os.environ.get("BASE_URL", "http://localhost:8000")
RUN_DEPLOYMENT_TESTS = os.environ.get("RUN_DEPLOYMENT_TESTS") == "1"

pytestmark = pytest.mark.skipif(
    not RUN_DEPLOYMENT_TESTS,
    reason="Deployment smoke tests run only when RUN_DEPLOYMENT_TESTS=1"
)


@pytest.fixture(scope="function")
def client():
    """Provide a fresh HTTP client for each test to ensure strict statelessness."""
    with httpx.Client(base_url=BASE_URL, timeout=10.0) as c:
        yield c


def test_health_check(client: httpx.Client):
    """Verify the liveness/readiness probe returns expected payload."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["cache_active"] is True
    assert "version" in data


def test_openapi_schema(client: httpx.Client):
    """Verify FastAPI automatically exposes a valid OpenAPI specification."""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    data = response.json()
    assert "openapi" in data
    assert "paths" in data
    assert "/health" in data["paths"]


def test_mcp_endpoint_mounted(client: httpx.Client):
    """Verify the MCP SSE transport is correctly mounted and accessible."""
    response = client.get("/mcp")
    # SSE endpoints may return 200, 405, or 406 depending on headers/method
    # We only assert it's not a 404 (unmounted) or 500 (crashed)
    assert response.status_code not in (404, 500)


def test_not_found(client: httpx.Client):
    """Verify unregistered routes correctly return 404."""
    response = client.get("/this-endpoint-does-not-exist")
    assert response.status_code == 404
