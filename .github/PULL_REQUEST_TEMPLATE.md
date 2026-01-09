# Aurora-X Pull Request

## Description
<!-- Describe your changes here -->

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Security fix

## Checklist

### Pre-Merge
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex code
- [ ] Documentation updated (if needed)
- [ ] No new warnings generated
- [ ] Tests added/updated and passing locally

### CI/CD
- [ ] All CI checks passing
- [ ] E2E workflow (`aurora-e2e.yml`) passes
- [ ] Security scan (`security-scan.yml`) passes
- [ ] Artifact `aurora-e2e-logs` present and non-empty

### Post-Merge (Release)
- [ ] Tag created following semver (e.g., `v0.1.1`)
- [ ] Docker image built and pushed to GHCR
- [ ] GitHub Release created automatically
- [ ] `/healthz` endpoint verified in production
- [ ] Logs show structured output (`rid`, `path`, `status`, `duration_ms`)

## Related Documentation
- [OPERATIONS.md](../OPERATIONS.md) - Deployment and operations guide
- [CONTRIBUTING.md](../CONTRIBUTING.md) - Developer guide and CI triage
- [SPEC1_VERIFICATION.md](../SPEC1_VERIFICATION.md) - E2E workflow verification
- [GO_LIVE_EXECUTION.md](../GO_LIVE_EXECUTION.md) - Go-live execution plan

## Testing
<!-- Describe how you tested your changes -->

## Deployment Notes
<!-- Any special deployment considerations? -->

## Rollback Plan
<!-- If this PR requires rollback, describe the plan -->

---

**Note**: After merge to `main`, create a release tag to trigger Docker build and GitHub Release:
```bash
git tag -a v0.1.1 -m "Aurora X 0.1.1"
git push origin v0.1.1
```
