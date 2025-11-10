#!/bin/bash
# Aurora-X Docker Run Script
# Starts all services with docker-compose

set -e

echo "🚀 Starting Aurora-X Services..."
echo "================================"

# Check if docker-compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose not found. Please install it first."
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  No .env file found. Creating default .env..."
    cat > .env << 'EOF'
# Aurora-X Environment Variables

# Node.js Backend
NODE_ENV=production
DATABASE_URL=postgresql://aurora:aurora_secure_password@db:5432/aurora_x

# PostgreSQL
POSTGRES_DB=aurora_x
POSTGRES_USER=aurora
POSTGRES_PASSWORD=aurora_secure_password

# Optional: Cloudflare Tunnel (for production)
# CF_TUNNEL_TOKEN=your_token_here
EOF
    echo "✅ Default .env created. Please review and customize it."
fi

# Start services
echo "Starting all services..."
docker-compose up -d

echo ""
echo "⏳ Waiting for services to be healthy..."
sleep 10

echo ""
echo "📊 Service Status:"
docker-compose ps

echo ""
echo "✅ Aurora-X is running!"
echo ""
echo "Access points:"
echo "  - Frontend:    http://localhost:5173"
echo "  - Backend API: http://localhost:5000"
echo "  - Bridge:      http://localhost:5001"
echo "  - Self-Learn:  http://localhost:5002"
echo "  - Chat:        http://localhost:5003"
echo "  - Database:    localhost:5432"
echo ""
echo "Useful commands:"
echo "  - View logs:      docker-compose logs -f"
echo "  - Stop services:  docker-compose down"
echo "  - Restart:        docker-compose restart"
echo "  - Check health:   docker-compose ps"
