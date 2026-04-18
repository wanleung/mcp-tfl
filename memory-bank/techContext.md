# Tech Context

## Tech Stack
- **Language:** Python 3.11
- **Framework:** FastAPI + official `mcp` Python SDK
- **HTTP Client:** `httpx` (async)
- **Caching:** `cachetools` (`TTLCache`)
- **Server:** `uvicorn` (ASGI)
- **Containerization:** Docker (Alpine base)

## Dependencies
- `fastapi`
- `mcp` (official Python SDK, v1.0 compliant)
- `httpx`
- `cachetools`
- `uvicorn`

## Environment Variables
- `CACHE_TTL`: Duration in seconds for in-memory cache expiration (default: 60)
- `API_TIMEOUT`: Request timeout for TfL API calls
- `TFL_API_ENDPOINT`: Base URL for TfL Unified API
- *(Note: Current implementation lacks robust type validation for these variables)*

## Infrastructure & Constraints
- **Stateless Deployment:** No persistent storage or database; relies entirely on in-memory cache and external API.
- **Headless Operation:** Designed exclusively for programmatic/AI client consumption via JSON-RPC.
- **Lightweight Runtime:** Alpine-based Docker image optimized for minimal footprint and fast cold starts.