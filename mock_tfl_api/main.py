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
with open(RESPONSES_DIR / "lines_status.json", "r", encoding="utf-8") as f:
    LINES_STATUS = json.load(f)
with open(RESPONSES_DIR / "disruptions.json", "r", encoding="utf-8") as f:
    DISRUPTIONS = json.load(f)

# Test configuration injected via environment variables
MOCK_DELAY_MS = int(os.getenv("MOCK_DELAY_MS", "0"))
MOCK_ERROR_RATE = float(os.getenv("MOCK_ERROR_RATE", "0.0"))


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
async def get_line_status():
    """Return simulated TfL line status payload matching the unified API schema."""
    return LINES_STATUS


@app.get("/Line/{line_id}/Disruption")
async def get_line_disruption(line_id: str):
    """Return simulated disruption payload for a specific line ID."""
    disruptions = DISRUPTIONS.get(line_id.lower(), [])
    return {"disruptions": disruptions}