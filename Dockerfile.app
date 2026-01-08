FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PORT=8000 AURORA_DEFAULT_LANG=python
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends build-essential curl && rm -rf /var/lib/apt/lists/*
COPY . /app
RUN pip install --upgrade pip && pip install -e . && pip cache purge
EXPOSE 8000
HEALTHCHECK --interval=20s --timeout=3s --retries=6 CMD curl -fsS http://127.0.0.1:${PORT}/healthz || exit 1
CMD ["python","-m","aurora_x.serve"]
