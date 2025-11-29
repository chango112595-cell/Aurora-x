#!/bin/bash
# Quick Cloudflare Tunnel setup for Aurora-X

# Configuration (edit these)
DOMAIN="yourdomain.com"  # Change to your actual domain
SUBDOMAIN="aurora"        # Change if you want different subdomain
TUNNEL_NAME="aurora-x"

echo "🚀 Aurora-X Cloudflare Tunnel Setup"
echo "===================================="
echo ""
echo "Setting up: https://${SUBDOMAIN}.${DOMAIN}"
echo ""

# Check if cloudflared is installed
if ! command -v cloudflared &> /dev/null; then
    echo "⚠️  cloudflared not found. Installing..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        brew install cloudflared
    else
        curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb -o cf.deb
        sudo apt install -y ./cf.deb
        rm cf.deb
    fi
fi

# Login to Cloudflare
echo "📝 Step 1: Logging into Cloudflare..."
cloudflared tunnel login

# Create tunnel
echo "🔧 Step 2: Creating tunnel..."
cloudflared tunnel create $TUNNEL_NAME

# Get tunnel UUID
TUNNEL_UUID=$(cloudflared tunnel list | grep $TUNNEL_NAME | awk '{print $1}')
echo "✅ Tunnel UUID: $TUNNEL_UUID"

# Create config file
echo "📋 Step 3: Creating config file..."
cat > ~/.cloudflared/config.yml << EOF
tunnel: $TUNNEL_UUID
credentials-file: $HOME/.cloudflared/${TUNNEL_UUID}.json

ingress:
  - hostname: ${SUBDOMAIN}.${DOMAIN}
    service: http://localhost:8000
    originRequest:
      httpHostHeader: ${SUBDOMAIN}.${DOMAIN}
      connectTimeout: 10s
      noTLSVerify: true
  - service: http_status:404
EOF

echo "✅ Config saved to ~/.cloudflared/config.yml"

# Route DNS
echo "🌐 Step 4: Setting up DNS route..."
cloudflared tunnel route dns $TUNNEL_NAME ${SUBDOMAIN}.${DOMAIN}

echo ""
echo "✅ Setup complete!"
echo ""
echo "To run the tunnel:"
echo "  cloudflared tunnel run $TUNNEL_NAME"
echo ""
echo "Or with Docker Compose:"
echo "  docker-compose -f docker-compose.cloudflare.yml up -d"
echo ""
echo "📱 Your Aurora will be accessible at:"
echo "  https://${SUBDOMAIN}.${DOMAIN}"