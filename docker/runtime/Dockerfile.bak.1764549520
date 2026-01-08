FROM python:3.11-slim
WORKDIR /app
COPY ../../packs ./packs
COPY ../../installer ./installer
COPY ../../tools ./tools
RUN pip install --no-cache-dir aiohttp fastapi uvicorn
CMD ["python3", "installer/launcher_runtime.py"]
