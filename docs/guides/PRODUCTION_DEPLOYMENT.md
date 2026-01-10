# Aurora-X Production Deployment Guide

## Quick Start (Docker Compose)

### Standard Deployment

```bash
# Set required secret
export AURORA_TOKEN_SECRET=$(python -c 'import secrets; print(secrets.token_hex(32))')

# Deploy
docker compose -f compose.prod.yaml up -d

# Verify
curl http://127.0.0.1:8000/healthz
```

### Production-Tuned Deployment

```bash
# Use production compose file
export VERSION=v0.1.0
export AURORA_TOKEN_SECRET=$(python -c 'import secrets; print(secrets.token_hex(32))')
export ENVIRONMENT=prod
export PORT=8000

docker compose -f compose.prod.yaml pull
docker compose -f compose.prod.yaml up -d
```

## Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `AURORA_TOKEN_SECRET` | ✅ Yes | - | Secret token (64 hex chars) |
| `ENVIRONMENT` | No | `prod` | Environment name |
| `PORT` | No | `8000` | Container port |
| `DATABASE_URL` | No | - | PostgreSQL connection string |
| `CORS_ORIGINS` | No | `*` | Comma-separated allowed origins |

### Resource Limits

Default limits in `compose.prod.yaml`:
- **CPU**: 2.0 cores (limit), 0.5 cores (reservation)
- **Memory**: 2GB (limit), 512MB (reservation)

Adjust based on your VM capacity:
```yaml
deploy:
  resources:
    limits:
      cpus: '4.0'      # Adjust
      memory: 4G       # Adjust
```

## Monitoring

### Health Checks

```bash
# Container health
docker compose -f compose.prod.yaml ps

# Endpoint health
curl http://127.0.0.1:8000/healthz
```

### Logs

```bash
# Follow logs
docker compose -f compose.prod.yaml logs -f api

# Structured logs
docker compose -f compose.prod.yaml logs api | grep -E '"rid"|"status"|"duration_ms"'

# Errors only
docker compose -f compose.prod.yaml logs api | grep -i error
```

### Metrics (Optional - When Prometheus Enabled)

```bash
# Scrape metrics
curl http://127.0.0.1:8000/metrics
```

## Security

### Secrets Management

**Production:**
- Use a secrets manager (AWS Secrets Manager, HashiCorp Vault, etc.)
- Rotate `AURORA_TOKEN_SECRET` regularly
- Never commit secrets to version control

**Docker Compose:**
```bash
# Use .env file (not committed)
echo "AURORA_TOKEN_SECRET=$(python -c 'import secrets; print(secrets.token_hex(32))')" > .env.prod
docker compose -f compose.prod.yaml --env-file .env.prod up -d
```

### CORS Configuration

```bash
# Restrict origins
export CORS_ORIGINS="https://app.example.com,https://admin.example.com"
docker compose -f compose.prod.yaml up -d
```

## Scaling

### Single VM (Current)

- One container instance
- Resource limits as configured
- Suitable for: < 1000 req/min

### Multiple VMs (Future)

- Use load balancer (nginx, HAProxy)
- Deploy same `compose.prod.yaml` on each VM
- Health checks on all instances

### Kubernetes (Future)

- Use provided K8s manifests (if available)
- Horizontal Pod Autoscaler (HPA) for auto-scaling
- Service mesh for advanced routing

## Backup & Recovery

### Configuration Backup

```bash
# Backup environment variables
env | grep -E 'AURORA_|DATABASE_|CORS_' > backup.env

# Backup compose file
cp compose.prod.yaml backup/
```

### Rollback

```bash
# Pull previous version
export VERSION=v0.0.9  # Previous version
docker compose -f compose.prod.yaml pull
docker compose -f compose.prod.yaml up -d
```

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker compose -f compose.prod.yaml logs api

# Check health
docker compose -f compose.prod.yaml ps

# Verify secret
docker compose -f compose.prod.yaml config | grep AURORA_TOKEN_SECRET
```

### High Memory Usage

```bash
# Check resource usage
docker stats aurora-x-api

# Adjust limits in compose.prod.yaml
# Increase memory limit or investigate memory leaks
```

### Rate Limiting Issues

```bash
# Check rate limit headers
curl -v http://127.0.0.1:8000/healthz

# Adjust in aurora_x/ratelimit.py if needed
```

## Performance Tuning

### Logging

```yaml
# In compose.prod.yaml
logging:
  driver: "json-file"
  options:
    max-size: "10m"    # Rotate at 10MB
    max-file: "3"      # Keep 3 files
```

### Health Checks

```yaml
# Adjust intervals based on startup time
healthcheck:
  interval: 10s    # Check every 10s
  timeout: 3s     # 3s timeout
  retries: 10     # 10 retries before unhealthy
  start_period: 40s  # 40s grace period
```

## Next Steps

1. **Monitoring**: Add Prometheus + Grafana (optional)
2. **Alerting**: Set up alerts for SLOs
3. **Logging**: Forward logs to centralized system
4. **Backup**: Automate configuration backups
5. **Scaling**: Plan for multi-VM or K8s deployment

---

**Status**: Production-ready with `compose.prod.yaml`
