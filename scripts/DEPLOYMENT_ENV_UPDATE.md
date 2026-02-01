# Deployment Environment Variables Update Guide

**Purpose:** Update environment variables in deployment configurations after secret rotation.

## Deployment Locations Found

Based on codebase analysis, you may have deployments in:

1. **Docker Compose** (`docker-compose.yml`, `docker-compose.cloudflare.yml`, etc.)
2. **Kubernetes** (`k8s/` directory)
3. **GitHub Actions Deployments** (`.github/workflows/deploy-*.yml`)
4. **Direct Server Deployments** (SSH-based)

## Update Instructions

### 1. Docker Compose Files

**Files to check:**
- `docker-compose.yml`
- `docker-compose.cloudflare.yml`
- `docker-compose.aurora-x.yml`
- `docker/docker-compose.yml`

**Action:** Update environment variables in `environment:` sections:

```yaml
environment:
  JWT_SECRET: ${JWT_SECRET}
  ADMIN_PASSWORD: ${ADMIN_PASSWORD}
  AURORA_ADMIN_KEY: ${AURORA_ADMIN_KEY}
  AURORA_MASTER_PASSPHRASE: ${AURORA_MASTER_PASSPHRASE}
```

**Or use `.env` file:**
- Create/update `.env` file in deployment directory
- Set all 4 secrets (same values as `.env.local`)
- Ensure `.env` is in `.gitignore`

---

### 2. Kubernetes Deployments

**Files to check:**
- `k8s/aurora-deployment.yaml`
- `k8s/kustomize/base/deployment.yaml`
- Any other K8s manifests

**Action:** Update secrets in Kubernetes:

```bash
# Create/update secrets
kubectl create secret generic aurora-secrets \
  --from-literal=JWT_SECRET='c6f44238bd0e1471ea5fd1785818f5f268ed956f14a6d455c3ec502bcab3a339' \
  --from-literal=AURORA_ADMIN_KEY='d481c5de54138586e3bf325bd6cbf39b24bcac1abed05824834f30cc7eced16a' \
  --from-literal=ADMIN_PASSWORD='<your-password>' \
  --from-literal=AURORA_MASTER_PASSPHRASE='<your-passphrase>' \
  --dry-run=client -o yaml | kubectl apply -f -
```

**Or update existing secret:**
```bash
kubectl edit secret aurora-secrets
```

---

### 3. GitHub Actions Deployment Workflows

**Files to check:**
- `.github/workflows/deploy-ssh.yml`
- `.github/workflows/deploy-ghcr.yml`

**Action:** These workflows use GitHub Secrets (already covered in Step 2 of rotation). Verify they reference:
- `JWT_SECRET`
- `AURORA_ADMIN_KEY`
- `ADMIN_PASSWORD`
- `AURORA_MASTER_PASSPHRASE`

---

### 4. Direct Server Deployments

**If you deploy directly to a server:**

1. SSH into server
2. Navigate to deployment directory
3. Update `.env` file or environment variables
4. Restart services:

```bash
# Docker Compose
docker compose down
docker compose up -d

# Systemd service
sudo systemctl restart aurora-x

# PM2
pm2 restart aurora-x
```

---

## Verification Checklist

After updating deployment env vars:

- [ ] Docker containers restarted (if using Docker)
- [ ] Kubernetes pods restarted (if using K8s)
- [ ] Server services restarted (if direct deployment)
- [ ] Health checks passing
- [ ] Authentication working (test admin login)
- [ ] `/api/control` endpoint working (test with admin key)
- [ ] Vault operations working (test vault endpoints)

---

## Security Notes

- **Never commit secrets** - Use environment variables or secret management
- **Use same values** - All deployments should use the same rotated secrets
- **Rotate regularly** - Consider periodic secret rotation as best practice
- **Monitor logs** - Watch for authentication failures indicating old secrets still in use

---

## If You Don't Have Deployments Yet

If you're not currently deployed anywhere, you can skip this step. Just ensure:
- Local `.env.local` is updated ✅
- GitHub Actions secrets are updated ✅
- You're ready to set deployment env vars when you do deploy
