"""Pytest configuration and fixtures for MCP integration tests.

Provides an async HTTP client and a JSON-RPC helper to interact with the running MCP server.
"""
import os
import pytest
import httpx
from typing import AsyncGenerator, Callable, Awaitable, Dict, Any


@pytest.fixture(scope="session")
def mcp_server_url() -> str:
    """Resolve the target MCP server URL from environment or default to Docker service name."""
    return os.getenv("MCP_SERVER_URL", "http://mcp-server:8000")


@pytest.fixture(scope="session")
async def http_client(mcp_server_url: str) -> AsyncGenerator[httpx.AsyncClient, None]:
    """Provide a shared async HTTP client for the test session."""
    async with httpx.AsyncClient(base_url=mcp_server_url, timeout=10.0) as client:
        yield client


@pytest.fixture
def mcp_client(http_client: httpx.AsyncClient) -> Callable[[str, Dict[str, Any], int], Awaitable[Dict[str, Any]]]:
    """Return a helper function to make JSON-RPC calls to the MCP endpoint."""
    async def _call(method: str, params: Dict[str, Any] | None = None, request_id: int = 1) -> Dict[str, Any]:
        payload = {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": method,
            "params": params or {}
        }
        response = await http_client.post("/mcp", json=payload)
        response.raise_for_status()
        return response.json()
    return _call