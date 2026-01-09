# Aurora-X Go-Live Execution Plan

## ✅ Confirmations

1. **Tag v0.1.0** - ✅ CONFIRMED
   - First production release will be `v0.1.0`
   - Semantic versioning: Major.Minor.Patch

2. **Deployment Target: Docker Compose** - ✅ CONFIRMED
   - Single VM deployment using `compose.yaml`
   - One-command deployment ready

## Go-Live Execution (Copy-Paste Ready)

### Step 1: Cut Release & Push Image

```bash
# Ensure you're on the latest main
git checkout main
git pull origin main

# Merge vs-code-aurora-version if not already merged
git merge vs-code-aurora-version
git push origin main

# Create and push release tag
git tag -a v0.1.0 -m "Aurora X 0.1.0 - Production Release"
git push origin v0.1.0
```

**Expected Result:**
- `docker-release.yml` workflow triggers automatically
- Image builds and pushes to `ghcr.io/chango112595-cell/Aurora-x:v0.1.0`
- Image also tagged as `:latest`
- GitHub Release created automatically

### Step 2: Deploy (Docker Compose)

```bash
# Set required secret
export AURORA_TOKEN_SECRET=$(python -c 'import secrets; print(secrets.token_hex(32))')

# Pull latest image and start
docker compose pull
docker compose up -d

# Verify container is running
docker compose ps
```

**Expected Result:**
- Container starts successfully
- Health check passes
- Service available on port 8000

### Step 3: Smoke Checks

```bash
# Health endpoint
curl -fsS http://127.0.0.1:8000/healthz

# Expected response:
# {"status":"ok","ok":true,"t08_enabled":false,"ts":1234567890.123}

# Check logs for structured output
docker compose logs api | grep -E '"rid"|"path"|"status"|"duration_ms"'
```

### Step 4: CI Sanity on Main

```bash
# Trigger E2E workflow
gh workflow run "aurora-e2e.yml" --ref main

# Wait for completion (get run ID from output)
gh run watch <run-id> --exit-status

# Download and verify logs
gh run download <run-id> -n aurora-e2e-logs -D e2e-logs
tail -n 200 e2e-logs/aurora.log
cat e2e-logs/aurora.target
```

**Expected Result:**
- All workflow steps pass
- Artifact `aurora-e2e-logs` contains both files
- API started successfully in CI

## Rollback Plan (2 Minutes)

### If Issues Occur:

```bash
# Stop current deployment
docker compose down

# Pull previous version (if available)
# Note: For v0.1.0, there's no previous version yet
# For future versions, use:
docker pull ghcr.io/chango112595-cell/Aurora-x:v0.0.9  # example

# Update compose.yaml to use previous tag, then:
docker compose pull
docker compose up -d
```

### Keep Last 3 Tags Hot:
- Maintain `v0.1.0`, `v0.0.9`, `v0.0.8` (or similar) for instant rollback
- Document rollback procedure in OPERATIONS.md

## Day-2 Operations

### Monitoring

**Logs Structure:**
```json
{
  "rid": "uuid-here",
  "path": "/api/endpoint",
  "method": "GET",
  "status": 200,
  "duration_ms": 45
}
```

**View Logs:**
```bash
docker compose logs -f api
```

### Alerts (Starter SLOs)

1. **Availability (healthz)**: ≥ 99.5%
   - Alert if: 3 consecutive failures OR 5xx rate >2% over 5 minutes
   - Check: `curl http://127.0.0.1:8000/healthz`

2. **Latency (p95)**: < 500ms
   - Alert if: p95 > 500ms over 10 minutes
   - Monitor: `duration_ms` in logs

3. **Artifact Presence**: Always present
   - Alert if: `aurora-e2e-logs` artifact missing (shouldn't happen with ensure step)

### Security

**Automated Scanning:**
- `security-scan.yml` runs on every push to `main`
- Weekly scheduled scans
- Reports available in workflow artifacts

**Manual Check:**
```bash
pip-audit -r requirements.txt
```

### Releases

**Future Releases:**
```bash
# Patch release
git tag -a v0.1.1 -m "Aurora X 0.1.1"
git push origin v0.1.1

# Minor release
git tag -a v0.2.0 -m "Aurora X 0.2.0"
git push origin v0.2.0

# Major release
git tag -a v1.0.0 -m "Aurora X 1.0.0"
git push origin v1.0.0
```

**Auto-Generated:**
- Docker image pushed to GHCR
- GitHub Release created with notes
- Multiple tags (latest, sha, semver)

## Handoff Checklist

- [x] `AURORA_TOKEN_SECRET` configured (set in deployment environment)
- [x] Image `ghcr.io/chango112595-cell/Aurora-x:v0.1.0` will be available after tag push
- [ ] `/healthz` returns 200 in production (verify after deployment)
- [ ] CI e2e on `main` green & artifact `aurora-e2e-logs` present (verify after workflow run)
- [x] READMEs/OPERATIONS visible in repo
  - `CONTRIBUTING.md` ✅
  - `OPERATIONS.md` ✅
  - `SPECS_IMPLEMENTATION_SUMMARY.md` ✅
  - `GO_LIVE_CHECKLIST.md` ✅

## Quick Reference

**Image Location:**
```
ghcr.io/chango112595-cell/Aurora-x:v0.1.0
ghcr.io/chango112595-cell/Aurora-x:latest
```

**Health Endpoint:**
```
http://127.0.0.1:8000/healthz
```

**Documentation:**
- `CONTRIBUTING.md` - Developer guide
- `OPERATIONS.md` - Deployment and operations
- `GO_LIVE_CHECKLIST.md` - Pre-deployment checklist

---

**Status**: ✅ Ready for immediate execution
**Version**: v0.1.0
**Target**: Docker Compose on single VM
