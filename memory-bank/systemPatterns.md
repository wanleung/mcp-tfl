# System Patterns

## Architecture
- **Headless & Stateless:** Optimized for AI client integration; no web/mobile UI.
- **JSON-RPC over HTTP:** Exposes MCP v1.0 compliant endpoints for AI assistants to query real-time TfL line statuses.
- **Containerized Runtime:** Alpine Linux base with `uvicorn` for lightweight, production-ready deployment.
- **Profile-Driven Orchestration:** Docker Compose v2 architecture isolates test, mock, and production workloads via service profiles.

## Core Modules
- **MCP Protocol Handler:** Built using FastAPI and the official Python `mcp` SDK for native JSON-RPC routing and async I/O.
- **API Client:** `httpx`-based async HTTP client for communicating with the TfL Unified API.
- **Cache Manager:** In-memory `cachetools.TTLCache` with a 60-second TTL to minimize external API calls and reduce latency.
- **Configuration Loader:** Environment-driven setup for cache TTL, API timeouts, and endpoint URLs.
- **Mock API Server:** Lightweight FastAPI service simulating TfL Unified API responses for offline, rate-limit-free integration testing.

## Design Patterns
- **Async-First I/O:** All external calls and MCP routing leverage Python's `asyncio` for non-blocking execution.
- **TTL Caching:** Read-through caching strategy with fixed expiration to balance data freshness and API rate limits.
- **Environment-Driven Config:** Decouples runtime parameters from code, enabling flexible deployment across environments.
- **Multi-Stage Container Builds:** Separates dependency installation and runtime layers to minimize final image footprint.
- **Zero-Dependency Readiness Probes:** Relies on native Docker healthchecks for service state validation without external tooling.