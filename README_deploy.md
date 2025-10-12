# 🚀 Aurora.X.com Deployment Guide

Deploy Aurora at `aurora.x.com` with Cloudflare Tunnel in 5 minutes.

## Prerequisites
- Docker & Docker Compose installed
- Cloudflare account (free tier works)
- Domain configured in Cloudflare DNS

## 🎯 Quick Deploy (Copy-Paste Commands)

### Step 1: Install Cloudflared
```bash
# macOS
brew install cloudflared

# Linux (Ubuntu/Debian)
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb -o cf.deb
sudo apt install -y ./cf.deb && rm cf.deb

# Linux (Other)
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o /usr/local/bin/cloudflared
chmod +x /usr/local/bin/cloudflared
```

### Step 2: Create Tunnel
```bash
# Login to Cloudflare (opens browser)
cloudflared tunnel login

# Create named tunnel
cloudflared tunnel create aurora

# Note the UUID (you'll see output like):
# Created tunnel aurora with id: abc123-def456-ghi789
```

### Step 3: Configure Tunnel
```bash
# Create config directory
mkdir -p ~/.cloudflared

# Get your tunnel UUID
TUNNEL_UUID=$(cloudflared tunnel list | grep aurora | awk '{print $1}')

# Create config file
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
```

### Step 4: Route DNS
```bash
# Map aurora.x.com to your tunnel
cloudflared tunnel route dns aurora aurora.x.com
```

### Step 5: Create Docker Compose
```bash
# Save as docker-compose.yml
cat > docker-compose.yml << 'EOF'
services:
  aurora:
    image: ghcr.io/<OWNER>/<REPO>:latest  # ← Replace with your image
    container_name: aurora
    environment:
      PORT: "8000"
      AURORA_DEFAULT_LANG: "python"
    ports:
      - "8000:8000"
    healthcheck:
      test: ["CMD", "curl", "-fsS", "http://127.0.0.1:8000/healthz"]
      interval: 20s
      timeout: 5s
      retries: 6
    restart: unless-stopped

  cloudflared:
    image: cloudflare/cloudflared:latest
    container_name: cf-tunnel
    command: tunnel run aurora
    volumes:
      - ~/.cloudflared:/etc/cloudflared:ro
    network_mode: host
    depends_on:
      aurora:
        condition: service_healthy
    restart: unless-stopped
EOF
```

### Step 6: Deploy
```bash
# Start both containers
docker compose up -d

# Watch logs (optional)
docker compose logs -f
```

## ✅ Verify Deployment

```bash
# Check local health
curl http://localhost:8000/healthz

# Check public access
curl https://aurora.x.com/healthz

# Open in browser
open https://aurora.x.com/dashboard/demos
```

## 📊 Management Commands

### View Status
```bash
# Check containers
docker compose ps

# View logs
docker compose logs aurora        # App logs
docker compose logs cloudflared   # Tunnel logs
docker compose logs -f            # Follow all logs
```

### Update Aurora
```bash
# Pull latest image
docker compose pull aurora

# Recreate with new version
docker compose up -d aurora
```

### Stop/Start
```bash
# Stop all services
docker compose down

# Stop but keep data
docker compose stop

# Restart services
docker compose restart
```

## 🔄 Rollback

### Quick Rollback to Previous Version
```bash
# Tag current as backup
docker tag ghcr.io/<OWNER>/<REPO>:latest ghcr.io/<OWNER>/<REPO>:backup

# Pull specific version
docker pull ghcr.io/<OWNER>/<REPO>:sha-abc123  # Use commit SHA

# Update compose to use specific version
sed -i 's/:latest/:sha-abc123/g' docker-compose.yml

# Redeploy
docker compose up -d
```

### Emergency Recovery
```bash
# Stop everything
docker compose down

# Remove containers and networks
docker system prune -f

# Fresh deploy
docker compose up -d
```

## 🔍 Troubleshooting

### Tunnel Not Connecting
```bash
# Check tunnel status
docker logs cf-tunnel

# Verify credentials exist
ls -la ~/.cloudflared/*.json

# Test tunnel manually
cloudflared tunnel run aurora
```

### Aurora Not Responding
```bash
# Check health
docker exec aurora curl http://localhost:8000/healthz

# Restart Aurora only
docker compose restart aurora

# Check resource usage
docker stats
```

### DNS Issues
```bash
# Verify DNS record
dig aurora.x.com

# Should show CNAME to:
# <tunnel-uuid>.cfargotunnel.com
```

## 🔐 Security Notes

- Tunnel credentials in `~/.cloudflared/` should be kept secure
- Consider using Docker secrets for production
- Enable Cloudflare Access for authentication
- Regular backups of tunnel credentials recommended

## 📱 Mobile Access

Once deployed at aurora.x.com:
1. Open on phone browser
2. **iOS**: Safari → Share → Add to Home Screen
3. **Android**: Chrome → Menu → Install App

## 🎉 Success Checklist

- [ ] Cloudflared installed
- [ ] Tunnel created with UUID
- [ ] DNS routed to aurora.x.com
- [ ] Docker Compose running
- [ ] Health check passing
- [ ] Public URL accessible
- [ ] Mobile PWA working

---

**Need help?** The containers auto-restart, so Aurora.X.com stays live 24/7 at `https://aurora.x.com`