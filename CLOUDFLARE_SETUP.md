# 🔒 Aurora-X Cloudflare Tunnel Setup

## Zero-Port Exposure + Custom Domain for Mobile Access

Deploy Aurora-X with **zero exposed ports** using Cloudflare Tunnel. Perfect for secure mobile access at `aurora.yourname.dev`.

## 📱 Quick Setup (5 minutes)

### 1. Get Cloudflare Tunnel Token

```bash
# Install cloudflared
brew install cloudflare/cloudflare/cloudflared  # macOS
# OR
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o cloudflared

# Login to Cloudflare
cloudflared tunnel login

# Create tunnel
cloudflared tunnel create aurora-x

# Get tunnel token (save this!)
cloudflared tunnel token aurora-x
```

### 2. Configure DNS

In Cloudflare Dashboard:
1. Go to your domain's DNS settings
2. Add CNAME: `aurora` → `<tunnel-id>.cfargotunnel.com`
3. Add CNAME: `api.aurora` → `<tunnel-id>.cfargotunnel.com`
4. Add CNAME: `health.aurora` → `<tunnel-id>.cfargotunnel.com`

### 3. Deploy with Docker Compose

```bash
# Set environment variables
export GITHUB_REPOSITORY="yourusername/aurora-x"
export CLOUDFLARE_TUNNEL_TOKEN="your-tunnel-token-here"

# Pull latest multi-arch image
docker pull ghcr.io/${GITHUB_REPOSITORY}:latest

# Start Aurora + Cloudflare Tunnel
docker-compose -f docker-compose.cloudflare.yml up -d

# Check health
curl https://aurora.yourname.dev/healthz
```

## 🎯 Access Points

Once deployed, access Aurora from anywhere:

| Endpoint | URL | Purpose |
|----------|-----|---------|
| **Main App** | `https://aurora.yourname.dev` | Full Aurora interface |
| **Dashboard** | `https://aurora.yourname.dev/dashboard/demos` | Demo dashboard (PWA) |
| **API** | `https://api.aurora.yourname.dev` | API endpoints |
| **Health** | `https://health.aurora.yourname.dev` | Monitoring endpoint |

## 📱 Mobile Setup

### iOS (iPhone/iPad)
1. Open Safari
2. Navigate to `https://aurora.yourname.dev`
3. Tap Share → "Add to Home Screen"
4. Aurora runs as native app!

### Android
1. Open Chrome
2. Navigate to `https://aurora.yourname.dev`
3. Menu → "Install app"
4. Aurora appears in app drawer!

## 🚀 Advanced Features

### Auto-Deploy on Push

The `aurora-release.yml` workflow automatically:
1. Builds multi-arch images (amd64/arm64)
2. Pushes to GitHub Container Registry
3. Tags with `:latest` and `:sha-xxxxx`

### Update Running Container

```bash
# Pull latest
docker-compose -f docker-compose.cloudflare.yml pull

# Recreate with new image
docker-compose -f docker-compose.cloudflare.yml up -d --force-recreate
```

### Custom Subdomain

Edit `cloudflare-tunnel.yml`:
```yaml
- hostname: ai.company.com  # Your custom domain
  service: http://localhost:8000
```

### Enable WebSockets

Already configured in `cloudflare-tunnel.yml` for real-time features:
```yaml
- hostname: aurora.yourname.dev
  path: /ws
  service: http://localhost:8000
```

## 🔐 Security Benefits

✅ **Zero exposed ports** - No direct server access  
✅ **DDoS protection** - Cloudflare's network  
✅ **Auto HTTPS** - Valid SSL certificates  
✅ **WAF ready** - Web Application Firewall  
✅ **Access control** - Cloudflare Access integration  

## 📊 Monitoring

Check tunnel status:
```bash
docker logs aurora-tunnel

# View metrics
curl https://health.aurora.yourname.dev | jq .
```

## 🌍 Global Performance

Cloudflare Tunnel provides:
- **Anycast routing** - Connects to nearest datacenter
- **Argo Smart Routing** - Optimized path selection
- **HTTP/3 support** - Faster mobile connections
- **Automatic failover** - High availability

## 🎉 You're Live!

Aurora-X is now accessible globally at your custom domain with:
- Enterprise-grade security
- Mobile-optimized PWA
- Zero maintenance tunnels
- Automatic HTTPS renewal

Perfect for phones, tablets, and any device with a browser!