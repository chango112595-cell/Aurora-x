# Final Green-Light Checklist

## Pre-Launch

- [ ] Push **`v0.1.0`** tag (or run release script)
  ```bash
  git tag -a v0.1.0 -m "Aurora X 0.1.0"
  git push origin v0.1.0
  # OR
  .\scripts\release.ps1 -Version v0.1.0 -Message "Aurora X 0.1.0"
  ```

- [ ] Confirm GHCR images: `:v0.1.0` and `:latest`
  ```bash
  gh api repos/chango112595-cell/Aurora-x/packages | jq '.[] | select(.name == "Aurora-x")'
  # OR check: https://github.com/chango112595-cell/Aurora-x/pkgs/container/aurora-x
  ```

- [ ] Deploy via Compose (as in **FINAL_CUTOVER_BLOCK.md**)
  ```bash
  export AURORA_TOKEN_SECRET=$(python -c 'import secrets; print(secrets.token_hex(32))')
  docker compose pull && docker compose up -d
  ```

- [ ] Smoke: `/healthz` → 200
  ```bash
  curl -fsS http://127.0.0.1:8000/healthz
  # Expected: {"status":"ok","ok":true,...}
  ```

- [ ] Run main **E2E** and verify `aurora-e2e-logs` artifact
  ```bash
  gh workflow run "aurora-e2e.yml" --ref main
  gh run watch <run-id> --exit-status
  gh run download <run-id> -n aurora-e2e-logs -D e2e-logs
  ls -la e2e-logs/
  ```

- [ ] Annotate **CHANGELOG.md** if anything changed during cutover
  - Update `[Unreleased]` section if needed
  - Document any last-minute fixes

## Post-Launch Watch (First 30-60 min)

### Logs Monitoring

```bash
# Tail logs for structured output
docker compose logs -f api | grep -E '"rid"|"status"|"duration_ms"'

# Watch for errors
docker compose logs api | grep -i error

# Check request patterns
docker compose logs api | grep -E '"path":|"method":'
```

### Metrics to Watch

- [ ] **Error rate**: < 2% (check logs for 4xx/5xx responses)
- [ ] **p95 latency**: < 500ms (check `duration_ms` in logs)
- [ ] **Health check**: All `/healthz` calls return 200
- [ ] **Rate limiting**: Verify 429 responses when limit exceeded (test if needed)

### Security Scan

- [ ] Verify `pip-audit` job completed on `main`
  ```bash
  gh run list --workflow "security-scan.yml" --limit 1
  gh run view <run-id> --log
  ```

### Structured Log Verification

Look for entries like:
```json
{
  "rid": "uuid-here",
  "path": "/healthz",
  "method": "GET",
  "status": 200,
  "duration_ms": 12
}
```

## Future Releases (v0.1.1+)

**Windows:**
```powershell
.\scripts\release.ps1 -Version v0.1.1 -Message "Bug fixes and improvements"
```

**Linux/Mac:**
```bash
./scripts/release.sh v0.1.1 "Bug fixes and improvements"
```

**Manual:**
```bash
git tag -a v0.1.1 -m "Aurora X 0.1.1"
git push origin v0.1.1
```

## Optional Polish (Future Enhancements)

- [ ] **SBOM + Signing**: Add `syft` + `cosign` to release job
- [ ] **PR Gates**: Require green E2E + security scan before merging to `main`
- [ ] **Metrics Endpoint**: Expose `/metrics` (Prometheus) for observability

---

**Status**: ✅ Ready for launch
