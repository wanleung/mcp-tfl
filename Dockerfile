FROM python:3.11-alpine AS runtime

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN addgroup -S appgroup && adduser -S appuser -G appgroup

COPY main.py ./main.py
COPY cache/ ./cache/
COPY clients/ ./clients/
COPY config/ ./config/
COPY models/ ./models/
COPY tools/ ./tools/
COPY utils/ ./utils/

RUN chown -R appuser:appgroup /app

USER appuser
ENV PYTHONUNBUFFERED=1
EXPOSE 8000
ENTRYPOINT ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

FROM runtime AS test

USER root
COPY requirements-test.txt .
RUN pip install --no-cache-dir -r requirements-test.txt

COPY scripts/ ./scripts/
COPY tests/ ./tests/
RUN chmod +x /app/scripts/run_tests.sh && chown -R appuser:appgroup /app

USER appuser
CMD ["sh", "/app/scripts/run_tests.sh"]
