# mcp-tfl

## Project Summary

**mcp-tfl** is a headless, stateless MCP (Model Context Protocol) server for real-time London Underground (TfL) line status queries. It is designed for AI client integration and exposes an MCP endpoint over SSE for programmatic access to TfL data. The project leverages FastAPI, the official Python `mcp` SDK, and an async HTTP client to deliver fast, reliable responses with in-memory caching.

### Key Features
- **MCP Protocol Handler:** FastAPI + official `mcp` SDK for MCP over SSE and async I/O.
- **Async TfL API Client:** Uses `httpx` for non-blocking communication with the TfL Unified API.
- **In-memory Caching:** `cachetools.TTLCache` (default 60s TTL) to minimize API calls and reduce latency.
- **Environment-driven Configuration:** Flexible setup for cache TTL, API timeouts, and logging levels.
- **Containerized & Profile-Driven:** Docker Compose v2 setup with isolated profiles for testing, mocking, and deployment.

## Architecture & System Patterns
- **Headless & Stateless:** No web/mobile UI; optimized for AI client consumption.
- **MCP over SSE:** FastAPI mounts `mcp.sse_app()` at `/mcp` for MCP client integrations.
- **Async-First I/O:** All external calls and MCP routing leverage Python's `asyncio`.
- **TTL Caching:** Read-through caching with fixed expiration to balance data freshness and API rate limits.
- **Environment-Driven Config:** Decouples runtime parameters from code for flexible deployment.
- **Multi-Stage Container Builds:** Uses separate `runtime` and `test` stages so test dependencies are only added for testing targets.

## Tech Stack & Dependencies
- **Language:** Python 3.11
- **Framework:** FastAPI + official `mcp` Python SDK
- **HTTP Client:** `httpx` (async)
- **Caching:** `cachetools` (`TTLCache`)
- **Server:** `uvicorn` (ASGI)
- **Containerization:** Docker (Alpine base), Docker Compose v2
- **Testing:** `pytest`, `pytest-asyncio`

### Core Dependencies
- `fastapi`
- `mcp` (official Python SDK, v1.0 compliant)
- `httpx`
- `cachetools`
- `uvicorn`

## Setup & Installation

### 1. Clone the Repository
```bash
git clone https://github.com/wanleung/mcp-tfl.git
cd mcp-tfl
```

### 2. Configure Environment Variables
Set the following environment variables (defaults shown):
- `CACHE_TTL_SECONDS`: Duration in seconds for in-memory cache expiration (default: `60`)
- `TFL_API_TIMEOUT_MS`: Request timeout for TfL API calls in milliseconds (default: `5000`)
- `TFL_API_BASE_URL`: Base URL for TfL Unified API (default: official TfL API)
- `LOG_LEVEL`: Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`; default: `INFO`)

Example (in `.env` or your deployment config):
```env
CACHE_TTL_SECONDS=60
TFL_API_TIMEOUT_MS=5000
TFL_API_BASE_URL=https://api.tfl.gov.uk
LOG_LEVEL=INFO
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Server
#### Local (development)
```bash
uvicorn main:app --reload
```

#### Container workflow (Docker Compose)
The project uses Docker Compose v2 with profile-driven environments:
```bash
# Run production-like setup
docker compose -f docker-compose.yml -f docker-compose.deploy.yml --profile deploy up -d

# Run test environment with mock API
docker compose -f docker-compose.yml -f docker-compose.test.yml --profile test up -d
```
*Note: The `Dockerfile` uses a multi-stage build on `python:3.11-alpine` for a lightweight runtime.*

## Usage & API Endpoints

### MCP Endpoint (Primary)
- **URL:** `http://localhost:8000/mcp`
- **Transport:** Server-Sent Events (SSE)
- **Protocol:** JSON-RPC 2.0 (MCP v1.0 compliant)
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

### Mock API Server (Testing)
- **Compose network URL:** `http://mock-tfl-api:8080` (when running with `--profile test`)
- This mock service is reachable from other containers on the Docker Compose network via the `mock-tfl-api` service name; it is not exposed on a host `localhost` port unless a port mapping is added in Compose.
- Lightweight FastAPI service simulating TfL Unified API responses.
- Enables offline, rate-limit-free integration testing and CI/CD validation.

### Health & Monitoring
- **Healthcheck:** Docker Compose includes native healthchecks for service readiness.
- **Logging:** Logs are written to `stdout` in a consistent plain-text format for centralized monitoring and debugging.

## Caching & Performance
- Responses are cached in-memory for 60 seconds (configurable via `CACHE_TTL_SECONDS`).
- Designed for stateless, fast cold starts and minimal resource usage.
- Read-through caching strategy balances data freshness with external API rate limits.

## Development & Testing

### Running Tests
Tests are containerized to ensure environment consistency:
```bash
docker compose -f docker-compose.yml -f docker-compose.test.yml --profile test run test-runner
# or locally:
pytest tests/ -v
```

### Docker Profiles
- `deploy`: Production-ready configuration with optimized runtime settings.
- `test`: Includes mock API server, test dependencies, and isolated networking for CI/CD.

### Current Focus & Roadmap
- Expanding automated tests around transport/error handling behavior.
- Improving deployment documentation and developer onboarding guides.
- Hardening observability and operational runbooks for production deployments.
- Extending integration coverage for retry/caching behavior under failure scenarios.

## Known Issues & Tech Debt
- Previously noted concerns around config validation, cache concurrency safety, TfL client retry backoff, Alpine test-runner shell compatibility, and Compose/FastAPI healthcheck alignment have been addressed in the current implementation.

## License
See LICENSE file for details.
