# syntax=docker/dockerfile:1.6
FROM python:3.11-slim AS base
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
COPY pyproject.toml* requirements.txt* /app/ 2>/dev/null || true
RUN pip install --no-cache-dir -U pip && \
    if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi
COPY . /app
EXPOSE 8000
CMD ["python","-m","aurora_x.serve"]