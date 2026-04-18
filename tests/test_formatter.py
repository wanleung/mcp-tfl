"""Unit tests for the Response Formatter module."""

import pytest
from utils.formatter import _parse_line_status, _build_summary, _build_warnings, format_response
from models.schemas import LineStatus, ToolResponse


def test_parse_line_status_good_service():
    """Test parsing a line with Good Service (severity 0)."""
    raw = {
        "name": "Victoria",
        "lineStatuses": [{"statusSeverity": 0, "statusSeverityDescription": "Good Service"}]
    }
    status = _parse_line_status(raw)
    assert status.line_name == "Victoria"
    assert status.status_severity == 0
    assert status.is_good_service is True
    assert status.disruption_reason is None


def test_parse_line_status_disruption():
    """Test parsing a line with disruption and a reason."""
    raw = {
        "name": "Central",
        "lineStatuses": [
            {"statusSeverity": 5, "statusSeverityDescription": "Minor Delays", "reason": "Signal failure"}
        ]
    }
    status = _parse_line_status(raw)
    assert status.line_name == "Central"
    assert status.status_severity == 5
    assert status.is_good_service is False
    assert status.disruption_reason == "Signal failure"


def test_parse_line_status_missing_fields():
    """Test parsing a line with missing status fields."""
    raw = {"name": "Unknown"}
    status = _parse_line_status(raw)
    assert status.line_name == "Unknown"
    assert status.status_severity == -1
    assert status.is_good_service is False


def test_build_summary_all_good():
    """Test summary generation when all lines are running normally."""
    lines = [
        LineStatus(line_name="A", status_severity=0, status_description="Good", is_good_service=True, disruption_reason=None),
        LineStatus(line_name="B", status_severity=0, status_description="Good", is_good_service=True, disruption_reason=None)
    ]
    summary = _build_summary(lines)
    assert summary == "All 2 Underground lines are currently running with Good Service."


def test_build_summary_some_disrupted():
    """Test summary generation when some lines are disrupted."""
    lines = [
        LineStatus(line_name="A", status_severity=0, status_description="Good", is_good_service=True, disruption_reason=None),
        LineStatus(line_name="B", status_severity=5, status_description="Bad", is_good_service=False, disruption_reason="Delay")
    ]
    summary = _build_summary(lines)
    assert "1 of 2 lines running normally" in summary
    assert "Disruptions reported on: B" in summary


def test_build_warnings():
    """Test warning extraction from disrupted lines."""
    lines = [
        LineStatus(line_name="A", status_severity=5, status_description="Bad", is_good_service=False, disruption_reason="Delay"),
        LineStatus(line_name="B", status_severity=0, status_description="Good", is_good_service=True, disruption_reason=None)
    ]
    warnings = _build_warnings(lines)
    assert len(warnings) == 1
    assert warnings[0] == "A: Delay"


def test_format_response():
    """Test full response formatting pipeline."""
    raw_data = [
        {"name": "Piccadilly", "lineStatuses": [{"statusSeverity": 0, "statusSeverityDescription": "Good Service"}]}
    ]
    cache_info = {"cache_status": "fresh"}
    resp = format_response(raw_data, cache_info)
    
    assert isinstance(resp, ToolResponse)
    assert resp.cache_status == "fresh"
    assert len(resp.lines) == 1
    assert resp.lines[0].line_name == "Piccadilly"
    assert resp.error_type is None
    assert resp.user_message is None