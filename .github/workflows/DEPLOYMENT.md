# Aurora-X Deployment Documentation

This document covers the complete deployment system for Aurora-X, including GitHub Actions workflows, server setup, and deployment strategies.

## 📋 Table of Contents
- [Deployment Options](#deployment-options)
- [Required GitHub Secrets](#required-github-secrets)
- [Server Setup](#server-setup)
- [Deployment Workflows](#deployment-workflows)
- [Rollback Procedures](#rollback-procedures)
- [Monitoring & Notifications](#monitoring--notifications)
- [Usage Examples](#usage-examples)
- [Troubleshooting](#troubleshooting)

## 🚀 Deployment Options

Aurora-X supports two primary deployment strategies:

### 1. SSH Deployment (deploy-ssh.yml)
- **Best for**: Small teams, simple setups, direct server control
- **How it works**: Copies files via SCP, builds Docker image on server
- **Pros**: Simple, no registry needed, full control
- **Cons**: Builds on production server, uses server resources

### 2. GitHub Container Registry (deploy-ghcr.yml)
- **Best for**: Multi-server deployments, larger teams, CI/CD pipelines
- **How it works**: Builds image in GitHub Actions, pushes to GHCR, server pulls image
- **Pros**: Consistent builds, multi-arch support, image versioning
- **Cons**: Requires GitHub packages access, more complex

## 🔐 Required GitHub Secrets

Configure these in your repository settings under **Settings → Secrets and variables → Actions**:

### Essential Secrets
```yaml
SSH_HOST              # Your server's IP or hostname (e.g., 192.168.1.100)
SSH_USER              # SSH username (e.g., ubuntu, root)
SSH_KEY               # Private SSH key for authentication
SSH_PORT              # SSH port (optional, defaults to 22)
CF_TUNNEL_TOKEN       # Cloudflare Tunnel token for public access
AURORA_HEALTH_TOKEN   # Health check authentication token
```

### Optional Variables (not secrets)
```yaml
DISCORD_WEBHOOK_URL   # Discord webhook for notifications
AURORA_URL            # Public URL of your Aurora instance
```

### Setting SSH Key
```bash
# Generate SSH key pair (if you don't have one)
ssh-keygen -t ed25519 -C "aurora-deploy"

# Copy public key to server
ssh-copy-id -i ~/.ssh/id_ed25519.pub user@server

# Add private key to GitHub Secrets
cat ~/.ssh/id_ed25519 | pbcopy  # macOS
cat ~/.ssh/id_ed25519 | xclip    # Linux
# Then paste into SSH_KEY secret
```

## 🖥️ Server Setup

### Prerequisites
- Ubuntu 20.04+ or similar Linux distribution
- Docker and Docker Compose installed
- SSH access configured
- Minimum 2GB RAM, 10GB disk space

### Initial Server Setup
```bash
# 1. Update system
sudo apt update && sudo apt upgrade -y

# 2. Install Docker
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker $USER

# 3. Install Docker Compose
sudo apt install docker-compose-plugin -y

# 4. Create deployment directory
mkdir -p ~/aurora-x-deployment
cd ~/aurora-x-deployment

# 5. Set up environment file
# Copy .env.example and configure:
nano .env
```

### Environment Configuration
Edit `.env` with your values:
```env
# Cloudflare Tunnel (for public access)
CF_TUNNEL_TOKEN=your-tunnel-token-here

# Aurora Configuration
AURORA_HEALTH_TOKEN=secure-health-token
AURORA_ENV=production
AURORA_DEFAULT_LANG=python

# Optional monitoring
AURORA_DISCORD_WEBHOOK=https://discord.com/api/webhooks/...

# GitHub repository (for GHCR)
GITHUB_REPOSITORY=yourusername/aurora-x
```

### Cloudflare Tunnel Setup
1. Go to [Cloudflare Zero Trust Dashboard](https://one.dash.cloudflare.com/)
2. Navigate to **Networks → Tunnels**
3. Create a new tunnel
4. Copy the token
5. Configure public hostname to point to `http://aurora:8000`

## 📦 Deployment Workflows

### SSH Deployment Workflow

**Trigger**: Push to main branch or manual dispatch

```yaml
# Manual trigger with custom message
workflow_dispatch:
  inputs:
    deploy_message: "Fixed critical bug #123"
```

**Process**:
1. Checks out code
2. Sends Discord notification (if configured)
3. Creates deployment directory on server
4. Backs up current configuration
5. Copies files via SCP
6. Builds and starts containers
7. Performs health checks
8. Reports deployment status

### GHCR Deployment Workflow

**Trigger**: Push to main branch or manual dispatch

**Two-stage process**:

**Stage 1 - Build & Push**:
1. Builds multi-architecture Docker image
2. Tags with version, SHA, and latest
3. Pushes to GitHub Container Registry

**Stage 2 - Deploy**:
1. SSH into server
2. Creates backup of current state
3. Pulls new image from GHCR
4. Restarts containers with new image
5. Validates health
6. Cleans up old images

## ↩️ Rollback Procedures

### Manual Rollback Workflow

**Trigger**: Manual only (requires reason)

```yaml
# Rollback options
rollback_method:
  - docker_image    # Use previous Docker image
  - compose_backup  # Restore compose file from backup
  - both           # Try both methods
```

### Rollback Process
1. **Docker Image Rollback**:
   - Tags current image as `failed-<timestamp>`
   - Restores previous image tagged as `rollback`
   - Restarts containers with rollback image

2. **Compose File Rollback**:
   - Finds latest backup in `~/aurora-x-deployment/backups/`
   - Restores previous docker-compose.yml
   - Restarts with restored configuration

3. **Health Validation**:
   - Performs health checks after rollback
   - Reports success/failure via Discord

## 📊 Monitoring & Notifications

### Discord Notifications
Workflows send notifications for:
- 🚀 Deployment starting
- ✅ Deployment successful
- ❌ Deployment failed
- ⏮️ Rollback initiated
- ✅ Rollback successful
- ❌ Rollback failed

### Health Checks
All deployments validate health via:
```bash
curl http://localhost:8000/healthz?token=${AURORA_HEALTH_TOKEN}
```

Health check configuration:
- **Timeout**: 120 seconds
- **Retries**: 30 attempts
- **Interval**: 4 seconds between attempts

## 💡 Usage Examples

### Deploy on Push to Main
```bash
# Automatic deployment
git add .
git commit -m "feat: Add new synthesis template"
git push origin main
# Workflow triggers automatically
```

### Manual SSH Deployment
```bash
# Via GitHub Actions UI:
1. Go to Actions tab
2. Select "Deploy via SSH"
3. Click "Run workflow"
4. Enter deployment message
5. Click "Run workflow" button
```

### Manual GHCR Deployment
```bash
# Same as SSH but builds in GitHub:
1. Go to Actions tab
2. Select "Deploy via GitHub Container Registry"
3. Click "Run workflow"
4. Enter deployment message
5. Click "Run workflow" button
```

### Emergency Rollback
```bash
# Via GitHub Actions UI:
1. Go to Actions tab
2. Select "Rollback Deployment"
3. Click "Run workflow"
4. Enter rollback reason (required)
5. Select rollback method:
   - docker_image (fastest)
   - compose_backup (configuration rollback)
   - both (comprehensive)
6. Click "Run workflow" button
```

### Auto-Updater Integration
The deployment system works with the auto-updater:
```bash
# On server, set up auto-updater cron
crontab -e

# Add auto-update check every 5 minutes
*/5 * * * * cd ~/aurora-x-deployment && ./update-aurora.sh >> aurora-update.log 2>&1
```

## 🔧 Troubleshooting

### Common Issues

#### SSH Connection Failed
```bash
# Test SSH connection
ssh -i ~/.ssh/your-key user@server -p 22

# Check SSH key permissions
chmod 600 ~/.ssh/your-key
```

#### Health Check Timeout
```bash
# Check container logs
docker compose logs -f aurora

# Verify health endpoint
curl http://localhost:8000/healthz?token=your-token

# Check container status
docker compose ps
```

#### GHCR Authentication Failed
```bash
# Manually test login
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin

# Pull image manually
docker pull ghcr.io/yourusername/aurora-x:latest
```

#### Rollback Image Not Found
```bash
# Check available images
docker images | grep aurora

# Manually tag current as rollback
docker tag ghcr.io/yourusername/aurora-x:latest \
          ghcr.io/yourusername/aurora-x:rollback
```

### Debug Commands

#### Check deployment status
```bash
# On server
cd ~/aurora-x-deployment
docker compose ps
docker compose logs --tail=50 aurora
```

#### Manual health check
```bash
# With token
curl -v "http://localhost:8000/healthz?token=your-token"

# Check all endpoints
curl http://localhost:8000/api/status
curl http://localhost:8000/api/solve/demo
```

#### View deployment history
```bash
# Check backup directory
ls -la ~/aurora-x-deployment/backups/

# View GitHub Actions history
# Go to: https://github.com/yourusername/aurora-x/actions
```

## 📚 Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [GitHub Container Registry Guide](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Cloudflare Tunnel Documentation](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/)

## 🔒 Security Best Practices

1. **Use strong tokens**: Generate secure random tokens for health checks
2. **Rotate SSH keys**: Periodically update SSH keys
3. **Limit SSH access**: Use firewall rules to restrict SSH access
4. **Use secrets**: Never commit sensitive data to repository
5. **Monitor logs**: Regularly review deployment and application logs
6. **Test rollbacks**: Periodically test rollback procedures
7. **Backup data**: Maintain regular backups of persistent data

## 📝 Workflow Comparison

| Feature | SSH Deployment | GHCR Deployment |
|---------|---------------|-----------------|
| Build Location | On server | GitHub Actions |
| Registry Required | No | Yes (GitHub) |
| Multi-arch Support | No | Yes |
| Build Caching | Limited | Full |
| Network Usage | Low (code only) | High (images) |
| Rollback Speed | Slower | Faster |
| Version History | Manual | Automatic |
| Server Resources | High (build) | Low (pull only) |

Choose based on your needs:
- **SSH**: Simple, direct, good for single server
- **GHCR**: Scalable, versioned, good for teams

---

For questions or issues, please open an issue on the [Aurora-X repository](https://github.com/yourusername/aurora-x/issues).