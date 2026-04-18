"""MCP tool registration and handler for TfL Underground Status.

Orchestrates cache lookup, API fetching, response formatting, and error fallback.
"""

import logging
from datetime import datetime, timezone
from typing import Any

from mcp.server.fastmcp import FastMCP

from cache.manager import CacheManager
from clients.tfl_api import fetch_all_lines, TflApiError
from config.settings import settings
from models.schemas import ToolResponse
from utils.formatter import format_response

logger = logging.getLogger(__name__)

# Singleton cache manager instance
cache_manager = CacheManager(ttl_seconds=settings.TFL_CACHE_TTL)


def register_tools(mcp: FastMCP) -> None:
    """Register the TfL Underground Status tool with the MCP server.

    Args:
        mcp: The FastMCP server instance to register the tool with.
    """

    @mcp.tool()
    async def get_tfl_underground_status() -> str:
        """Retrieve the current operational status of all TfL Underground lines.

        Returns:
            A JSON string representing the ToolResponse schema.
        """
        try:
            # 1. Check cache
            cache_entry = cache_manager.get()
            is_stale = cache_manager.is_stale()

            if cache_entry and not is_stale:
                # Cache hit
                cache_status = "fresh" if cache_entry.ttl_remaining_seconds > settings.TFL_CACHE_TTL / 2 else "cached"
                response = format_response(cache_entry.data, cache_status=cache_status)
            else:
                # Cache miss or stale -> fetch from API
                raw_data = await fetch_all_lines()
                response = format_response(raw_data, cache_status="fresh")
                # Cache the formatted line statuses
                cache_manager.set(response.lines)

            return response.model_dump_json()

        except TflApiError as e:
            logger.error(f"TfL API communication failed: {e}")
            # Fallback to stale cache if available
            stale_entry = cache_manager.get()
            if stale_entry:
                logger.warning("Serving stale cache due to API failure")
                response = format_response(
                    stale_entry.data,
                    cache_status="stale",
                    error_type="api_failure",
                    user_message="Using cached data due to temporary API issues."
                )
                return response.model_dump_json()

            # Complete failure fallback
            fallback = ToolResponse(
                timestamp_utc=datetime.now(timezone.utc),
                cache_status="stale",
                lines=[],
                summary="Unable to retrieve TfL Underground status at this time.",
                warnings=["Service status unavailable"],
                error_type="api_failure",
                user_message="Failed to fetch live status from TfL API. Please try again later."
            )
            return fallback.model_dump_json()

        except Exception as e:
            logger.exception("Unexpected error in tool handler")
            fallback = ToolResponse(
                timestamp_utc=datetime.now(timezone.utc),
                cache_status="stale",
                lines=[],
                summary="An unexpected error occurred.",
                warnings=["Internal server error"],
                error_type="internal_error",
                user_message="An unexpected error occurred while processing your request."
            )
            return fallback.model_dump_json()