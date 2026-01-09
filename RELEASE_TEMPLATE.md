# Aurora-X Release Template

## For v0.1.1 and Future Releases

### Quick Release Commands

```bash
# 1. Update version (if needed in pyproject.toml or similar)
# 2. Create release tag
git tag -a v0.1.1 -m "Aurora X 0.1.1 - $(date +%Y-%m-%d)"
git push origin v0.1.1

# 3. Verify workflow triggered
gh run list --workflow "docker-release.yml" --limit 1

# 4. Check GitHub Release created
gh release view v0.1.1
```

### Changelog Template

```markdown
# Aurora X v0.1.1

**Release Date:** YYYY-MM-DD

## 🎉 What's New
- Feature description
- Another feature

## 🐛 Bug Fixes
- Fixed issue description
- Another fix

## 🔧 Improvements
- Performance improvement
- Code quality enhancement

## 📚 Documentation
- Updated docs
- New guides

## 🔒 Security
- Security fix (if applicable)

## 📦 Docker Image
- Image: `ghcr.io/chango112595-cell/Aurora-x:v0.1.1`
- Pull: `docker pull ghcr.io/chango112595-cell/Aurora-x:v0.1.1`

## 🚀 Deployment
```bash
export AURORA_TOKEN_SECRET=$(python -c 'import secrets; print(secrets.token_hex(32))')
docker compose pull
docker compose up -d
```

## 📊 Verification
```bash
curl -fsS http://127.0.0.1:8000/healthz
gh workflow run "aurora-e2e.yml" --ref main
```
```

### Automated Changelog Generation

For future releases, you can use GitHub's auto-generated release notes or create a script:

```bash
# Get commits since last tag
git log $(git describe --tags --abbrev=0)..HEAD --pretty=format:"- %s (%h)" > CHANGELOG_v0.1.1.md
```

### Semantic Versioning Guide

- **PATCH** (v0.1.1): Bug fixes, minor improvements
- **MINOR** (v0.2.0): New features, backward compatible
- **MAJOR** (v1.0.0): Breaking changes

### Release Checklist

- [ ] All tests passing on `main`
- [ ] Security scan clean
- [ ] Documentation updated
- [ ] Changelog prepared
- [ ] Tag created with semver
- [ ] Docker image built and pushed
- [ ] GitHub Release created
- [ ] `/healthz` verified in production
- [ ] E2E workflow passes
- [ ] Rollback plan documented (if needed)

### Post-Release

1. **Monitor** logs for first 15 minutes
2. **Verify** structured logs (`rid`, `path`, `status`, `duration_ms`)
3. **Check** rate limiting working correctly
4. **Confirm** CORS configured (if applicable)
5. **Validate** security scan results

---

**Next Release:** Use this template for v0.1.1, v0.2.0, etc.
