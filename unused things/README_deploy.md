# 🚀 Aurora-X Production Deployment Guide

Deploy Aurora-X with Cloudflare Tunnel for zero-exposed-ports HTTPS access.

## 📋 Prerequisites

- **VPS/Server**: Ubuntu 22.04+ (DigitalOcean, AWS, Hetzner, etc.)
- **Domain**: Configured in Cloudflare (free plan works)
- **Docker**: Will be installed by script if missing

> **Note**: This requires a real server. Replit can't run Docker Compose or Cloudflare Tunnels reliably.

## 🎯 Quick Deploy (5 Minutes)

### Option A: One-Command Script

```bash
# SSH to your server, then:
curl -sSL https://raw.githubusercontent.com/yourusername/aurora-x/main/deploy.sh | bash
```

### Option B: Manual Setup

#### 1. Install Docker (if needed)

```bash
# Update system
sudo apt-get update -y

# Install Docker
sudo apt-get install -y ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(. /etc/os-release; echo $VERSION_CODENAME) stable" | sudo tee /etc/apt/sources.list.d/docker.list >/dev/null
sudo apt-get update -y
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker
```

#### 2. Create Cloudflare Tunnel

1. Go to [Cloudflare Zero Trust Dashboard](https://one.dash.cloudflare.com/zero-trust/tunnels)
2. Click **Create a tunnel**
3. Choose **Cloudflared**
4. Name it `aurora-x`
5. Click **Save tunnel**
6. Under **Install and run a connector**, copy the token

#### 3. Setup Aurora-X

```bash
# Create project directory
mkdir -p ~/aurora-x && cd ~/aurora-x

# Create environment file
cat > .env << EOF
# REQUIRED: Paste your tunnel token here
CF_TUNNEL_TOKEN=YOUR_TUNNEL_TOKEN_HERE

# GitHub repository (if using published image)
GITHUB_REPOSITORY=yourusername/aurora-x

# Optional settings
AURORA_HEALTH_TOKEN=secure123
DISCORD_WEBHOOK_URL=
AURORA_DEFAULT_LANG=python
EOF

# Download docker-compose.yml
curl -o docker-compose.yml https://raw.githubusercontent.com/yourusername/aurora-x/main/docker-compose.yml
```

#### 4. Deploy

```bash
# Start services
docker compose up -d

# Check status
docker compose ps
```

#### 5. Configure Cloudflare Hostname

Back in Cloudflare Dashboard:
1. Go to your tunnel > **Public Hostname** tab
2. Click **Add a public hostname**
3. Configure:
   - **Subdomain**: `aurora` (or leave blank for root)
   - **Domain**: Select your domain
   - **Service**: `http://aurora:8000`
4. Click **Save hostname**

## ✅ Verify Deployment

```bash
# Local health check
curl http://localhost:8000/healthz

# Public access (wait 30 seconds for DNS)
curl https://aurora.yourdomain.com/healthz
```

### Access Points

- **Health**: `https://aurora.yourdomain.com/healthz`
- **Dashboard**: `https://aurora.yourdomain.com/dashboard/demos`
- **Chat API**: `https://aurora.yourdomain.com/chat`
- **Main App**: `https://aurora.yourdomain.com`

## 📱 Mobile PWA Setup

1. Open `https://aurora.yourdomain.com` on mobile
2. **iOS**: Safari → Share → Add to Home Screen
3. **Android**: Chrome → Menu → Install App

## 🔧 Management

### View Logs

```bash
# All logs
docker compose logs -f

# Aurora only
docker compose logs -f aurora

# Tunnel only
docker compose logs -f cloudflared
```

### Update Aurora

```bash
# Pull latest image
docker compose pull aurora

# Restart with new version
docker compose up -d aurora
```

### Stop/Restart

```bash
# Stop all
docker compose down

# Restart all
docker compose restart

# Stop but preserve data
docker compose stop
```

## 🔄 Rollback Procedures

### Quick Rollback

```bash
# Tag current as backup
docker tag ghcr.io/yourusername/aurora-x:latest backup

# Use specific version
docker compose down
sed -i 's/:latest/:v1.2.3/g' docker-compose.yml
docker compose up -d
```

### Emergency Recovery

```bash
# Full reset
docker compose down
docker system prune -af
docker volume prune -f

# Fresh deploy
docker compose pull
docker compose up -d
```

## 🔍 Troubleshooting

### Aurora Not Starting

```bash
# Check logs
docker logs aurora_x

# Test health endpoint
docker exec aurora_x curl http://localhost:8000/healthz

# Check resources
docker stats
```

### Tunnel Not Connecting

```bash
# Check tunnel logs
docker logs aurora_cf_tunnel

# Verify token in .env
cat .env | grep CF_TUNNEL_TOKEN

# Test connection
docker exec aurora_cf_tunnel cloudflared tunnel info
```

### DNS Issues

```bash
# Check DNS propagation
dig aurora.yourdomain.com

# Should show CNAME to:
# <tunnel-id>.cfargotunnel.com
```

## 🔐 Security Best Practices

1. **Token Security**: Keep `.env` file secure (chmod 600)
2. **Updates**: Enable automatic security updates
3. **Monitoring**: Set up health check alerts
4. **Backups**: Regular backup of `aurora_runs/` directory
5. **Access Control**: Consider Cloudflare Access for authentication

## 🚀 Advanced Configuration

### Build from Source

If building from repository instead of using image:

```yaml
# In docker-compose.yml, replace image with:
build:
  context: .
  dockerfile: Dockerfile.app
```

### Custom Domain Examples

- **Subdomain**: `aurora.yourdomain.com`
- **Root domain**: `yourdomain.com` 
- **Custom port**: Add `originRequest` in Cloudflare

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `CF_TUNNEL_TOKEN` | **Required** - Cloudflare tunnel token | - |
| `GITHUB_REPOSITORY` | GitHub repo for image pulls | - |
| `AURORA_HEALTH_TOKEN` | Health check authentication | secure123 |
| `DISCORD_WEBHOOK_URL` | Discord alerts webhook | - |
| `AURORA_DEFAULT_LANG` | Default synthesis language | python |

## 🎉 Success Checklist

- [ ] Docker installed on server
- [ ] Cloudflare Tunnel created
- [ ] Token added to `.env`
- [ ] Docker Compose running
- [ ] Public hostname configured
- [ ] HTTPS working at your domain
- [ ] Mobile PWA installable

---

**Questions?** Aurora-X auto-restarts on crashes and stays live 24/7 at your domain with zero exposed ports!