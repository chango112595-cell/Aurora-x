# CI/CD Documentation

## Overview

Aurora-X uses GitHub Actions for continuous integration and deployment. The CI/CD pipeline automates testing, security scanning, building, and deployment processes to ensure code quality and production readiness.

## Workflows

### Main CI/CD Workflow

**File:** `.github/workflows/aurora-main-ci.yml`

**Triggers:**
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop`
- Manual workflow dispatch

**Jobs:**

#### 1. Test & Build Job

**Steps:**
1. **Checkout code** - Clone the repository
2. **Setup Python 3.11** - Configure Python environment with pip cache
3. **Setup Node.js 20** - Configure Node.js environment with npm cache
4. **Install Python dependencies** - Install pytest, ruff, bandit, semgrep, and project dependencies
5. **Install Node dependencies** - Run `npm ci` or `npm install`
6. **Lint Python** - Run Ruff linter (non-blocking)
7. **Security scan** - Run Bandit for Python security issues (high severity only)
8. **Semgrep scan** - Run Semgrep security scan with SARIF output
9. **Upload SARIF** - Upload security findings to GitHub Security tab
10. **Run Python tests** - Execute pytest with coverage reporting
11. **Calculate coverage** - Generate coverage percentage and badge color
12. **Run Node tests** - Execute npm test suite
13. **Build frontend** - Run npm build
14. **Build Docker images** - Build backend and frontend Docker images
15. **Run quality gates** - Execute Aurora's quality gate checks
16. **Generate coverage badge** - Create SVG badge with coverage percentage
17. **Publish badge** - Commit badge to `badges` branch (main branch only)
18. **Upload to Codecov** - Upload coverage reports to Codecov

#### 2. Docker Multi-Arch Build Job

**Triggers:** Only on push to `main` branch after test job passes

**Steps:**
1. **Checkout** - Clone repository
2. **Setup QEMU** - Configure multi-architecture emulation
3. **Setup Docker Buildx** - Configure advanced Docker builder
4. **Build backend** - Build for linux/amd64 and linux/arm64
5. **Build frontend** - Build for linux/amd64 and linux/arm64

#### 3. Status Check Job

**Purpose:** Aggregate workflow status and provide summary

**Runs:** Always, even if previous jobs fail

## Badges

The CI/CD pipeline automatically generates and updates badges in the README:

### CI/CD Status Badge
```markdown
![CI/CD Status](https://github.com/chango112595-cell/Aurora-x/actions/workflows/aurora-main-ci.yml/badge.svg)
```

Shows the current status of the main CI/CD workflow:
- ✅ Green: All checks passing
- ❌ Red: Some checks failing
- 🟡 Yellow: Workflow running

### Coverage Badge
```markdown
![Coverage](https://raw.githubusercontent.com/chango112595-cell/Aurora-x/badges/badges/coverage.svg)
```

Shows test coverage percentage:
- 🔴 Red: < 15%
- 🟠 Orange: 15-49%
- 🟡 Yellow: 50-69%
- 🟢 Green: ≥ 70%

Updated automatically on every push to `main` branch.

## Required Checks

For pull requests to be merged, the following checks should pass (configure in GitHub settings):

### Recommended Required Status Checks:
- ✅ Test & Build job completion
- ✅ Python tests passing
- ✅ Code quality checks (Ruff)
- ✅ Security scans (non-blocking but visible)
- ✅ Docker builds successful

### Branch Protection Rules (Recommended):

1. **Navigate to:** Repository Settings → Branches → Branch protection rules
2. **Add rule for:** `main` branch
3. **Enable:**
   - Require a pull request before merging
   - Require approvals: 1
   - Dismiss stale pull request approvals when new commits are pushed
   - Require status checks to pass before merging
   - Require branches to be up to date before merging
   - Status checks that are required:
     - `Test & Build`
   - Require conversation resolution before merging
   - Do not allow bypassing the above settings

## Manual Workflow Triggering

### Using GitHub Web Interface:
1. Go to repository → Actions tab
2. Select "Aurora Main CI/CD" workflow
3. Click "Run workflow" button
4. Select branch and click "Run workflow"

### Using GitHub CLI:
```bash
# Trigger workflow on current branch
gh workflow run "Aurora Main CI/CD"

# Trigger on specific branch
gh workflow run "Aurora Main CI/CD" --ref develop

# View workflow runs
gh run list --workflow=aurora-main-ci.yml

# Watch latest run
gh run watch
```

## Viewing Results

### GitHub Actions UI:
1. Go to repository → Actions tab
2. Click on workflow run
3. View job details, logs, and artifacts

### Check Annotations:
- Security findings appear in the Security tab
- Test failures show inline annotations in PR
- Coverage reports available as artifacts

### Coverage Reports:
- Codecov: https://codecov.io/gh/chango112595-cell/Aurora-x
- Badge: Updated automatically in README
- XML report: Available as workflow artifact

## Troubleshooting

### Workflow Fails on Test Step

**Check:**
1. View pytest output in workflow logs
2. Run tests locally: `pytest -v`
3. Check for missing dependencies
4. Verify environment variables

**Fix:**
- Update dependencies in `requirements.txt`
- Fix failing tests
- Add missing environment variables to GitHub Secrets

### Docker Build Fails

**Check:**
1. View Docker build logs
2. Verify Dockerfile syntax
3. Check for missing files

**Fix:**
- Test Docker build locally: `docker build -f docker/Dockerfile.backend .`
- Update Dockerfile if needed
- Ensure all required files exist

### Coverage Badge Not Updating

**Check:**
1. Verify workflow completed successfully
2. Check if `badges` branch exists
3. Verify badge path in README

**Fix:**
```bash
# Create badges branch if missing
git checkout --orphan badges
git rm -rf .
mkdir badges
echo "Badge storage branch" > README.md
git add .
git commit -m "Initialize badges branch"
git push origin badges
git checkout main
```

### Security Scan Warnings

**Check:**
1. View Semgrep/Bandit output in workflow logs
2. Review findings in Security tab
3. Check if issues are false positives

**Fix:**
- Address genuine security issues
- Add suppressions for false positives (with comments)
- Update security rules if needed

## Environment Variables

The following environment variables can be configured in GitHub repository settings (Settings → Secrets and variables → Actions):

### Optional:
- `CODECOV_TOKEN` - Token for Codecov uploads (optional, works without it for public repos)

## Cost Optimization

### GitHub Actions Minutes:
- Public repositories: Free unlimited minutes
- Private repositories: 2,000 minutes/month free (varies by plan)

### Optimization Tips:
1. Use caching for dependencies (already configured)
2. Set timeouts on jobs (configured to 30 minutes)
3. Use `continue-on-error` for non-critical checks
4. Parallelize independent jobs where possible

## Security

### Security Scanning:
- **Bandit** - Python security linter (high severity issues)
- **Semgrep** - Advanced security scanning with SARIF output
- **Ruff** - Code quality and potential security issues

### SARIF Upload:
Security findings are uploaded to GitHub Security tab for:
- Centralized security monitoring
- Integration with Dependabot alerts
- Security policy enforcement

### Secrets Management:
- Never commit secrets to repository
- Use GitHub Secrets for sensitive data
- Rotate tokens regularly
- Use least-privilege access

## Maintenance

### Regular Tasks:

**Weekly:**
- Review workflow run history
- Check for failed runs
- Update dependencies if needed

**Monthly:**
- Review security findings
- Update GitHub Actions versions
- Optimize workflow performance
- Review branch protection rules

**Quarterly:**
- Audit required status checks
- Review and update security scanning rules
- Evaluate new GitHub Actions features
- Update documentation

## CI/CD Metrics

Track these metrics to ensure CI/CD health:

### Performance:
- Workflow duration (target: < 15 minutes)
- Success rate (target: > 95%)
- Time to feedback (target: < 10 minutes)

### Quality:
- Test coverage (target: > 70%)
- Security findings (target: 0 high severity)
- Code quality score (target: A)

### Reliability:
- Flaky test rate (target: < 5%)
- Workflow availability (target: > 99%)
- Badge update success (target: 100%)

## Advanced Configuration

### Custom Workflow Triggers:

Add to workflow file:
```yaml
on:
  schedule:
    # Run daily at 2 AM UTC
    - cron: '0 2 * * *'
  
  repository_dispatch:
    # Allow external triggers
    types: [custom-event]
```

### Matrix Testing:

Test multiple versions:
```yaml
jobs:
  test:
    strategy:
      matrix:
        python-version: [3.10, 3.11, 3.12]
        node-version: [18, 20]
```

### Conditional Steps:

Run steps conditionally:
```yaml
- name: Deploy to production
  if: github.ref == 'refs/heads/main' && github.event_name == 'push'
  run: ./deploy.sh
```

## Integration with Other Tools

### Codecov Integration:
- Automatic coverage uploads
- Coverage trends and insights
- PR coverage diff reports

### GitHub Security:
- SARIF uploads for security findings
- Integration with Dependabot
- Security advisories

### Docker Registry:
Ready for integration with:
- GitHub Container Registry (GHCR)
- Docker Hub
- AWS ECR
- Google Container Registry

## Future Enhancements

Planned improvements:
- 🔄 Automated deployment to staging/production
- 📊 Performance benchmarking
- 🔍 Additional security scanners
- 📦 Artifact management
- 🚀 Release automation
- 📈 Enhanced metrics and reporting
- 🔔 Slack/Discord notifications
- 🏷️ Automatic semantic versioning

## Support

For CI/CD issues:
1. Check workflow logs in Actions tab
2. Review this documentation
3. Check GitHub Actions documentation: https://docs.github.com/en/actions
4. Open an issue with workflow run URL and error details

---

**Last Updated:** 2025-11-10
**Workflow Version:** 1.0
**Status:** ✅ Production Ready
