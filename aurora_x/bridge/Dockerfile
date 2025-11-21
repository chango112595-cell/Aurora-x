# Aurora-X Bridge Service Dockerfile
# Multi-stage build for optimized image size

FROM python:3.12-slim AS builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# ============================================
# Final stage - minimal runtime image
# ============================================
FROM python:3.12-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user 'aurora' idempotently (do nothing if it already exists)
RUN set -eux; \
    if ! id -u aurora >/dev/null 2>&1; then \
      useradd -m aurora || true; \
    fi; \
    mkdir -p /app && chown -R aurora:aurora /app

WORKDIR /app

# Copy Python packages from builder
COPY --from=builder --chown=aurora:aurora /root/.local /home/aurora/.local

# Copy application code
COPY --chown=aurora:aurora aurora_x/ ./aurora_x/
COPY --chown=aurora:aurora tools/ ./tools/

# Set Python path and user
ENV PATH=/home/aurora/.local/bin:$PATH \
    PYTHONPATH=/app \
    PYTHONUNBUFFERED=1

# Switch to non-root user
USER aurora

# Expose port
EXPOSE 5001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:5001/api/health || exit 1

# Start the bridge service
CMD ["python", "-m", "uvicorn", "aurora_x.bridge.service:app", "--host", "0.0.0.0", "--port", "5001"]
