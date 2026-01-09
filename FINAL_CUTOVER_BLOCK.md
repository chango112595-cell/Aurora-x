# Final Cutover Block - Copy-Paste Ready

## 0) Preflight (Once)

```bash
# Ensure you're on the right repo/branch and clean
git remote -v
git checkout main
git pull
```

## 1) Cut the Release (Triggers Image Build + GitHub Release)

```bash
git tag -a v0.1.0 -m "Aurora X 0.1.0"
git push origin v0.1.0
```

**What happens automatically:**
- `docker-release.yml` workflow triggers
- Docker image builds and pushes to `ghcr.io/chango112595-cell/Aurora-x:v0.1.0` and `:latest`
- GitHub Release created with auto-generated notes

## 2) Deploy

### Option A — Docker Compose (Single VM)

```bash
export AURORA_TOKEN_SECRET=$(python - <<'PY'
import secrets; print(secrets.token_hex(32))
PY
)
docker compose pull
docker compose up -d
```

### Option B — Kubernetes

```bash
kubectl apply -f k8s/
kubectl set image deploy/aurora-x api=ghcr.io/chango112595-cell/Aurora-x:v0.1.0
kubectl rollout status deploy/aurora-x
```

## 3) Smoke + Sanity

```bash
# Health check
curl -fsS http://127.0.0.1:8000/healthz
# Expected: {"status":"ok","ok":true,...}

# E2E on main
gh workflow run "aurora-e2e.yml" --ref main
# Copy the run id printed, then:
gh run watch <run-id> --exit-status
gh run download <run-id> -n aurora-e2e-logs -D e2e-logs
tail -n 200 e2e-logs/aurora.log
```

## 4) Rollback (Simple + Fast)

**Compose:**
```bash
docker compose pull ghcr.io/chango112595-cell/Aurora-x:<prev-tag>
docker compose up -d
```

**K8s:**
```bash
kubectl rollout undo deploy/aurora-x
```

## Go/No-Go Checklist

- [ ] v0.1.0 tag pushed
- [ ] Image at `ghcr.io/chango112595-cell/Aurora-x:v0.1.0`
- [ ] `/healthz` returns 200 in prod
- [ ] E2E on `main` green & `aurora-e2e-logs` present

---

## For Future Releases (v0.1.1+)

### Quick Release

**PowerShell:**
```powershell
.\scripts\release.ps1 -Version v0.1.1 -Message "Bug fixes and improvements"
```

**Bash:**
```bash
./scripts/release.sh v0.1.1 "Bug fixes and improvements"
```

**Manual:**
```bash
git tag -a v0.1.1 -m "Aurora X 0.1.1"
git push origin v0.1.1
```

### Update Changelog

1. Edit `CHANGELOG.md`
2. Move items from `[Unreleased]` to new version section
3. Commit: `git commit -m "chore: Update CHANGELOG for v0.1.1"`

---

**Status**: ✅ Ready to execute
