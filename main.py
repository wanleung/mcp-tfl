"""
Main application entrypoint for the TfL Underground Status MCP Server.

Initializes FastAPI, configures structured logging, binds MCP transport (SSE/stdio),
registers global exception handlers, and exposes health check endpoints.
Designed to be run via `uvicorn main:app` as the Docker entrypoint.
"""

import logging
import os
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from mcp.server.fastmcp import FastMCP

from config.settings import settings
from tools.underground_status import register_tools


def setup_logging() -> None:
    """Configure structured JSON-compatible logging for the application."""
    log_format = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL),
        format=log_format,
        stream=sys.stdout
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application startup and shutdown lifecycle."""
    setup_logging()
    logging.info("TfL Underground MCP Server starting up")
    yield
    logging.info("TfL Underground MCP Server shutting down")


app = FastAPI(lifespan=lifespan)

# Initialize MCP Server
mcp = FastMCP("TfL Underground Status")
register_tools(mcp)

# Bind MCP transport
# Defaults to SSE for HTTP/ASGI deployments (Docker/uvicorn)
# Can be overridden to "stdio" for local CLI integration
transport = os.getenv("MCP_TRANSPORT", "sse").lower()
if transport == "stdio":
    logging.warning("Stdio transport requested but running in ASGI context. Falling back to SSE.")
    app.mount("/mcp", mcp.sse_app())
else:
    app.mount("/mcp", mcp.sse_app())


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all exception handler to prevent server crashes and log errors gracefully."""
    logging.error(f"Unhandled exception on {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal Server Error", "message": "An unexpected error occurred."}
    )


@app.get("/health")
async def health_check():
    """Liveness and readiness probe endpoint for container orchestration."""
    return {
        "status": "healthy",
        "cache_active": True,
        "version": "1.0.0"
    }