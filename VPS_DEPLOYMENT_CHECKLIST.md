# ✅ Aurora-X VPS Deployment Checklist

## 📁 **1. Folder Structure Check**
```
~/aurora-x/
├── docker-compose.aurora-x.yml ✓ (791 bytes)
├── setup-aurora-x.sh           ✓ (1293 bytes, executable)
├── .env                         ⚠️ (create from template)
└── app/                         🔄 (will be cloned automatically)
```

## 🔐 **2. Environment Configuration (.env)**
Create from template and add your token:
```bash
# Copy template to .env
cp .env.template .env

# Edit and add your Cloudflare token
nano .env
```

Required values:
- `CF_TUNNEL_TOKEN=` **[PASTE YOUR TOKEN HERE]**
- `AURORA_HEALTH_TOKEN=ok` ✓
- `AURORA_DISCORD_WEBHOOK=` (optional)

## 🐳 **3. Docker Check**
```bash
# Check if installed
docker -v
docker compose version

# If missing, no worries - setup script auto-installs!
```

## ☁️ **4. Cloudflare Tunnel Setup**

### Create Tunnel:
1. Go to [Cloudflare Zero Trust](https://one.dash.cloudflare.com/)
2. Navigate to **Zero Trust → Networks → Tunnels**
3. Click **Create a tunnel**
4. Choose **Cloudflared**
5. Name: `aurora-x`
6. Click **Save tunnel**
7. Copy the token (starts with `ey...`)

### Configure Public Hostname:
1. In your tunnel → **Public Hostnames** tab
2. Click **Add a public hostname**
3. Configure:
   - **Subdomain**: `aurora` (or blank for root)
   - **Domain**: `yourdomain.com`
   - **Service**: `http://aurora:8000`
4. Click **Save hostname**

## 🚀 **5. Ready to Deploy!**
Once all items above are checked:
```bash
cd ~/aurora-x
./setup-aurora-x.sh
```

## 📊 **What Will Happen:**
1. **Clone repo**: `github.com/chango112595-cell/Aurora-x`
2. **Build Docker image** from your Dockerfile
3. **Start Aurora** container with health checks
4. **Start Cloudflared** tunnel 
5. **Auto-connect** to your domain via HTTPS

## 🔍 **Post-Deployment Verification:**
```bash
# Local health check
curl http://localhost:8000/health?token=ok

# Public HTTPS check (wait 30s for DNS)
curl https://aurora.yourdomain.com/health?token=ok

# View live logs
docker compose -f docker-compose.aurora-x.yml logs -f
```

## 📱 **Mobile PWA Test:**
1. Visit `https://aurora.yourdomain.com` on phone
2. iOS: Safari → Share → Add to Home Screen
3. Android: Chrome → Menu → Install App

---

**Status**: All deployment files ready! Just need your Cloudflare token in `.env`