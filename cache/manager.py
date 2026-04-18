"""Cache manager for TfL Underground Status MCP Server.

Implements a thread-safe wrapper around cachetools.TTLCache to handle
line status caching, staleness tracking, and async-safe access.
"""

import threading
from datetime import datetime, timezone, timedelta
from typing import Optional

from cachetools import TTLCache

from models.schemas import CacheEntry, LineStatus


class CacheManager:
    """Thread-safe in-memory cache manager for TfL line status data."""

    def __init__(self, ttl_seconds: int = 60, maxsize: int = 1):
        """Initialize the cache manager.

        Args:
            ttl_seconds: Time-to-live for cached entries in seconds.
            maxsize: Maximum number of items in the cache (default 1 for single status snapshot).
        """
        self._cache = TTLCache(maxsize=maxsize, ttl=ttl_seconds)
        self._lock = threading.Lock()
        self._ttl_seconds = ttl_seconds

    def get(self) -> Optional[CacheEntry]:
        """Retrieve the current cache entry if it exists and hasn't been evicted.

        Returns:
            A CacheEntry object with updated TTL remaining, or None on cache miss.
        """
        with self._lock:
            try:
                entry = self._cache["tfl_status"]
                now = datetime.now(timezone.utc)
                ttl_remaining = max(0, int((entry.expires_at_utc - now).total_seconds()))
                return CacheEntry(
                    data=entry.data,
                    fetched_at_utc=entry.fetched_at_utc,
                    expires_at_utc=entry.expires_at_utc,
                    ttl_remaining_seconds=ttl_remaining,
                )
            except KeyError:
                return None

    def set(self, data: list[LineStatus]) -> CacheEntry:
        """Store new line status data in the cache with a fresh TTL.

        Args:
            data: List of LineStatus objects to cache.

        Returns:
            The newly created CacheEntry.
        """
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(seconds=self._ttl_seconds)
        entry = CacheEntry(
            data=data,
            fetched_at_utc=now,
            expires_at_utc=expires_at,
            ttl_remaining_seconds=self._ttl_seconds,
        )
        with self._lock:
            self._cache["tfl_status"] = entry
        return entry

    def is_stale(self) -> bool:
        """Check if the cached data is missing or past its expiration time.

        Returns:
            True if the cache is empty or expired, False otherwise.
        """
        with self._lock:
            try:
                entry = self._cache["tfl_status"]
                return datetime.now(timezone.utc) >= entry.expires_at_utc
            except KeyError:
                return True