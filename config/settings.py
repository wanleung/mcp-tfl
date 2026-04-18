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
        cache_ttl = int(os.getenv("TFL_CACHE_TTL", "60"))
        if cache_ttl <= 0:
            raise ValueError("TFL_CACHE_TTL must be a positive integer")

        api_timeout = float(os.getenv("TFL_API_TIMEOUT", "10.0"))
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


# Singleton instance for global access throughout the application
settings = Settings.from_env()