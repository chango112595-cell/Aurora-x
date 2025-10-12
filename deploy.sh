#!/bin/bash
# 🚀 Aurora-X One-Command VPS Deployment
# Usage: bash deploy.sh

set -e

echo "════════════════════════════════════════════════════════"
echo "          🌟 Aurora-X VPS Deployment Script 🌟          "
echo "════════════════════════════════════════════════════════"
echo ""

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Step 1: Install Docker if needed
if ! command -v docker &> /dev/null; then
    echo -e "${BLUE}📦 Installing Docker...${NC}"
    sudo apt-get update -y
    sudo apt-get install -y ca-certificates curl gnupg
    sudo install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
      https://download.docker.com/linux/ubuntu $(. /etc/os-release; echo $VERSION_CODENAME) stable" \
      | sudo tee /etc/apt/sources.list.d/docker.list >/dev/null
    sudo apt-get update -y
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    
    # Add current user to docker group
    sudo usermod -aG docker $USER
    echo -e "${GREEN}✅ Docker installed${NC}"
else
    echo -e "${GREEN}✅ Docker already installed${NC}"
fi

# Step 2: Create project directory
echo -e "${BLUE}📁 Setting up project directory...${NC}"
mkdir -p ~/aurora-x
cd ~/aurora-x

# Step 3: Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚙️ Creating environment configuration...${NC}"
    cat > .env << 'EOF'
# Cloudflare Tunnel Token (REQUIRED)
# Get from: Cloudflare Dashboard > Zero Trust > Networks > Tunnels
CF_TUNNEL_TOKEN=

# GitHub Repository (for image pulls)
GITHUB_REPOSITORY=yourusername/aurora-x

# Optional: Security & Monitoring
AURORA_HEALTH_TOKEN=secure123
DISCORD_WEBHOOK_URL=

# Optional: Custom configuration
AURORA_DEFAULT_LANG=python
AURORA_ENV=production
EOF
    echo -e "${YELLOW}⚠️  IMPORTANT: Edit .env and add your CF_TUNNEL_TOKEN${NC}"
    echo -e "${YELLOW}   Get it from Cloudflare Dashboard > Zero Trust > Tunnels${NC}"
fi

# Step 4: Download docker-compose.yml
echo -e "${BLUE}📥 Downloading docker-compose.yml...${NC}"
cat > docker-compose.yml << 'EOF'
# Aurora-X Production Stack with Cloudflare Tunnel
services:
  aurora:
    image: ghcr.io/${GITHUB_REPOSITORY:-yourusername/aurora-x}:latest
    container_name: aurora_x
    environment:
      PORT: "8000"
      AURORA_DEFAULT_LANG: "${AURORA_DEFAULT_LANG:-python}"
      AURORA_ENV: "${AURORA_ENV:-production}"
      AURORA_HEALTH_TOKEN: "${AURORA_HEALTH_TOKEN:-secure123}"
      DISCORD_WEBHOOK_URL: "${DISCORD_WEBHOOK_URL:-}"
    ports:
      - "127.0.0.1:8000:8000"
    healthcheck:
      test: ["CMD", "curl", "-fsS", "http://localhost:8000/healthz"]
      interval: 15s
      timeout: 5s
      retries: 10
      start_period: 30s
    restart: unless-stopped
    volumes:
      - ./aurora_runs:/app/runs
      - ./aurora_data:/app/data
    networks:
      - aurora_net

  cloudflared:
    image: cloudflare/cloudflared:latest
    container_name: aurora_cf_tunnel
    depends_on:
      aurora:
        condition: service_healthy
    command: tunnel run
    environment:
      TUNNEL_TOKEN: "${CF_TUNNEL_TOKEN}"
    restart: unless-stopped
    networks:
      - aurora_net

networks:
  aurora_net:
    driver: bridge
EOF

echo -e "${GREEN}✅ Configuration files created${NC}"

# Step 5: Check if .env has token
if grep -q "^CF_TUNNEL_TOKEN=$" .env 2>/dev/null; then
    echo ""
    echo -e "${YELLOW}════════════════════════════════════════════════════════${NC}"
    echo -e "${YELLOW}         ⚠️  ACTION REQUIRED - ADD TUNNEL TOKEN ⚠️        ${NC}"
    echo -e "${YELLOW}════════════════════════════════════════════════════════${NC}"
    echo ""
    echo "1. Go to: https://one.dash.cloudflare.com/zero-trust/tunnels"
    echo "2. Click 'Create a tunnel' > Choose 'Cloudflared'"
    echo "3. Name it 'aurora-x' > Save tunnel"
    echo "4. Click 'Configure' > Copy the token"
    echo "5. Edit ~/aurora-x/.env and paste the token"
    echo ""
    echo "Then run: docker compose up -d"
    exit 0
fi

# Step 6: Deploy
echo -e "${BLUE}🚀 Starting Aurora-X...${NC}"
docker compose pull
docker compose up -d

# Step 7: Wait for health
echo -e "${BLUE}⏳ Waiting for services to start...${NC}"
sleep 10

# Step 8: Verify
echo ""
if curl -fsS http://localhost:8000/healthz > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Aurora is running!${NC}"
else
    echo -e "${YELLOW}⚠️  Aurora health check failed - checking logs...${NC}"
    docker compose logs --tail=20 aurora
fi

echo ""
echo "════════════════════════════════════════════════════════"
echo -e "${GREEN}         ✨ Aurora-X Deployment Complete! ✨           ${NC}"
echo "════════════════════════════════════════════════════════"
echo ""
echo "📋 Next Steps:"
echo "1. In Cloudflare Tunnel > Public Hostnames:"
echo "   • Subdomain: aurora (or your choice)"
echo "   • Domain: yourdomain.com"
echo "   • Service: http://aurora:8000"
echo ""
echo "2. Access your site:"
echo "   • https://aurora.yourdomain.com/healthz"
echo "   • https://aurora.yourdomain.com/dashboard/demos"
echo "   • https://aurora.yourdomain.com/chat"
echo ""
echo "📊 Management Commands:"
echo "   • View logs:  docker compose logs -f"
echo "   • Stop:       docker compose down"
echo "   • Update:     docker compose pull && docker compose up -d"
echo "   • Status:     docker compose ps"