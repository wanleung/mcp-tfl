"""
Configuration module for the TfL Underground Status MCP Server.

Loads environment variables, validates constraints, and provides a typed 
configuration object accessible as a singleton.
"""

import os
from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class Settings:
    """
    Typed configuration object loaded from environment variables.
    
    Attributes:
        TFL_CACHE_TTL: Time-to-live for the in-memory cache in seconds.
        TFL_API_TIMEOUT: Timeout in seconds for TfL API HTTP requests.
        LOG_LEVEL: Application logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
    """
    TFL_CACHE_TTL: int
    TFL_API_TIMEOUT: float
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

    @classmethod
    def from_env(cls) -> "Settings":
        """Load and validate settings from environment variables."""
        try:
            cache_ttl = int(os.getenv("TFL_CACHE_TTL", "60"))
        except ValueError:
            raise ValueError("TFL_CACHE_TTL must be a valid integer") from None
        if cache_ttl <= 0:
            raise ValueError("TFL_CACHE_TTL must be a positive integer")

        try:
            api_timeout = float(os.getenv("TFL_API_TIMEOUT", "10.0"))
        except ValueError:
            raise ValueError("TFL_API_TIMEOUT must be a valid number") from None
        if api_timeout <= 0:
            raise ValueError("TFL_API_TIMEOUT must be a positive number")

        log_level = os.getenv("LOG_LEVEL", "INFO").upper()
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if log_level not in valid_levels:
            raise ValueError(f"LOG_LEVEL must be one of {valid_levels}, got '{log_level}'")

        return cls(
            TFL_CACHE_TTL=cache_ttl,
            TFL_API_TIMEOUT=api_timeout,
            LOG_LEVEL=log_level
        )


_settings: Settings | None = None


def get_settings() -> Settings:
    """Return lazily-loaded application settings."""
    global _settings
    if _settings is None:
        _settings = Settings.from_env()
    return _settings
