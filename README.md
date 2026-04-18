# mcp-tfl

## Project Summary

**mcp-tfl** is a headless, stateless MCP (Model Context Protocol) server for real-time London Underground (TfL) line status queries. It is designed for AI client integration and exposes an MCP endpoint over SSE for programmatic access to TfL data. The project leverages FastAPI, the official Python `mcp` SDK, and an async HTTP client to deliver fast, reliable responses with in-memory caching.

### Key Features
- **MCP Protocol Handler:** FastAPI + official `mcp` SDK for MCP over SSE and async I/O.
- **Async TfL API Client:** Uses `httpx` for non-blocking communication with the TfL Unified API.
- **In-memory Caching:** `cachetools.TTLCache` (default 60s TTL) to minimize API calls and reduce latency.
- **Environment-driven Configuration:** Flexible setup for cache TTL, API timeouts, and logging levels.

## Architecture & System Patterns
- **Headless & Stateless:** No web/mobile UI; optimized for AI client consumption.
- **MCP over SSE:** FastAPI mounts `mcp.sse_app()` at `/mcp` for MCP client integrations.
- **Async-First I/O:** All external calls and MCP routing leverage Python's `asyncio`.
- **TTL Caching:** Read-through caching with fixed expiration to balance data freshness and API rate limits.
- **Environment-Driven Config:** Decouples runtime parameters from code for flexible deployment.

## Tech Stack
- **Language:** Python 3.11
- **Framework:** FastAPI + official `mcp` Python SDK
- **HTTP Client:** `httpx` (async)
- **Caching:** `cachetools` (`TTLCache`)
- **Server:** `uvicorn` (ASGI)

### Dependencies
- `fastapi`
- `mcp` (official Python SDK, v1.0 compliant)
- `httpx`
- `cachetools`
- `uvicorn`

## Setup

### 1. Clone the Repository
```bash
git clone https://github.com/wanleung/mcp-tfl.git
cd mcp-tfl
```

### 2. Configure Environment Variables
Set the following environment variables (defaults shown):
- `TFL_CACHE_TTL`: Duration in seconds for in-memory cache expiration (default: 60)
- `TFL_API_TIMEOUT`: Request timeout for TfL API calls (default: 10.0)
- `LOG_LEVEL`: Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`; default: `INFO`)

Example (in `.env` or your deployment config):
```
TFL_CACHE_TTL=60
TFL_API_TIMEOUT=5
LOG_LEVEL=INFO
```

### 3. Install Dependencies
```bash
pip install fastapi mcp httpx cachetools uvicorn
```

### 4. Run the Server
#### Local (development)
```bash
uvicorn main:app
```
#### Container workflow
`docker-compose.test.yml` exists for deployment testing, but a production `Dockerfile` is not currently included in this repository.

## Usage

### Querying Line Status (MCP client)
- The server exposes an MCP endpoint at `http://localhost:8000/mcp` (SSE transport).
- Designed for AI clients and programmatic access; no web UI.

#### Example Tool Invocation
Call the registered MCP tool `get_tfl_underground_status` with no arguments:
```json
{
  "name": "get_tfl_underground_status",
  "arguments": {}
}
```

#### Example Response
```json
{
  "timestamp_utc": "2026-04-18T14:00:00Z",
  "cache_status": "fresh",
  "lines": [
    {
      "line_name": "Central",
      "status_severity": 0,
      "status_description": "Good Service",
      "is_good_service": true,
      "disruption_reason": null
    }
  ],
  "summary": "All 1 Underground lines are currently running with Good Service.",
  "warnings": [],
  "error_type": null,
  "user_message": null
}
```

### Caching & Performance
- Responses are cached in-memory for 60 seconds (configurable).
- Designed for stateless, fast cold starts and minimal resource usage.

## Development & Contribution

### Current Focus
- Expanding automated tests around transport/error handling behavior.
- Improving deployment documentation and developer onboarding guides.

### Recent Changes
- Core MCP server implemented with FastAPI and MCP tooling.
- Async HTTP client and in-memory cache manager implemented.
- Environment-driven configuration established.

### Known Issues & Tech Debt
- **Container Packaging:** A production `Dockerfile` is not currently included in the repository.

## License
See LICENSE file for details.
