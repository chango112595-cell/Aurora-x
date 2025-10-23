
# Aurora-X GitHub Workflows Status

## ✅ ACTIVE (Run on every PR/push)

1. **aurora-ci.yml** - Main CI Pipeline
   - Runs: Lint (ruff), Security (bandit), Tests (pytest), Coverage (≥15%)
   - Publishes coverage badge to `badges` branch
   - Uploads SARIF security scan results

2. **ci.yml** - Quality Gates
   - Runs: `make gates` (calls `aurora_x/checks/ci_gate.py`)
   - Validates config, seeds, drift limits

3. **aurora-release.yml** - Docker Build & Publish
   - Runs: On push to `main`
   - Builds multi-arch image (amd64, arm64)
   - Pushes to `ghcr.io`

## 🔧 MANUAL ONLY (workflow_dispatch)

4. **deploy-ghcr.yml** - Deploy to VPS (requires secrets)
5. **rollback.yml** - Emergency rollback (requires secrets)

## ❌ DISABLED (Not running)

- `aurora-e2e.yml` - Needs full infra
- `aurora-e2e-cached.yml` - Needs full infra
- `aurora-e2e-extended.yml` - Needs full infra
- `deploy-ssh.yml` - Duplicate of deploy-ghcr
- `docker-multiarch.yml` - Duplicate of release
- `deep-scan.yml` - Redundant with aurora-ci
- `ci-autofix.yml` - Requires write permissions
- `manual.yml` - Just a hello-world example

## Self-Healing Architecture

Aurora can recover from failures via:

1. **Isolated runs** - Each synthesis in `runs/run-*/` 
2. **Fallback templates** - `aurora_x/synthesis/fallback.py`
3. **Health monitoring** - `/healthz` endpoint
4. **Persistent corpus** - `data/corpus.db` survives crashes
5. **CI gates** - Block bad deploys
6. **Automatic snapshots** - `backups/aurora_backup_*/`

---

**To check workflow status:**
```bash
gh run list --limit 20
```

**To manually trigger deploy:**
```bash
gh workflow run deploy-ghcr.yml
```
