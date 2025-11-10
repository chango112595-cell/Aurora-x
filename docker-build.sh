#!/bin/bash
# Aurora-X Docker Build Script
# Builds all service images

set -e  # Exit on error

echo "🐳 Building Aurora-X Docker Images..."
echo "======================================"

# Colors for output
GREEN='\033[0.32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Build each service
echo -e "${BLUE}Building Backend (Node.js)...${NC}"
docker build -f Dockerfile.backend -t aurora-backend:latest .

echo -e "${BLUE}Building Bridge Service (Python/FastAPI)...${NC}"
docker build -f aurora_x/bridge/Dockerfile -t aurora-bridge:latest .

echo -e "${BLUE}Building Self-Learn Server (Python/FastAPI)...${NC}"
docker build -f Dockerfile.self-learn -t aurora-self-learn:latest .

echo -e "${BLUE}Building Chat Server (Python/Flask)...${NC}"
docker build -f Dockerfile.chat -t aurora-chat:latest .

echo -e "${BLUE}Building Frontend (React/Vite)...${NC}"
docker build -f Dockerfile.frontend -t aurora-frontend:latest .

echo ""
echo -e "${GREEN}✅ All images built successfully!${NC}"
echo ""
echo "Image sizes:"
docker images | grep "aurora-" | awk '{print $1 "\t" $7 " " $8}'

echo ""
echo "Next steps:"
echo "  - Run: docker-compose up -d"
echo "  - Check status: docker-compose ps"
echo "  - View logs: docker-compose logs -f"
