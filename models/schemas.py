"""Pydantic data models for TfL Underground Status MCP Server.

Defines schemas for line status, cache entries, and tool responses
with validation rules and UTC-aware datetime handling.
"""

from datetime import datetime, timezone
from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator


def _ensure_utc(value: datetime) -> datetime:
    """Convert naive datetimes to UTC and ensure timezone-aware datetimes are in UTC."""
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


class LineStatus(BaseModel):
    """Represents the operational status of a single TfL Underground line."""

    line_name: str = Field(
        ..., min_length=1, description="Name of the Underground line (e.g., 'Central')"
    )
    status_severity: int = Field(
        ...,
        ge=-1,
        le=10,
        description="TfL status severity code (-1 unknown/unavailable, 0 indicates Good Service)"
    )
    status_description: str = Field(
        ..., min_length=1, description="Human-readable status description provided by TfL"
    )
    is_good_service: bool = Field(
        ..., description="Boolean flag indicating if the line is running normally"
    )
    disruption_reason: Optional[str] = Field(
        None, description="Detailed reason for disruption, if applicable"
    )


class CacheEntry(BaseModel):
    """Represents a cached snapshot of TfL line statuses with metadata."""

    data: list[LineStatus] = Field(..., description="List of line status objects")
    fetched_at_utc: datetime = Field(
        ..., description="UTC timestamp when the data was originally fetched"
    )
    expires_at_utc: datetime = Field(
        ..., description="UTC timestamp when this cache entry becomes invalid"
    )
    ttl_remaining_seconds: int = Field(
        ..., ge=0, description="Seconds remaining until the cache entry expires"
    )

    @field_validator("fetched_at_utc", "expires_at_utc", mode="before")
    @classmethod
    def _validate_utc_timestamps(cls, value: datetime) -> datetime:
        return _ensure_utc(value)


class ToolResponse(BaseModel):
    """Standardized response payload returned to MCP clients."""

    timestamp_utc: datetime = Field(
        ..., description="UTC timestamp when this response was generated"
    )
    cache_status: Literal["fresh", "cached", "stale"] = Field(
        ..., description="Indicates whether the data was freshly fetched, cached, or stale"
    )
    lines: list[LineStatus] = Field(..., description="List of current line statuses")
    summary: str = Field(
        ..., min_length=1, description="Concise, commuter-friendly summary of network status"
    )
    warnings: list[str] = Field(
        default_factory=list, description="List of operational warnings or advisories"
    )
    error_type: Optional[str] = Field(
        None, description="Machine-readable error code if the request encountered issues"
    )
    user_message: Optional[str] = Field(
        None, description="Human-readable message for the end user, especially on errors"
    )

    @field_validator("timestamp_utc", mode="before")
    @classmethod
    def _validate_utc_timestamp(cls, value: datetime) -> datetime:
        return _ensure_utc(value)
