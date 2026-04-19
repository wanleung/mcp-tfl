"""Mock TfL Unified API service for deterministic integration testing."""
import asyncio
import json
import os
import random
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI(title="Mock TfL Unified API", version="1.0.0")

# Load canned response payloads
RESPONSES_DIR = Path(__file__).parent / "responses"


def _load_json(filename: str):
    filepath = RESPONSES_DIR / filename
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError as exc:
        raise RuntimeError(f"Mock response file not found: {filepath}") from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Invalid JSON in {filepath}: {exc}") from exc


LINES_STATUS = _load_json("lines_status.json")
DISRUPTIONS = _load_json("disruptions.json")


def _parse_non_negative_int(name: str, default: int = 0) -> int:
    value = os.getenv(name, str(default))
    try:
        return max(0, int(value))
    except ValueError:
        return default


def _parse_probability(name: str, default: float = 0.0) -> float:
    value = os.getenv(name, str(default))
    try:
        return max(0.0, min(1.0, float(value)))
    except ValueError:
        return default

# Test configuration injected via environment variables
MOCK_DELAY_MS = _parse_non_negative_int("MOCK_DELAY_MS", 0)
MOCK_ERROR_RATE = _parse_probability("MOCK_ERROR_RATE", 0.0)


@app.middleware("http")
async def simulate_network_conditions(request: Request, call_next):
    """Inject configurable latency and random transient failures for testing."""
    if MOCK_DELAY_MS > 0:
        await asyncio.sleep(MOCK_DELAY_MS / 1000.0)

    if MOCK_ERROR_RATE > 0.0 and random.random() < MOCK_ERROR_RATE:
        return JSONResponse(
            status_code=503,
            content={"error": "Service Unavailable", "message": "Simulated transient failure"}
        )

    response = await call_next(request)
    return response


@app.get("/health")
async def health_check():
    """Liveness probe for the mock service."""
    return {"status": "ok", "env": os.getenv("APP_ENV", "test")}


@app.get("/Line/Status")
@app.get("/Line/Mode/tube/Status")
async def get_line_status():
    """Return simulated TfL line status payload matching the unified API schema."""
    return LINES_STATUS


@app.get("/Line/{line_id}/Disruption")
async def get_line_disruption(line_id: str):
    """Return simulated disruption payload for a specific line ID."""
    disruptions = DISRUPTIONS.get(line_id.lower(), [])
    return {"disruptions": disruptions}
