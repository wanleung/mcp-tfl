"""
TfL Unified API client module.

Handles async HTTP requests to the TfL API with exponential backoff,
timeout enforcement, and robust error mapping.
"""

import asyncio
import logging
from typing import Dict, List

import httpx

from config.settings import get_settings

logger = logging.getLogger(__name__)

TFL_API_BASE_URL = "https://api.tfl.gov.uk"
TFL_LINE_STATUS_ENDPOINT = f"{TFL_API_BASE_URL}/Line/Mode/tube/Status"


class TflApiError(Exception):
    """Custom exception for TfL API communication failures."""
    pass


async def fetch_all_lines() -> List[Dict]:
    """
    Fetches the current status of all TfL Underground lines.

    Uses exponential backoff for transient failures (5xx, timeouts) and enforces
    timeout constraints from application settings. Maps 4xx/5xx responses to
    descriptive errors.

    Returns:
        List[Dict]: Raw JSON response parsed into a list of line status dictionaries.

    Raises:
        TflApiError: If the request fails after maximum retries or encounters a client error.
    """
    settings = get_settings()
    max_retries = 3
    base_delay = 1.0

    async with httpx.AsyncClient(timeout=settings.TFL_API_TIMEOUT) as client:
        for attempt in range(max_retries):
            try:
                response = await client.get(TFL_LINE_STATUS_ENDPOINT)

                # Map and handle HTTP error status codes
                if response.status_code >= 400:
                    error_msg = f"TfL API returned {response.status_code}: {response.text}"
                    if response.status_code >= 500:
                        logger.warning(f"Server error (attempt {attempt + 1}/{max_retries}): {error_msg}")
                        if attempt < max_retries - 1:
                            delay = base_delay * (2**attempt)
                            await asyncio.sleep(delay)
                            continue
                    # 4xx errors are typically client-side or rate limits; fail fast
                    raise TflApiError(error_msg)

                return response.json()

            except httpx.RequestError as e:
                logger.warning(f"Network/Timeout error (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    delay = base_delay * (2**attempt)
                    await asyncio.sleep(delay)
                    continue
                raise TflApiError(f"Failed to connect to TfL API after {max_retries} attempts: {e}") from e

    raise TflApiError("Unexpected failure in fetch loop")
