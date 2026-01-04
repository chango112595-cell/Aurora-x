# syntax=docker/dockerfile:1
FROM python:3.11-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends build-essential curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt* /tmp/
RUN if [ -f /tmp/requirements.txt ]; then \
      pip install -r /tmp/requirements.txt; \
    else \
      pip install fastapi uvicorn; \
    fi

COPY . /app
EXPOSE 8000
CMD ["uvicorn", "aurora_x.serve:app", "--host", "0.0.0.0", "--port", "8000", "--log-level", "info"]
