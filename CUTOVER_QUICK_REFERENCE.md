# Aurora-X Cutover Quick Reference

## 🚀 Execute Now (Copy-Paste)

### 1. Cut Release
```bash
git checkout main && git pull
git tag -a v0.1.0 -m "Aurora X 0.1.0"
git push origin v0.1.0
```

### 2. Deploy (Docker Compose)
```bash
export AURORA_TOKEN_SECRET=$(python -c 'import secrets; print(secrets.token_hex(32))')
docker compose pull && docker compose up -d
```

### 3. Smoke Test
```bash
curl -fsS http://127.0.0.1:8000/healthz
# Expected: {"status":"ok","ok":true,...}
```

### 4. CI Sanity
```bash
gh workflow run "aurora-e2e.yml" --ref main
gh run watch <run-id> --exit-status
```

## 📋 Go/No-Go Checklist

- [ ] Tag `v0.1.0` pushed
- [ ] Image at `ghcr.io/chango112595-cell/Aurora-x:v0.1.0`
- [ ] `/healthz` returns 200
- [ ] E2E on `main` green
- [ ] Artifact `aurora-e2e-logs` present

## 🔄 Rollback (2 min)

**Compose:**
```bash
docker compose pull ghcr.io/chango112595-cell/Aurora-x:<prev-tag>
docker compose up -d
```

**K8s:**
```bash
kubectl rollout undo deploy/aurora-x
```

## 📊 Day-2 Checks

**Logs:**
```bash
docker compose logs api | grep -E '"rid"|"path"|"status"|"duration_ms"'
```

**Security:**
- `security-scan.yml` runs on every push to `main`
- Check workflow artifacts for pip-audit reports

**New Releases:**
```bash
git tag -a v0.1.1 -m "Aurora X 0.1.1"
git push origin v0.1.1
```

## 📚 Documentation

- **OPERATIONS.md** - Deployment, monitoring, rollback
- **CONTRIBUTING.md** - Developer guide, CI triage
- **SPEC1_VERIFICATION.md** - E2E workflow verification
- **GO_LIVE_EXECUTION.md** - Full execution plan

## 🎯 SLOs

- **Availability**: ≥ 99.5% (healthz)
- **Latency**: p95 < 500ms
- **Artifacts**: Always present

---

**Status**: ✅ Ready to launch
