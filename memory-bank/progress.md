# Progress

## Completed
- [x] MCP protocol handler (FastAPI + official `mcp` SDK)
- [x] Async HTTP client (`httpx`) for TfL API integration
- [x] Configuration loader (environment-driven)
- [x] In-memory cache manager (`cachetools.TTLCache`, 60s TTL)
- [x] Dockerized runtime (Alpine + uvicorn) exposing JSON-RPC endpoints
- [x] Docker Compose v2 configuration with profile-driven environments
- [x] Multi-stage Dockerfile (`python:3.11-alpine`)
- [x] FastAPI mock server for offline TfL API simulation
- [x] Containerized test runner script (`scripts/run_tests.sh`)
- [x] Docker healthchecks and stdout structured logging integration

## In Progress
- [ ] Resolve `config/settings.py` unhandled `ValueError` on invalid env var type conversion
- [ ] Implement cache manager synchronization for concurrent request safety
- [ ] Fix `run_tests.sh` bash compatibility for Alpine
- [ ] Inject test dependencies into Docker build stages
- [ ] Align Docker healthchecks with FastAPI route implementation
- [ ] Standardize error handling in container entrypoints and mock routing

## Planned / Backlog
- [ ] Replace basic config casting with `pydantic-settings` schema validation
- [ ] Implement custom exponential backoff/retry logic for TfL API calls
- [ ] Finalize PR merge after code review fixes
- [ ] Validate multi-container networking and Compose profile isolation

## Known Issues & Tech Debt
- **Config Validation:** Relies on basic type casting; invalid strings crash at import time.
- **Cache Concurrency:** `TTLCache` lacks explicit locking/async-safe wrapper; potential race condition under load.
- **API Resilience:** Uses `httpx` default retries; custom exponential backoff not yet configured.
- **Alpine Compatibility:** Test runner script requires bash, which is absent in the Alpine base image.
- **Test Dependency Isolation:** Dockerfile omits test dependencies (`pytest`, `pytest-asyncio`, `httpx`), breaking the test runner.
- **Healthcheck Mismatch:** Compose healthcheck assumptions do not align with the actual FastAPI route.
- **Error Handling:** Container entrypoints and mock routing lack standardized error handling and fallbacks.