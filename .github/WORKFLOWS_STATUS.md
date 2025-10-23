
# GitHub Actions Workflows Status

## ✅ Active & Working Workflows

### Core CI/CD
- **aurora-ci.yml** - Main CI pipeline with quality gates, linting, and testing
- **ci-quick.yml** - Fast PR checks for quick feedback
- **ci.yml** - Standard CI with comprehensive quality gates
- **ci-autofix.yml** - Auto-fixes linting issues and commits them
- **aurora-e2e.yml** - End-to-end API testing
- **aurora-release.yml** - Automated releases with semantic versioning
- **docker-multiarch.yml** - Multi-architecture Docker builds (AMD64/ARM64)

### Utilities
- **manual.yml** - Manual workflow dispatch for custom commands

## ⚙️ Configuration Required

These workflows are functional but require secrets/configuration:

### Deployment Workflows
- **deploy-ghcr.yml** - Deploy via GitHub Container Registry
  - Required: `SSH_HOST`, `SSH_USER`, `SSH_KEY`
  - Optional: `SSH_PORT`, `CF_TUNNEL_TOKEN`, `AURORA_HEALTH_TOKEN`
  
- **deploy-ssh.yml** - Direct SSH deployment
  - Required: `SSH_HOST`, `SSH_USER`, `SSH_KEY`
  - Optional: `SSH_PORT`

- **rollback.yml** - Deployment rollback
  - Required: `SSH_HOST`, `SSH_USER`, `SSH_KEY`
  - Optional: `SSH_PORT`

## 🚫 Disabled Workflows

These workflows are intentionally disabled:

- **deep-scan.yml** - Redundant with aurora-ci.yml
- **aurora-e2e-cached.yml** - Requires full infrastructure setup
- **aurora-e2e-extended.yml** - Requires multi-language compilers (Go, Rust, .NET)

## 📊 Workflow Health Summary

| Category | Status | Count |
|----------|--------|-------|
| Active & Passing | ✅ | 7 |
| Needs Configuration | ⚙️ | 3 |
| Intentionally Disabled | 🚫 | 3 |

## 🔧 Setup Instructions

### To Enable Deployment Workflows:

1. Go to your repository Settings → Secrets and variables → Actions
2. Add the required secrets:
   ```
   SSH_HOST=your.server.com
   SSH_USER=deployuser
   SSH_KEY=<your-private-key>
   SSH_PORT=22 (optional, defaults to 22)
   ```
3. Uncomment the `push:` trigger in the workflow file
4. Push to `main` branch to trigger automatic deployments

### To Enable Extended E2E Testing:

1. Ensure your runner has:
   - Go 1.21+
   - Rust (stable)
   - .NET 8.0+
2. Uncomment `workflow_dispatch:` in aurora-e2e-extended.yml
3. Manually trigger from Actions tab

## 🐛 Troubleshooting

If a workflow fails:

1. Check the workflow logs in the Actions tab
2. Verify all required secrets are configured
3. Ensure the workflow is not disabled
4. Check for recent changes to workflow files
5. Review the specific workflow's requirements above

## 📝 Notes

- All workflows use the latest Ubuntu runner
- Python 3.11 is the standard version
- Node.js 18 is used for TypeScript/JavaScript workflows
- Caching is enabled for all language dependencies
- Auto-fix workflows will skip CI on commits with `[skip ci]`
