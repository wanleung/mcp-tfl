# mcp-tfl

## Project Summary

**mcp-tfl** is a headless, stateless MCP (Model Context Protocol) server for real-time London Underground (TfL) line status queries. It is designed for AI client integration, exposing JSON-RPC endpoints for programmatic access to TfL data. The project leverages FastAPI, the official Python `mcp` SDK, and an async HTTP client to deliver fast, reliable responses with in-memory caching. The runtime is containerized for lightweight, production-ready deployment.

### Key Features
- **MCP Protocol Handler:** FastAPI + official `mcp` SDK for native JSON-RPC routing and async I/O.
- **Async TfL API Client:** Uses `httpx` for non-blocking communication with the TfL Unified API.
- **In-memory Caching:** `cachetools.TTLCache` (default 60s TTL) to minimize API calls and reduce latency.
- **Environment-driven Configuration:** Flexible setup for cache TTL, API timeouts, and endpoints.
- **Dockerized Runtime:** Alpine Linux base with `uvicorn` for lightweight, stateless deployment.

## Architecture & System Patterns
- **Headless & Stateless:** No web/mobile UI; optimized for AI client consumption.
- **JSON-RPC over HTTP:** MCP v1.0 compliant endpoints for real-time status queries.
- **Async-First I/O:** All external calls and MCP routing leverage Python's `asyncio`.
- **TTL Caching:** Read-through caching with fixed expiration to balance data freshness and API rate limits.
- **Environment-Driven Config:** Decouples runtime parameters from code for flexible deployment.

## Tech Stack
- **Language:** Python 3.11
- **Framework:** FastAPI + official `mcp` Python SDK
- **HTTP Client:** `httpx` (async)
- **Caching:** `cachetools` (`TTLCache`)
- **Server:** `uvicorn` (ASGI)
- **Containerization:** Docker (Alpine base)

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
- `CACHE_TTL`: Duration in seconds for in-memory cache expiration (default: 60)
- `API_TIMEOUT`: Request timeout for TfL API calls
- `TFL_API_ENDPOINT`: Base URL for TfL Unified API

Example (in `.env` or your deployment config):
```
CACHE_TTL=60
API_TIMEOUT=5
TFL_API_ENDPOINT=https://api.tfl.gov.uk/Line/Mode/tube/Status
```

### 3. Install Dependencies
```bash
pip install fastapi mcp httpx cachetools uvicorn
```

### 4. Run the Server
#### Local (development)
```bash
python main.py
```
#### Production (Docker)
```bash
docker build -t mcp-tfl .
docker run --env-file .env -p 8000:8000 mcp-tfl
```
Or use `docker-compose.test.yml` for test deployments.

## Usage

### Querying Line Status (JSON-RPC)
- The server exposes MCP v1.0 compliant JSON-RPC endpoints for querying real-time TfL Underground line statuses.
- Designed for AI clients and programmatic access; no web UI.

#### Example Request
Send a JSON-RPC request to the server's endpoint (default: `http://localhost:8000/mcp`):
```json
{
  "jsonrpc": "2.0",
  "method": "getLineStatus",
  "params": { "line": "central" },
  "id": 1
}
```

#### Example Response
```json
{
  "jsonrpc": "2.0",
  "result": {
    "line": "central",
    "status": "Good Service"
  },
  "id": 1
}
```

### Caching & Performance
- Responses are cached in-memory for 60 seconds (configurable).
- Designed for stateless, fast cold starts and minimal resource usage.

## Development & Contribution

### Current Focus
- Improving config parsing robustness and cache concurrency safety.
- Integrating `pydantic-settings` for configuration schema validation.
- Implementing custom exponential backoff for TfL API calls.

### Recent Changes
- Core MCP server built and containerized.
- Async HTTP client and in-memory cache manager implemented.
- Environment-driven configuration established.

### Known Issues & Tech Debt
- **Config Validation:** Relies on basic type casting; invalid strings crash at import time.
- **Cache Concurrency:** `TTLCache` lacks explicit locking/async-safe wrapper; potential race condition under load.
- **API Resilience:** Uses `httpx` default retries; custom exponential backoff not yet configured.

## License
See LICENSE file for details.
