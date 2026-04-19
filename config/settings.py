"""Pydantic-based environment validator for the TfL MCP Server.

Loads configuration from environment variables and optional `.env` files.
Validates types, ranges, and formats at import time to fail fast on misconfiguration.
"""
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class ServiceConfiguration(BaseSettings):
    """Validates and loads service configuration from environment variables and .env files."""

    APP_ENV: Literal["test", "staging", "production", "development"] = Field(default="development")
    CACHE_TTL_SECONDS: int = Field(default=60, ge=1)
    TFL_API_BASE_URL: str = Field(default="https://api.tfl.gov.uk")
    TFL_API_TIMEOUT_MS: int = Field(default=5000, ge=100, le=30000)
    SERVER_HOST: str = Field(default="0.0.0.0")
    SERVER_PORT: int = Field(default=8000, ge=1, le=65535)
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(default="INFO")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    @field_validator("TFL_API_BASE_URL")
    @classmethod
    def validate_url(cls, v: str) -> str:
        """Ensure the API URL has a valid HTTP/HTTPS scheme."""
        if not v.startswith(("http://", "https://")):
            raise ValueError("TFL_API_BASE_URL must start with http:// or https://")
        return v


# Instantiate settings at module level to trigger validation immediately on import
settings = ServiceConfiguration()


def get_settings() -> ServiceConfiguration:
    """Return the singleton service configuration instance for backwards compatibility."""
    return settings
