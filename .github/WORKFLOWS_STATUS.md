
# GitHub Workflows Status

## ✅ Active & Working

### CI/CD Workflows
- **aurora-ci.yml** - Main CI pipeline with quality gates, tests, and coverage badge
- **ci-quick.yml** - Fast PR checks (lint, security scan)
- **ci.yml** - Standard CI with quality gates

### Build & Release
- **aurora-release.yml** - Multi-arch Docker builds to GHCR (manual trigger or tags)
- **docker-multiarch.yml** - Full multi-arch builds (manual trigger)

### E2E Testing
- **aurora-e2e.yml** - Basic E2E tests (manual trigger)

## ⚠️ Disabled (Require Configuration)

### Deployment Workflows
- **deploy-ghcr.yml** - Requires SSH secrets: `SSH_HOST`, `SSH_USER`, `SSH_KEY`
- **deploy-ssh.yml** - Requires SSH secrets: `SSH_HOST`, `SSH_USER`, `SSH_KEY`
- **rollback.yml** - Requires SSH secrets for rollback operations

To enable: Add secrets in GitHub Settings → Secrets and Variables → Actions

### Advanced E2E
- **aurora-e2e-cached.yml** - Requires full infrastructure setup
- **aurora-e2e-extended.yml** - Requires full infrastructure setup

### Maintenance
- **ci-autofix.yml** - Auto-commit disabled (requires write permissions)
- **deep-scan.yml** - Redundant with aurora-ci.yml

## 🔧 Configuration Notes

### Aurora CI (Main Pipeline)
- Runs on: PRs and pushes to `main`
- Coverage threshold: 15% minimum
- Auto-publishes coverage badge to `badges` branch
- Quality gates: lint, security scan, tests

### Docker Builds
- Multi-arch support: `linux/amd64`, `linux/arm64`
- Published to: `ghcr.io/${{ github.repository }}`
- Tags: `latest`, `sha-<commit>`, `v*` (for releases)

### Secrets Required for Full Deployment
```bash
# VPS Deployment
SSH_HOST=your.vps.ip
SSH_USER=ubuntu
SSH_KEY=<your-private-key>
SSH_PORT=22  # optional

# Optional Services
CF_TUNNEL_TOKEN=<cloudflare-tunnel-token>
AURORA_HEALTH_TOKEN=<health-check-token>
DISCORD_WEBHOOK_URL=<discord-webhook>
```

## 📊 Workflow Triggers

| Workflow | PR | Push | Manual | Schedule |
|----------|----|----- |--------|----------|
| aurora-ci | ✅ | ✅ | - | - |
| ci-quick | ✅ | ✅ | - | - |
| aurora-release | - | ✅ (main/tags) | ✅ | - |
| aurora-e2e | ✅ | - | ✅ | - |
| deploy-* | - | - | ✅ | - |

## 🚀 Quick Actions

**Run E2E Tests:**
```bash
gh workflow run aurora-e2e.yml
```

**Trigger Release Build:**
```bash
git tag v1.0.0
git push origin v1.0.0
```

**Manual Deployment:**
```bash
gh workflow run deploy-ghcr.yml
```

---

Last updated: 2025-01-22
