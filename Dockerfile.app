# Production multi-arch Dockerfile (optimized for size & performance)
FROM python:3.11-slim as builder
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /build
# Build dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*
COPY setup.py pyproject.toml ./
COPY aurora_x ./aurora_x
RUN pip install --upgrade pip && pip wheel --no-cache-dir --no-deps --wheel-dir /wheels .

# Final stage - minimal runtime
FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PORT=8000 AURORA_DEFAULT_LANG=python
WORKDIR /app

# Runtime deps only (no build tools)
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/* && \
    useradd -m -s /bin/bash aurora && \
    mkdir -p /app/runs /app/aurora_x/static && \
    chown -R aurora:aurora /app

# Copy wheels and install
COPY --from=builder /wheels /wheels
RUN pip install --no-cache /wheels/*.whl && rm -rf /wheels

# Copy app code
COPY --chown=aurora:aurora aurora_x /app/aurora_x
COPY --chown=aurora:aurora Makefile /app/

USER aurora
EXPOSE 8000

# Health check for container orchestration
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:${PORT}/healthz || exit 1

CMD ["python", "-m", "aurora_x.serve"]