# Aurora-X Operations Guide

## Deployment

### Docker Compose (Single Node)

```bash
# Set required environment variable
export AURORA_TOKEN_SECRET=$(python -c 'import secrets; print(secrets.token_hex(32))')

# Start services
docker compose up -d

# Check health
curl http://127.0.0.1:8000/healthz

# View logs
docker compose logs -f api
```

### Docker Run

```bash
docker run -d \
  --name aurora-x \
  -p 8000:8000 \
  -e AURORA_TOKEN_SECRET=$(python -c 'import secrets; print(secrets.token_hex(32))') \
  ghcr.io/chango112595-cell/Aurora-x:latest
```

### Kubernetes (Optional)

See `k8s/` directory for Kubernetes manifests (if available).

## Configuration

### Required Environment Variables

- `AURORA_TOKEN_SECRET`: Secret token for authentication (64 hex characters)

### Optional Environment Variables

- `HOST`: Bind host (default: `127.0.0.1`)
- `PORT`: Bind port (default: `8000`)
- `ENVIRONMENT`: Environment name (default: `dev`)
- `DATABASE_URL`: PostgreSQL connection string (optional)
- `CORS_ORIGINS`: Comma-separated list of allowed CORS origins (optional)

### Configuration Schema

The application uses Pydantic for configuration validation. Invalid configurations will fail fast on startup.

## Health Checks

### Endpoint

```bash
curl http://127.0.0.1:8000/healthz
```

Expected response:
```json
{
  "ok": true,
  "t08_enabled": false,
  "ts": 1234567890.123
}
```

### Docker Health Check

The Dockerfile includes a health check that runs every 10 seconds:
```dockerfile
HEALTHCHECK --interval=10s --timeout=3s --retries=10 \
    CMD curl -fsS http://127.0.0.1:8000/healthz || exit 1
```

## Monitoring

### Logs

Structured logs are emitted with request IDs, paths, status codes, and durations:

```json
{
  "rid": "uuid-here",
  "path": "/api/endpoint",
  "method": "GET",
  "status": 200,
  "duration_ms": 45
}
```

### Request IDs

All responses include an `X-Request-ID` header for correlation.

### Rate Limiting

Rate limits are enforced per IP:
- Default: 120 requests per 60 seconds
- Headers: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`
- 429 response when limit exceeded

## Troubleshooting

### API Won't Start

1. Check `AURORA_TOKEN_SECRET` is set
2. Verify port 8000 is not in use
3. Check logs: `docker compose logs api` or `/tmp/aurora.log` in CI

### Health Check Failing

1. Verify `/healthz` endpoint is accessible
2. Check application logs for errors
3. Verify dependencies are installed

### Rate Limit Issues

1. Check `X-RateLimit-*` headers in responses
2. Adjust limits in `aurora_x/ratelimit.py` if needed
3. Consider using Redis-backed rate limiting for distributed deployments

## Rollback

### Docker Image Rollback

```bash
# Pull previous version
docker pull ghcr.io/chango112595-cell/Aurora-x:v0.1.0

# Stop current container
docker stop aurora-x

# Run previous version
docker run -d \
  --name aurora-x \
  -p 8000:8000 \
  -e AURORA_TOKEN_SECRET=$AURORA_TOKEN_SECRET \
  ghcr.io/chango112595-cell/Aurora-x:v0.1.0
```

### Docker Compose Rollback

```yaml
# In compose.yaml, change image tag
image: ghcr.io/chango112595-cell/Aurora-x:v0.1.0
```

Then:
```bash
docker compose pull
docker compose up -d
```

## Security

### Secret Management

- Never commit `AURORA_TOKEN_SECRET` to version control
- Use GitHub Secrets for CI/CD
- Rotate secrets regularly
- Use environment-specific secrets for production

### CORS Configuration

Set `CORS_ORIGINS` environment variable to restrict origins:
```bash
export CORS_ORIGINS="https://app.example.com,https://admin.example.com"
```

### Dependency Scanning

Run security scans regularly:
```bash
pip-audit -r requirements.txt
```

CI automatically runs `pip-audit` on PRs and weekly.

## Performance

### Request Timing

All requests are logged with duration. Check logs for slow requests (>1s threshold).

### Rate Limiting

Default limits are conservative. Adjust based on:
- Expected traffic patterns
- Server capacity
- Business requirements

## Backup and Recovery

### Database (if used)

If using PostgreSQL:
```bash
# Backup
pg_dump $DATABASE_URL > backup.sql

# Restore
psql $DATABASE_URL < backup.sql
```

### Configuration

Backup environment variables and secrets securely.

## Support

For issues:
1. Check logs and health endpoint
2. Review GitHub Actions workflow runs
3. Check CONTRIBUTING.md for CI triage
4. Open an issue with logs and error details
