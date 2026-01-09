# Changelog

All notable changes to Aurora-X will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Future features will be listed here

### Changed
- Future changes will be listed here

### Fixed
- Future fixes will be listed here

## [0.1.0] - 2026-01-09

### Added
- **SPEC-1**: E2E workflow reliability with 180s timeout, log artifacts, fork-safe secrets
- **SPEC-2**: Production Dockerfile (`Dockerfile.api`), Docker Compose setup, GHCR release workflow
- **SPEC-3**: TimingMiddleware with structured JSON logs, request IDs, duration tracking
- **SPEC-4**: CORS middleware, rate limiting (120 req/60s), automated pip-audit security scanning
- **SPEC-5**: pytest smoke tests for `/healthz` endpoint, CI integration
- **SPEC-6**: Developer documentation (CONTRIBUTING.md, OPERATIONS.md), Makefile commands
- **SPEC-7**: Runtime configuration schema with Pydantic validation, DATABASE_URL support
- **SPEC-8**: Tag-based releases with automatic GitHub Releases and Docker image publishing

### Infrastructure
- Docker Compose configuration for single-VM deployment
- GitHub Actions workflows for Docker builds, security scanning, E2E testing
- Health check endpoint (`/healthz`) with structured response
- Structured logging with request correlation IDs

### Documentation
- `CONTRIBUTING.md` - Developer guide with CI triage
- `OPERATIONS.md` - Deployment, monitoring, and rollback procedures
- `GO_LIVE_EXECUTION.md` - Step-by-step go-live plan
- `CUTOVER_QUICK_REFERENCE.md` - Quick reference card
- `.github/pull_request_template.md` - PR template with documentation links
- `RELEASE_TEMPLATE.md` - Template for future releases

### Security
- Rate limiting middleware (120 requests per 60 seconds per IP)
- CORS policy (configurable via `CORS_ORIGINS` environment variable)
- Automated dependency vulnerability scanning (pip-audit)
- Secret management via GitHub Secrets and environment variables

### Observability
- Request timing middleware with `duration_ms` tracking
- Structured JSON logs with `rid`, `path`, `method`, `status`
- Request ID headers (`X-Request-ID`) for correlation
- Health check endpoint for monitoring

---

## Release Types

- **[Unreleased]**: Changes in development
- **[Major.Minor.Patch]**: Released versions
  - **Major**: Breaking changes
  - **Minor**: New features, backward compatible
  - **Patch**: Bug fixes, minor improvements

## How to Update

1. Add new entries under `[Unreleased]` as you work
2. When releasing, move `[Unreleased]` items to new version section
3. Update date in version header
4. Commit with message: `chore: Update CHANGELOG for v0.1.1`
