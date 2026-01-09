# Contributing to Aurora-X

## Development Setup

### Quick Start

1. Clone the repository:
   ```bash
   git clone https://github.com/chango112595-cell/Aurora-x.git
   cd Aurora-x
   ```

2. Install dependencies:
   ```bash
   make install-deps
   # or
   pip install -e ".[dev]"
   ```

3. Run locally:
   ```bash
   make run
   # or
   AURORA_TOKEN_SECRET=$(python -c 'import secrets; print(secrets.token_hex(32))') uvicorn aurora_x.serve:app --reload
   ```

## CI/CD Workflow

### Triggering E2E Tests

To trigger the E2E workflow on a specific branch:

```bash
gh workflow run "aurora-e2e.yml" --ref <branch-name>
```

### Finding Workflow Runs

To find the latest run for a PR:

```powershell
# PowerShell
$prNumber = 177
$runs = gh run list --workflow "aurora-e2e.yml" --json databaseId,headBranch,pullRequests --limit 20 | ConvertFrom-Json
$prRun = $runs | Where-Object { $_.pullRequests.number -eq $prNumber } | Select-Object -First 1
$runId = $prRun.databaseId
gh run view $runId
```

### Downloading Artifacts

```bash
# Download E2E logs
gh run download <run-id> -n aurora-e2e-logs -D e2e-logs

# View logs
cat e2e-logs/aurora.log
cat e2e-logs/aurora.target
```

### Expected Workflow Steps

The E2E workflow should have these steps in order:

1. **Launch API** - Starts the FastAPI server via `scripts/ci-start.sh`
2. **Wait for API** - Polls `/healthz` for up to 180 seconds
3. **Run tests** - Executes pytest smoke tests
4. **Teardown** - Tails logs and kills the server
5. **Ensure log files exist** - Creates log files if missing
6. **Upload logs** - Uploads artifacts (always, with warn on missing files)

## Testing

### Run Tests Locally

```bash
# Run all tests
make test
# or
pytest

# Run specific test file
pytest tests/test_healthz.py -v

# Run with coverage
make cov
```

### Smoke Tests

The smoke tests verify basic functionality:

- `/healthz` endpoint returns 200
- Response structure is valid

## Code Quality

### Linting

```bash
make lint
# or
ruff check .
```

### Security Scanning

```bash
make sec
# or
pip-audit -r requirements.txt
```

### All Quality Gates

```bash
make gates
```

## Docker Development

### Build and Run

```bash
# Build image
docker build -f Dockerfile.api -t aurora-x:latest .

# Run container
docker run -e AURORA_TOKEN_SECRET=$(python -c 'import secrets; print(secrets.token_hex(32))') -p 8000:8000 aurora-x:latest

# Or use Docker Compose
docker compose up
```

### Health Check

```bash
curl http://127.0.0.1:8000/healthz
```

## Troubleshooting CI Failures

### Common Issues

1. **YAML syntax errors**: Check workflow files with `yamllint` or pre-commit hooks
2. **Missing secrets**: Ensure `AURORA_TOKEN_SECRET` is set in repository secrets
3. **API startup failures**: Check `/tmp/aurora.log` in artifacts
4. **Timeout issues**: Increase wait time in "Wait for API" step if needed

### Debugging Workflow Runs

1. Download artifacts: `gh run download <run-id> -n aurora-e2e-logs`
2. Check logs: `cat e2e-logs/aurora.log`
3. Verify target: `cat e2e-logs/aurora.target`
4. Re-run workflow: `gh workflow run "aurora-e2e.yml" --ref <branch>`

## Pull Request Process

1. Create a feature branch from `main`
2. Make your changes
3. Run quality gates locally: `make gates`
4. Push and create a PR
5. Ensure all CI checks pass
6. Request review

## Release Process

Releases are automated via GitHub Actions:

- Pushing to `main` triggers Docker image build and push to GHCR
- Tagging with `v*` creates a GitHub Release
- Images are tagged with: `latest`, `sha-<commit>`, and semantic version tags
