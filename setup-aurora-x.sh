#!/bin/bash
# 🚀 Aurora.X.com Setup Script
# One-command deployment for production

echo "═══════════════════════════════════════"
echo "    🌟 Aurora.X.com Setup Wizard 🌟    "
echo "═══════════════════════════════════════"
echo ""

# Check if cloudflared is installed
if ! command -v cloudflared &> /dev/null; then
    echo "📦 Installing cloudflared..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        brew install cloudflared
    else
        curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb -o cf.deb
        sudo apt install -y ./cf.deb && rm cf.deb
    fi
fi

# Step 1: Login to Cloudflare
echo "📝 Step 1: Logging into Cloudflare..."
cloudflared tunnel login

# Step 2: Create tunnel
echo ""
echo "🔧 Step 2: Creating Aurora tunnel..."
cloudflared tunnel create aurora

# Get tunnel UUID
TUNNEL_UUID=$(cloudflared tunnel list | grep aurora | awk '{print $1}')
echo "✅ Tunnel UUID: $TUNNEL_UUID"

# Step 3: Create config file
echo ""
echo "📋 Step 3: Creating config for aurora.x.com..."
mkdir -p ~/.cloudflared
cat > ~/.cloudflared/config.yml << EOF
tunnel: $TUNNEL_UUID
credentials-file: $HOME/.cloudflared/${TUNNEL_UUID}.json

ingress:
  - hostname: aurora.x.com
    service: http://localhost:8000
    originRequest:
      httpHostHeader: aurora.x.com
      connectTimeout: 10s
      noTLSVerify: true
  - service: http_status:404
EOF

echo "✅ Config saved to ~/.cloudflared/config.yml"

# Step 4: Route DNS
echo ""
echo "🌐 Step 4: Setting up DNS for aurora.x.com..."
cloudflared tunnel route dns aurora aurora.x.com

# Step 5: Docker setup
echo ""
echo "🐳 Step 5: Starting Aurora with Docker Compose..."

# Check if docker compose is available
if command -v docker compose &> /dev/null; then
    docker compose -f docker-compose.aurora-x.yml up -d
else
    docker-compose -f docker-compose.aurora-x.yml up -d
fi

# Wait for services
echo ""
echo "⏳ Waiting for services to start..."
sleep 10

# Step 6: Verify
echo ""
echo "🔍 Step 6: Verifying deployment..."
if curl -fsS http://localhost:8000/healthz > /dev/null 2>&1; then
    echo "✅ Aurora is running locally"
else
    echo "⚠️  Aurora health check failed - check Docker logs"
fi

echo ""
echo "═══════════════════════════════════════"
echo "   ✨ Aurora.X.com is LIVE! ✨         "
echo "═══════════════════════════════════════"
echo ""
echo "📱 Access Points:"
echo "  • Main App:  https://aurora.x.com"
echo "  • Dashboard: https://aurora.x.com/dashboard/demos"
echo "  • Health:    https://aurora.x.com/healthz"
echo "  • API:       https://aurora.x.com/chat"
echo ""
echo "📊 Commands:"
echo "  • View logs:    docker logs aurora-x-app"
echo "  • View tunnel:  docker logs aurora-x-tunnel"
echo "  • Stop all:     docker compose -f docker-compose.aurora-x.yml down"
echo "  • Restart:      docker compose -f docker-compose.aurora-x.yml restart"
echo ""
echo "🚀 Aurora.X.com is ready for global access!"