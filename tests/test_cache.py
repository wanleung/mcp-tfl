"""Unit tests for the CacheManager module."""

import time
import pytest
from cache.manager import CacheManager
from models.schemas import LineStatus


def test_cache_set_and_get():
    """Test that set stores data and get retrieves it correctly."""
    manager = CacheManager(ttl_seconds=60)
    lines = [
        LineStatus(
            line_name="Central",
            status_severity=0,
            status_description="Good Service",
            is_good_service=True,
            disruption_reason=None
        )
    ]
    entry = manager.set(lines)
    assert entry is not None
    assert len(entry.data) == 1
    assert entry.data[0].line_name == "Central"
    assert entry.ttl_remaining_seconds > 0


def test_cache_get_empty():
    """Test that get returns None when cache is empty."""
    manager = CacheManager(ttl_seconds=60)
    assert manager.get() is None


def test_cache_is_stale_empty():
    """Test that is_stale returns True when cache is empty."""
    manager = CacheManager(ttl_seconds=60)
    assert manager.is_stale() is True


def test_cache_is_stale_fresh():
    """Test that is_stale returns False for a fresh entry."""
    manager = CacheManager(ttl_seconds=60)
    manager.set([])
    assert manager.is_stale() is False


def test_cache_ttl_expiration():
    """Test that cache entries expire after the configured TTL."""
    manager = CacheManager(ttl_seconds=1)
    manager.set([])
    assert manager.is_stale() is False
    
    # Wait for TTL to expire
    time.sleep(1.1)
    
    assert manager.is_stale() is True
    assert manager.get() is None