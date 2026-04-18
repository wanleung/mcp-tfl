# Active Context

## Current Focus
- Docker Compose v2 setup with profile-driven environments, multi-stage Dockerfile, FastAPI mock server, and containerized test runner.

## Recent Changes
- TfL Underground Status MCP Server implementation completed and containerized.
- Addressed code review feedback: config parsing robustness and cache concurrency safety.
- Added Docker Compose v2 configuration with profile-driven service definitions for test and deployment.
- Implemented multi-stage Dockerfile using `python:3.11-alpine`.
- Integrated containerized test runner (`scripts/run_tests.sh`) and lightweight FastAPI mock server for offline integration testing.
- Added Docker healthchecks and stdout structured logging.

## Immediate Next Steps
- Resolve `scripts/run_tests.sh` bash compatibility issue for Alpine base image.
- Inject test dependencies (`pytest`, `pytest-asyncio`, `httpx`) into appropriate Docker build stages.
- Align Docker Compose healthcheck configuration with actual FastAPI health route implementation.
- Standardize error handling across container entrypoints and mock API fallbacks.
- Validate multi-container networking and Compose profile isolation before production merge.