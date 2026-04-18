FROM python:3.11-alpine

WORKDIR /app

# Install runtime dependencies directly to keep the image minimal
RUN pip install --no-cache-dir fastapi uvicorn

# Copy application code and static response payloads
COPY . .

EXPOSE 8080

# Run the mock API server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]