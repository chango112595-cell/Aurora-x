# Aurora Containerization Guide

## Prerequisites

**Install Docker Desktop for Windows:**
1. Download from: https://www.docker.com/products/docker-desktop
2. Install Docker Desktop
3. Start Docker Desktop (wait for "Docker Desktop is running")
4. Ensure WSL 2 is enabled (Docker will prompt if needed)

## Quick Start (Without Docker)

Aurora runs perfectly without Docker! Just use:

```bash
npm run dev
```

Visit: http://localhost:5000/chat

## With Docker (Optional)

Once Docker Desktop is running:

```bash
# Build and start all services
docker-compose up --build

# Or run in background
docker-compose up -d --build

# Stop all services
docker-compose down

# View logs
docker-compose logs -f aurora
```

## Simple Single-Container Setup

If you want just Aurora containerized (simpler):

```bash
# Build the image
docker build -t aurora-ai .

# Run the container
docker run -p 5000:5000 --name aurora aurora-ai

# Stop
docker stop aurora
docker rm aurora
```

## Benefits of Containerization

- ✅ Isolated environment (no conflicts)
- ✅ Auto-restart on crash
- ✅ Easy deployment to cloud
- ✅ Consistent across machines
- ✅ Version control for deployments

## Current Status

Aurora is **fully functional** without Docker at:
- http://localhost:5000/chat (Next.js)
- Python core working perfectly
- Memory persistence enabled

Docker is **optional** - use it when you want to deploy to production or need isolation.
