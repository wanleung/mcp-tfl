"""
Response formatter module for the TfL Underground Status MCP Server.

Transforms raw API payloads into LineStatus objects, maps severity codes,
extracts disruption reasons, and builds commuter-friendly summaries.
"""

from datetime import datetime, timezone
from typing import Any

from models.schemas import LineStatus, ToolResponse


def _parse_line_status(raw_line: dict[str, Any] | LineStatus) -> LineStatus:
    """Parses a single raw line dictionary from the TfL API into a LineStatus model."""
    if isinstance(raw_line, LineStatus):
        return raw_line

    line_name = raw_line.get("name", "Unknown Line")
    line_statuses = raw_line.get("lineStatuses", [])
    
    status_severity = -1
    status_description = "Unknown Status"
    disruption_reason = None
    
    if line_statuses:
        primary_status = line_statuses[0]
        status_severity = primary_status.get("statusSeverity", -1)
        status_description = primary_status.get("statusSeverityDescription", "Unknown Status")
        reason = primary_status.get("reason")
        disruption_reason = reason if reason else None

    # Per system design: maps statusSeverity === 0 to "Good Service"
    is_good_service = (status_severity == 0)

    return LineStatus(
        line_name=line_name,
        status_severity=status_severity,
        status_description=status_description,
        is_good_service=is_good_service,
        disruption_reason=disruption_reason
    )


def _build_summary(lines: list[LineStatus]) -> str:
    """Generates a concise, commuter-friendly summary of the network status."""
    good_lines = [l.line_name for l in lines if l.is_good_service]
    disrupted_lines = [l.line_name for l in lines if not l.is_good_service]
    
    total = len(lines)
    if not disrupted_lines:
        return f"All {total} Underground lines are currently running with Good Service."
        
    disrupted_str = ", ".join(disrupted_lines)
    return f"{len(good_lines)} of {total} lines running normally. Disruptions reported on: {disrupted_str}."


def _build_warnings(lines: list[LineStatus]) -> list[str]:
    """Extracts operational warnings or advisories from disrupted lines."""
    warnings = []
    for line in lines:
        if not line.is_good_service and line.disruption_reason:
            warnings.append(f"{line.line_name}: {line.disruption_reason}")
    return warnings


def format_response(
    raw_data: list[dict[str, Any] | LineStatus],
    cache_info: dict[str, Any] | None = None,
    cache_status: str | None = None,
    error_type: str | None = None,
    user_message: str | None = None
) -> ToolResponse:
    """
    Transforms raw TfL API payloads into a standardized ToolResponse.

    Args:
        raw_data: List of raw line status dictionaries from the TfL API.
        cache_info: Optional dictionary containing cache metadata, including 'cache_status'.
        cache_status: Optional cache status override.
        error_type: Optional machine-readable error code.
        user_message: Optional user-facing error message.

    Returns:
        ToolResponse: Formatted response ready for MCP client consumption.
    """
    lines = [_parse_line_status(line) for line in raw_data] if raw_data else []
    
    summary = _build_summary(lines)
    warnings = _build_warnings(lines)
    
    return ToolResponse(
        timestamp_utc=datetime.now(timezone.utc),
        cache_status=cache_status if cache_status is not None else (cache_info or {}).get("cache_status", "fresh"),
        lines=lines,
        summary=summary,
        warnings=warnings,
        error_type=error_type,
        user_message=user_message
    )
