# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Pre-commit hooks for code quality (black, ruff, isort, mypy, bandit)
- CODEOWNERS file for code review assignments
- Pull request and issue templates
- Dependabot configuration for automated dependency updates
- CodeQL security scanning workflow
- Semantic release automation with auto-generated changelogs

## [3.0.0] - 2025-11-10

### Added
- Comprehensive API documentation with OpenAPI/Swagger
- Complete user guide with examples and troubleshooting
- Developer guide with architecture and contribution guidelines
- Production deployment guide with Docker, Kubernetes, and scaling strategies
- Enhanced monitoring and alerting with Prometheus and Grafana
- Database migrations with Alembic
- Performance optimizations and caching improvements
- JWT-based authentication and authorization
- Backup and disaster recovery procedures
- CI/CD automation with GitHub Actions

### Changed
- FastAPI application now includes comprehensive metadata
- Increased test coverage to >80%
- Improved error handling and logging
- Enhanced security with rate limiting and input validation

### Fixed
- Various performance bottlenecks
- Memory leaks in long-running processes
- Race conditions in concurrent requests

## [0.2.0] - T02 Checkpoint
### Added
- Persistent corpus storage (JSONL + SQLite)
- Signature normalization and matching
- TF-IDF tokenization for post-conditions
- CLI corpus query interface
- Seeding system with bias control

## [0.1.0] - T01 Checkpoint
### Added
- AST-based synthesis engine
- Beam search with mutations
- Unittest and fuzzing generation
- Sandbox runner with timeouts
- HTML reports with call graphs
- Auto-debugger for shrinking inputs

[Unreleased]: https://github.com/chango112595-cell/Aurora-x/compare/v3.0.0...HEAD
[3.0.0]: https://github.com/chango112595-cell/Aurora-x/releases/tag/v3.0.0
[0.2.0]: https://github.com/chango112595-cell/Aurora-x/releases/tag/v0.2.0
[0.1.0]: https://github.com/chango112595-cell/Aurora-x/releases/tag/v0.1.0