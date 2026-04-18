# Stage 1: Builder
FROM python:3.11-alpine AS builder

WORKDIR /build

# Install build dependencies required for compiling certain Python packages
RUN apk add --no-cache gcc musl-dev linux-headers

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-alpine

WORKDIR /app

# Copy installed dependencies and executable binaries from the builder stage
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Create a non-root user and group for secure execution
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

# Copy application source code, configuration, and utility scripts
COPY src/ ./src/
COPY config/ ./config/
COPY scripts/ ./scripts/

# Assign ownership of the application directory to the non-root user
RUN chown -R appuser:appgroup /app

# Switch to the non-root user
USER appuser

# Disable Python output buffering to ensure real-time log streaming
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

# Set entrypoint to run the FastAPI application via uvicorn
ENTRYPOINT ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]