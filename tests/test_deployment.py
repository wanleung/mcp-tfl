"""
Deployment smoke tests for the TfL MCP Server.
Runs against a live Docker Compose stack using httpx.
Each test is stateless and independent.
"""
import os
import httpx
import pytest

BASE_URL = os.environ.get("BASE_URL", "http://localhost:8000")


@pytest.fixture(scope="function")
def client():
    """Create a fresh httpx client for each test to ensure statelessness."""
    with httpx.Client(base_url=BASE_URL, timeout=10.0) as c:
        yield c


def test_health_endpoint(client):
    """Verify the application is alive and responding."""
    response = client.get("/health")
    assert response.status_code == 200
    payload = response.json()
    assert "status" in payload


def test_line_status_endpoint(client):
    """Verify the primary API endpoint returns valid line status data."""
    response = client.get("/Line/Status")
    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, list)
    assert len(payload) > 0


def test_line_disruption_endpoint(client):
    """Verify parameterized endpoint returns disruption payload."""
    response = client.get("/Line/victoria/Disruption")
    assert response.status_code == 200
    payload = response.json()
    assert "disruptions" in payload
    assert isinstance(payload["disruptions"], list)


def test_unknown_route_returns_404(client):
    """Verify non-existent routes correctly return 404."""
    response = client.get("/api/nonexistent-route-v2")
    assert response.status_code == 404