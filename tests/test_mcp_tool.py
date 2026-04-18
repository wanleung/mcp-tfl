"""Unit tests for the MCP Tool registration and call handler."""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from tools.underground_status import register_tools, cache_manager
from models.schemas import LineStatus
from clients.tfl_api import TflApiError


class MockMCP:
    """Mock MCP server to capture registered tools without requiring the full SDK."""
    def __init__(self):
        self.tools = {}

    def tool(self):
        def decorator(func):
            self.tools[func.__name__] = func
            return func
        return decorator


@pytest.fixture
def mock_mcp():
    return MockMCP()


def test_register_tools(mock_mcp):
    """Ensure the tool is correctly registered on the MCP instance."""
    register_tools(mock_mcp)
    assert "get_tfl_underground_status" in mock_mcp.tools


@pytest.mark.asyncio
async def test_tool_cache_hit(mock_mcp):
    """Test that a cache hit bypasses the API call."""
    register_tools(mock_mcp)
    tool_func = mock_mcp.tools["get_tfl_underground_status"]
    
    lines = [LineStatus(line_name="Central", status_severity=0, status_description="Good Service", is_good_service=True, disruption_reason=None)]
    cache_manager.set(lines)
    
    with patch("tools.underground_status.fetch_all_lines", new_callable=AsyncMock) as mock_fetch:
        result = await tool_func()
        assert mock_fetch.call_count == 0
        assert '"Central"' in result
        assert '"cache_status": "fresh"' in result or '"cache_status": "cached"' in result


@pytest.mark.asyncio
async def test_tool_cache_miss_fetches_api(mock_mcp):
    """Test that a cache miss triggers an API fetch and caches the result."""
    register_tools(mock_mcp)
    tool_func = mock_mcp.tools["get_tfl_underground_status"]
    
    cache_manager._cache.clear()
    mock_raw = [{"name": "Victoria", "lineStatuses": [{"statusSeverity": 0, "statusSeverityDescription": "Good Service"}]}]
    
    with patch("tools.underground_status.fetch_all_lines", new_callable=AsyncMock, return_value=mock_raw):
        result = await tool_func()
        assert '"Victoria"' in result
        assert '"cache_status": "fresh"' in result


@pytest.mark.asyncio
async def test_tool_api_error_with_stale_cache(mock_mcp):
    """Test fallback to stale cache when API fails."""
    register_tools(mock_mcp)
    tool_func = mock_mcp.tools["get_tfl_underground_status"]
    
    cache_manager.set([LineStatus(line_name="Bakerloo", status_severity=0, status_description="Good", is_good_service=True, disruption_reason=None)])
    
    with patch("tools.underground_status.cache_manager.is_stale", return_value=True), \
         patch("tools.underground_status.fetch_all_lines", new_callable=AsyncMock, side_effect=TflApiError("API Down")):
        result = await tool_func()
        assert '"Bakerloo"' in result
        assert '"cache_status": "stale"' in result
        assert '"error_type": "api_failure"' in result


@pytest.mark.asyncio
async def test_tool_api_error_no_cache(mock_mcp):
    """Test graceful fallback when API fails and cache is empty."""
    register_tools(mock_mcp)
    tool_func = mock_mcp.tools["get_tfl_underground_status"]
    
    cache_manager._cache.clear()
    
    with patch("tools.underground_status.fetch_all_lines", new_callable=AsyncMock, side_effect=TflApiError("API Down")):
        result = await tool_func()
        assert '"lines": []' in result
        assert '"error_type": "api_failure"' in result
        assert '"user_message": "Failed to fetch live status from TfL API. Please try again later."' in result