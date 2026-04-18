# Progress

## Completed
- [x] MCP protocol handler (FastAPI + official `mcp` SDK)
- [x] Async HTTP client (`httpx`) for TfL API integration
- [x] Configuration loader (environment-driven)
- [x] In-memory cache manager (`cachetools.TTLCache`, 60s TTL)
- [x] Dockerized runtime (Alpine + uvicorn) exposing JSON-RPC endpoints

## In Progress
- [ ] Resolve `config/settings.py` unhandled `ValueError` on invalid env var type conversion
- [ ] Implement cache manager synchronization for concurrent request safety

## Planned / Backlog
- [ ] Replace basic config casting with `pydantic-settings` schema validation
- [ ] Implement custom exponential backoff/retry logic for TfL API calls
- [ ] Finalize PR merge after code review fixes

## Known Issues & Tech Debt
- **Config Validation:** Relies on basic type casting; invalid strings crash at import time.
- **Cache Concurrency:** `TTLCache` lacks explicit locking/async-safe wrapper; potential race condition under load.
- **API Resilience:** Uses `httpx` default retries; custom exponential backoff not yet configured.