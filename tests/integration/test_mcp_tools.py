"""Integration tests for MCP tool discovery, execution, error handling, and cache behavior.

Validates tool schemas, MCP-compliant error codes, cache TTL consistency, and health reporting.
"""
import pytest

pytestmark = pytest.mark.asyncio


async def test_tools_list_returns_valid_schemas(mcp_client):
    """Verify that the server exposes expected tools with valid JSON Schema definitions."""
    response = await mcp_client("tools/list")
    assert "result" in response
    assert "tools" in response["result"]
    tools = response["result"]["tools"]
    assert len(tools) > 0
    
    tool_names = [t["name"] for t in tools]
    assert "get_line_status" in tool_names
    assert "get_line_disruption" in tool_names
    
    status_tool = next(t for t in tools if t["name"] == "get_line_status")
    assert "inputSchema" in status_tool
    assert status_tool["inputSchema"]["type"] == "object"


async def test_get_line_status_returns_valid_data(mcp_client):
    """Execute the line status tool and verify it returns structured TfL data."""
    response = await mcp_client("tools/call", {
        "name": "get_line_status",
        "arguments": {}
    })
    assert "result" in response
    content = response["result"]["content"]
    assert len(content) > 0
    assert content[0]["type"] == "text"
    
    text = content[0]["text"].lower()
    assert "victoria" in text or "status" in text


async def test_invalid_tool_call_returns_mcp_error(mcp_client):
    """Ensure malformed or unknown tool calls return standard JSON-RPC error codes."""
    response = await mcp_client("tools/call", {
        "name": "non_existent_tool",
        "arguments": {}
    })
    assert "error" in response
    assert "code" in response["error"]
    assert "message" in response["error"]
    # JSON-RPC standard codes: -32601 (Method not found), -32602 (Invalid params)
    assert response["error"]["code"] in [-32601, -32602]


async def test_cache_ttl_consistency(mcp_client):
    """Verify that rapid successive calls return identical payloads, confirming cache hits."""
    resp1 = await mcp_client("tools/call", {"name": "get_line_status", "arguments": {}})
    resp2 = await mcp_client("tools/call", {"name": "get_line_status", "arguments": {}})
    
    assert "result" in resp1 and "result" in resp2
    text1 = resp1["result"]["content"][0]["text"]
    text2 = resp2["result"]["content"][0]["text"]
    assert text1 == text2, "Cache should return identical responses within the configured TTL window"


async def test_health_endpoint_reports_cache_age(mcp_client, http_client):
    """Validate the /health probe returns service status and cache age metrics."""
    response = await http_client.get("/health")
    response.raise_for_status()
    data = response.json()
    
    assert data["status"] == "ok"
    assert "cache_age_sec" in data
    assert isinstance(data["cache_age_sec"], int)
    assert data["env"] == "test"