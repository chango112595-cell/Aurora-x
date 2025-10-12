#!/bin/bash
# Quick Cloudflare Tunnel - No domain needed!

echo "🚀 Aurora-X Quick Tunnel (No Domain Required)"
echo "============================================="
echo ""
echo "Starting Aurora with a free Cloudflare tunnel..."
echo ""

# Check if Aurora is running
if ! curl -s http://localhost:8000/healthz > /dev/null 2>&1; then
    echo "⚠️  Aurora not detected on port 8000"
    echo "Starting Aurora in Docker..."
    docker run -d --name aurora-quick -p 8000:8000 ghcr.io/${GITHUB_REPOSITORY:-yourusername/aurora-x}:latest
    sleep 5
fi

# Run quick tunnel (no account needed!)
echo "🌐 Creating public HTTPS tunnel..."
echo ""
cloudflared tunnel --url http://localhost:8000 --no-autoupdate

# The URL will be displayed above
# It will look like: https://random-name-abc123.trycloudflare.com