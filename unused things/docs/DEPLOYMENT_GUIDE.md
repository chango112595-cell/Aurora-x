# Aurora-X Deployment Guide

Complete guide for deploying Aurora-X in production environments.

---

## Table of Contents

1. [Deployment Overview](#deployment-overview)
2. [Prerequisites](#prerequisites)
3. [Docker Deployment](#docker-deployment)
4. [Kubernetes Deployment](#kubernetes-deployment)
5. [Load Balancing with Nginx](#load-balancing-with-nginx)
6. [Database Setup](#database-setup)
7. [Redis Cache Setup](#redis-cache-setup)
8. [Environment Configuration](#environment-configuration)
9. [SSL/TLS Configuration](#ssltls-configuration)
10. [Monitoring & Logging](#monitoring--logging)
11. [Backup & Disaster Recovery](#backup--disaster-recovery)
12. [Scaling Strategy](#scaling-strategy)
13. [Production Checklist](#production-checklist)
14. [Troubleshooting](#troubleshooting)

---

## Deployment Overview

Aurora-X supports multiple deployment strategies:

| Method | Best For | Complexity | Scalability |
|--------|----------|------------|-------------|
| **Docker Compose** | Small deployments, testing | Low | Limited |
| **Kubernetes** | Production, enterprise | Medium | High |
| **Nginx + Systemd** | Traditional servers | Low | Medium |
| **Cloud Services** | AWS, GCP, Azure | Medium | High |

**Recommended:** Kubernetes for production, Docker Compose for development.

---

## Prerequisites

### Hardware Requirements

**Minimum (Development):**
- CPU: 2 cores
- RAM: 4 GB
- Storage: 20 GB
- Network: 10 Mbps

**Recommended (Production):**
- CPU: 4-8 cores
- RAM: 16-32 GB
- Storage: 100 GB SSD
- Network: 100 Mbps+

### Software Requirements

- **Docker**: 20.10+ and Docker Compose 2.0+
- **Kubernetes**: 1.24+ (if using K8s)
- **PostgreSQL**: 14+
- **Redis**: 7.0+
- **Nginx**: 1.20+ (for load balancing)

---

## Docker Deployment

### Single Server Deployment

#### 1. Prepare Environment

```bash
# Create deployment directory
mkdir -p /opt/aurora-x
cd /opt/aurora-x

# Clone repository
git clone https://github.com/chango112595-cell/Aurora-x.git .

# Create environment file
cat > .env << EOF
# Aurora-X Configuration
AURORA_PORT=5002
DEBUG=false
LOG_LEVEL=INFO

# Database
DATABASE_URL=postgresql://aurora:password@postgres:5432/aurora_db

# Redis
REDIS_URL=redis://redis:6379/0

# Security
SECRET_KEY=$(openssl rand -hex 32)
JWT_SECRET=$(openssl rand -hex 32)

# Performance
CACHE_TTL=300
MAX_WORKERS=4
EOF
```

#### 2. Update docker-compose.yml

```yaml
version: '3.8'

services:
  # Backend API
  aurora-backend:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: aurora-backend
    restart: unless-stopped
    ports:
      - "5002:5002"
    environment:
      - AURORA_PORT=5002
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - SECRET_KEY=${SECRET_KEY}
      - DEBUG=false
    depends_on:
      - postgres
      - redis
    volumes:
      - ./runs:/app/runs
      - ./specs:/app/specs
      - ./logs:/app/logs
    networks:
      - aurora-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5002/healthz"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  # PostgreSQL Database
  postgres:
    image: postgres:14-alpine
    container_name: aurora-postgres
    restart: unless-stopped
    environment:
      - POSTGRES_DB=aurora_db
      - POSTGRES_USER=aurora
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    volumes:
      - postgres-data:/var/lib/postgresql/data
      - ./backups:/backups
    networks:
      - aurora-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U aurora"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis Cache
  redis:
    image: redis:7-alpine
    container_name: aurora-redis
    restart: unless-stopped
    command: redis-server --appendonly yes --maxmemory 2gb --maxmemory-policy allkeys-lru
    volumes:
      - redis-data:/data
    networks:
      - aurora-network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Prometheus Monitoring
  prometheus:
    image: prom/prometheus:latest
    container_name: aurora-prometheus
    restart: unless-stopped
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--storage.tsdb.retention.time=30d'
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus
    ports:
      - "9090:9090"
    networks:
      - aurora-network

  # Grafana Dashboard
  grafana:
    image: grafana/grafana:latest
    container_name: aurora-grafana
    restart: unless-stopped
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
      - GF_SERVER_ROOT_URL=http://localhost:3000
    volumes:
      - grafana-data:/var/lib/grafana
      - ./monitoring/grafana/dashboards:/etc/grafana/provisioning/dashboards
    ports:
      - "3000:3000"
    networks:
      - aurora-network
    depends_on:
      - prometheus

  # Nginx Load Balancer
  nginx:
    image: nginx:alpine
    container_name: aurora-nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
      - ./nginx/logs:/var/log/nginx
    networks:
      - aurora-network
    depends_on:
      - aurora-backend

volumes:
  postgres-data:
  redis-data:
  prometheus-data:
  grafana-data:

networks:
  aurora-network:
    driver: bridge
```

#### 3. Deploy

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Check status
docker-compose ps

# Test health
curl http://localhost:5002/healthz
```

### Production Docker Configuration

```dockerfile
# Dockerfile.production
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

# Production image
FROM python:3.11-slim

# Create non-root user
RUN useradd -m -u 1000 aurora && \
    mkdir -p /app /app/logs /app/runs /app/specs && \
    chown -R aurora:aurora /app

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy wheels and install
COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .
RUN pip install --no-cache /wheels/*

# Copy application
COPY --chown=aurora:aurora . .

# Switch to non-root user
USER aurora

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:5002/healthz || exit 1

# Expose port
EXPOSE 5002

# Start application
CMD ["python", "-m", "aurora_x.serve"]
```

Build and deploy:
```bash
docker build -f Dockerfile.production -t aurora-x:latest .
docker push your-registry/aurora-x:latest
```

---

## Kubernetes Deployment

### 1. Create Namespace

```yaml
# namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: aurora-x
```

### 2. ConfigMap

```yaml
# configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: aurora-config
  namespace: aurora-x
data:
  AURORA_PORT: "5002"
  DEBUG: "false"
  LOG_LEVEL: "INFO"
  CACHE_TTL: "300"
  MAX_WORKERS: "4"
```

### 3. Secrets

```yaml
# secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: aurora-secrets
  namespace: aurora-x
type: Opaque
stringData:
  DATABASE_URL: "postgresql://aurora:password@postgres:5432/aurora_db"
  REDIS_URL: "redis://redis:6379/0"
  SECRET_KEY: "your-secret-key-here"
  JWT_SECRET: "your-jwt-secret-here"
```

### 4. PostgreSQL Deployment

```yaml
# postgres-deployment.yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
  namespace: aurora-x
spec:
  serviceName: postgres
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:14-alpine
        ports:
        - containerPort: 5432
        env:
        - name: POSTGRES_DB
          value: aurora_db
        - name: POSTGRES_USER
          value: aurora
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: aurora-secrets
              key: POSTGRES_PASSWORD
        volumeMounts:
        - name: postgres-data
          mountPath: /var/lib/postgresql/data
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
  volumeClaimTemplates:
  - metadata:
      name: postgres-data
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 20Gi
---
apiVersion: v1
kind: Service
metadata:
  name: postgres
  namespace: aurora-x
spec:
  selector:
    app: postgres
  ports:
  - port: 5432
    targetPort: 5432
  clusterIP: None
```

### 5. Redis Deployment

```yaml
# redis-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: redis
  namespace: aurora-x
spec:
  replicas: 1
  selector:
    matchLabels:
      app: redis
  template:
    metadata:
      labels:
        app: redis
    spec:
      containers:
      - name: redis
        image: redis:7-alpine
        command:
        - redis-server
        - --appendonly
        - "yes"
        - --maxmemory
        - "2gb"
        - --maxmemory-policy
        - allkeys-lru
        ports:
        - containerPort: 6379
        volumeMounts:
        - name: redis-data
          mountPath: /data
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
      volumes:
      - name: redis-data
        persistentVolumeClaim:
          claimName: redis-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: redis
  namespace: aurora-x
spec:
  selector:
    app: redis
  ports:
  - port: 6379
    targetPort: 6379
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: redis-pvc
  namespace: aurora-x
spec:
  accessModes:
  - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
```

### 6. Aurora-X Backend Deployment

```yaml
# aurora-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: aurora-backend
  namespace: aurora-x
spec:
  replicas: 3
  selector:
    matchLabels:
      app: aurora-backend
  template:
    metadata:
      labels:
        app: aurora-backend
    spec:
      containers:
      - name: aurora-backend
        image: your-registry/aurora-x:latest
        ports:
        - containerPort: 5002
        envFrom:
        - configMapRef:
            name: aurora-config
        - secretRef:
            name: aurora-secrets
        livenessProbe:
          httpGet:
            path: /healthz
            port: 5002
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /healthz
            port: 5002
          initialDelaySeconds: 10
          periodSeconds: 5
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
        volumeMounts:
        - name: runs
          mountPath: /app/runs
        - name: specs
          mountPath: /app/specs
      volumes:
      - name: runs
        persistentVolumeClaim:
          claimName: aurora-runs-pvc
      - name: specs
        persistentVolumeClaim:
          claimName: aurora-specs-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: aurora-backend
  namespace: aurora-x
spec:
  selector:
    app: aurora-backend
  ports:
  - port: 80
    targetPort: 5002
  type: LoadBalancer
```

### 7. Horizontal Pod Autoscaler

```yaml
# hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: aurora-backend-hpa
  namespace: aurora-x
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: aurora-backend
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

### 8. Ingress

```yaml
# ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: aurora-ingress
  namespace: aurora-x
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  tls:
  - hosts:
    - aurora.example.com
    secretName: aurora-tls
  rules:
  - host: aurora.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: aurora-backend
            port:
              number: 80
```

### Deploy to Kubernetes

```bash
# Apply all configurations
kubectl apply -f namespace.yaml
kubectl apply -f configmap.yaml
kubectl apply -f secrets.yaml
kubectl apply -f postgres-deployment.yaml
kubectl apply -f redis-deployment.yaml
kubectl apply -f aurora-deployment.yaml
kubectl apply -f hpa.yaml
kubectl apply -f ingress.yaml

# Check deployment status
kubectl get pods -n aurora-x
kubectl get svc -n aurora-x
kubectl get ingress -n aurora-x

# View logs
kubectl logs -f deployment/aurora-backend -n aurora-x

# Scale manually
kubectl scale deployment/aurora-backend --replicas=5 -n aurora-x
```

---

## Load Balancing with Nginx

### Generate Configuration

Aurora-X includes a script to generate Nginx configuration:

```bash
./scripts/generate-nginx-config.sh
```

This creates `/tmp/aurora-nginx.conf` with:
- Load balancing across multiple backend instances
- SSL/TLS configuration
- Health checks
- Gzip compression
- Security headers

### Manual Nginx Configuration

```nginx
# /etc/nginx/sites-available/aurora-x

upstream aurora_backend {
    least_conn;
    server 127.0.0.1:5001 max_fails=3 fail_timeout=30s;
    server 127.0.0.1:5002 max_fails=3 fail_timeout=30s;
    server 127.0.0.1:5003 max_fails=3 fail_timeout=30s;
    keepalive 32;
}

server {
    listen 80;
    server_name aurora.example.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name aurora.example.com;
    
    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/aurora.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/aurora.example.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    # Security Headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    
    # Gzip Compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css application/json application/javascript text/xml;
    
    # API Endpoints
    location /api/ {
        proxy_pass http://aurora_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # Health Check (no logging)
    location /healthz {
        access_log off;
        proxy_pass http://aurora_backend;
    }
    
    # Static Files
    location / {
        proxy_pass http://aurora_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Enable and reload:
```bash
sudo ln -s /etc/nginx/sites-available/aurora-x /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

## Database Setup

### PostgreSQL Configuration

```bash
# Install PostgreSQL
sudo apt-get install postgresql-14

# Create database and user
sudo -u postgres psql << EOF
CREATE DATABASE aurora_db;
CREATE USER aurora WITH PASSWORD 'your-secure-password';
GRANT ALL PRIVILEGES ON DATABASE aurora_db TO aurora;
\q
EOF

# Configure PostgreSQL for performance
sudo nano /etc/postgresql/14/main/postgresql.conf
```

Recommended settings:
```ini
# Memory
shared_buffers = 4GB
effective_cache_size = 12GB
maintenance_work_mem = 1GB
work_mem = 64MB

# Checkpoint
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100

# Performance
random_page_cost = 1.1
effective_io_concurrency = 200
max_worker_processes = 8
max_parallel_workers_per_gather = 4
max_parallel_workers = 8
```

### Run Migrations

```bash
# Upgrade to latest schema
alembic upgrade head

# Create new migration
alembic revision --autogenerate -m "Description"

# Downgrade if needed
alembic downgrade -1
```

---

## Redis Cache Setup

### Redis Configuration

```bash
# Install Redis
sudo apt-get install redis-server

# Configure Redis
sudo nano /etc/redis/redis.conf
```

Production settings:
```ini
# Network
bind 127.0.0.1
port 6379
protected-mode yes

# Memory
maxmemory 4gb
maxmemory-policy allkeys-lru

# Persistence
save 900 1
save 300 10
save 60 10000
appendonly yes
appendfsync everysec

# Performance
tcp-backlog 511
timeout 300
tcp-keepalive 300
```

Restart Redis:
```bash
sudo systemctl restart redis
sudo systemctl enable redis
```

### Redis Cluster (Optional)

For high availability:

```bash
# Create 6 instances (3 masters, 3 replicas)
redis-cli --cluster create \
  127.0.0.1:7000 127.0.0.1:7001 127.0.0.1:7002 \
  127.0.0.1:7003 127.0.0.1:7004 127.0.0.1:7005 \
  --cluster-replicas 1
```

---

## Environment Configuration

### Production .env File

```bash
# Application
AURORA_PORT=5002
DEBUG=false
LOG_LEVEL=INFO
ENVIRONMENT=production

# Database
DATABASE_URL=postgresql://aurora:password@localhost:5432/aurora_db
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=10

# Redis
REDIS_URL=redis://localhost:6379/0
REDIS_PASSWORD=your-redis-password

# Cache
CACHE_TTL=300
MAX_CACHE_SIZE=10000

# Security
SECRET_KEY=$(openssl rand -hex 32)
JWT_SECRET=$(openssl rand -hex 32)
JWT_EXPIRATION=3600
CORS_ORIGINS=https://aurora.example.com

# Performance
MAX_WORKERS=8
WORKER_TIMEOUT=300
REQUEST_TIMEOUT=60

# Monitoring
PROMETHEUS_ENABLED=true
PROMETHEUS_PORT=9090
METRICS_PREFIX=aurora_x

# Logging
LOG_FILE=/var/log/aurora-x/aurora.log
LOG_MAX_SIZE=100MB
LOG_BACKUP_COUNT=10

# Self-Learning
SELF_LEARNING_ENABLED=true
SELF_LEARNING_INTERVAL=3600
```

---

## SSL/TLS Configuration

### Using Let's Encrypt

```bash
# Install certbot
sudo apt-get install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d aurora.example.com

# Auto-renewal (cron)
sudo crontab -e
# Add:
0 0 * * * certbot renew --quiet
```

### Using Custom Certificate

```bash
# Generate CSR
openssl req -new -newkey rsa:4096 -nodes \
  -keyout aurora.key -out aurora.csr

# After receiving certificate from CA
sudo cp aurora.crt /etc/nginx/ssl/
sudo cp aurora.key /etc/nginx/ssl/
sudo chmod 600 /etc/nginx/ssl/aurora.key
```

---

## Monitoring & Logging

### Prometheus Configuration

```yaml
# monitoring/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'aurora-x'
    static_configs:
      - targets: ['localhost:5002']
    metrics_path: '/metrics'
```

### Grafana Dashboards

Import Aurora-X dashboard:
1. Open Grafana (http://localhost:3000)
2. Login (admin/admin)
3. Import dashboard
4. Use ID or upload JSON

### Logging Configuration

```python
# logging_config.py
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        },
        'json': {
            'class': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'format': '%(asctime)s %(name)s %(levelname)s %(message)s'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'default'
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/aurora-x/aurora.log',
            'maxBytes': 104857600,  # 100MB
            'backupCount': 10,
            'formatter': 'json'
        }
    },
    'root': {
        'level': 'INFO',
        'handlers': ['console', 'file']
    }
}
```

---

## Backup & Disaster Recovery

### Automated Backups

```bash
#!/bin/bash
# /opt/aurora-x/scripts/backup.sh

BACKUP_DIR="/backups/aurora-x"
DATE=$(date +%Y%m%d-%H%M%S)

# Backup PostgreSQL
pg_dump -U aurora aurora_db | gzip > "$BACKUP_DIR/postgres-$DATE.sql.gz"

# Backup Redis
redis-cli --rdb "$BACKUP_DIR/redis-$DATE.rdb"

# Backup application data
tar -czf "$BACKUP_DIR/data-$DATE.tar.gz" /opt/aurora-x/runs /opt/aurora-x/specs

# Keep last 7 days of backups
find "$BACKUP_DIR" -name "*.gz" -mtime +7 -delete
find "$BACKUP_DIR" -name "*.rdb" -mtime +7 -delete
```

Schedule with cron:
```bash
# Run daily at 2 AM
0 2 * * * /opt/aurora-x/scripts/backup.sh
```

### Disaster Recovery Plan

1. **Stop services:**
   ```bash
   docker-compose down
   ```

2. **Restore database:**
   ```bash
   gunzip < postgres-backup.sql.gz | psql -U aurora aurora_db
   ```

3. **Restore Redis:**
   ```bash
   cp redis-backup.rdb /var/lib/redis/dump.rdb
   sudo systemctl restart redis
   ```

4. **Restore data:**
   ```bash
   tar -xzf data-backup.tar.gz -C /opt/aurora-x/
   ```

5. **Restart services:**
   ```bash
   docker-compose up -d
   ```

---

## Scaling Strategy

### Vertical Scaling

Increase resources for existing instances:

```yaml
# docker-compose.yml
services:
  aurora-backend:
    deploy:
      resources:
        limits:
          cpus: '4'
          memory: 8G
        reservations:
          cpus: '2'
          memory: 4G
```

### Horizontal Scaling

Add more instances:

```bash
# Docker Compose
docker-compose up -d --scale aurora-backend=5

# Kubernetes
kubectl scale deployment/aurora-backend --replicas=10 -n aurora-x
```

### Database Scaling

```bash
# Read replicas
# Update connection string to use read replica for queries
READ_DATABASE_URL=postgresql://aurora:password@replica:5432/aurora_db

# Connection pooling
# Use PgBouncer
docker run -d --name pgbouncer \
  -e DATABASE_URL=$DATABASE_URL \
  -p 6432:6432 \
  brainsam/pgbouncer
```

### Redis Scaling

```bash
# Redis Cluster for horizontal scaling
redis-cli --cluster create \
  node1:7000 node2:7000 node3:7000 \
  node4:7000 node5:7000 node6:7000 \
  --cluster-replicas 1
```

---

## Production Checklist

### Pre-Deployment

- [ ] All tests passing
- [ ] Code reviewed and approved
- [ ] Security audit completed
- [ ] Performance testing done
- [ ] Backups configured
- [ ] Monitoring set up
- [ ] SSL certificates obtained
- [ ] Environment variables configured
- [ ] Database migrations ready
- [ ] Load balancer configured

### Deployment

- [ ] Deploy to staging first
- [ ] Run smoke tests
- [ ] Check health endpoints
- [ ] Verify monitoring
- [ ] Test key features
- [ ] Deploy to production
- [ ] Monitor logs for errors
- [ ] Check performance metrics

### Post-Deployment

- [ ] Verify all services running
- [ ] Test critical endpoints
- [ ] Check error rates
- [ ] Monitor resource usage
- [ ] Verify backups working
- [ ] Update documentation
- [ ] Notify team of deployment
- [ ] Schedule review meeting

### Security Checklist

- [ ] HTTPS enabled everywhere
- [ ] Strong passwords set
- [ ] Secrets not in code
- [ ] CORS configured properly
- [ ] Rate limiting enabled
- [ ] Input validation implemented
- [ ] SQL injection protection
- [ ] XSS protection enabled
- [ ] Security headers set
- [ ] Regular security updates

---

## Troubleshooting

### Service Won't Start

```bash
# Check logs
docker-compose logs aurora-backend

# Check port conflicts
sudo lsof -i :5002

# Verify environment variables
docker-compose config

# Test configuration
python -m aurora_x.serve --test-config
```

### High Memory Usage

```bash
# Check memory usage
docker stats

# Reduce cache size
# Edit .env:
MAX_CACHE_SIZE=5000

# Restart services
docker-compose restart
```

### Database Connection Issues

```bash
# Test connection
psql -U aurora -h localhost -d aurora_db

# Check PostgreSQL logs
sudo tail -f /var/log/postgresql/postgresql-14-main.log

# Verify credentials
echo $DATABASE_URL
```

### Redis Connection Issues

```bash
# Test Redis
redis-cli ping

# Check Redis logs
sudo journalctl -u redis -f

# Verify Redis running
sudo systemctl status redis
```

### Slow Performance

```bash
# Check slow requests
curl http://localhost:5002/api/performance/slow-requests

# Check cache hit rate
curl http://localhost:5002/api/performance/cache/stats

# Enable query logging
# In PostgreSQL:
ALTER DATABASE aurora_db SET log_min_duration_statement = 1000;
```

---

## Support & Resources

- **Documentation:** `/docs`
- **API Reference:** [API_REFERENCE.md](API_REFERENCE.md)
- **User Guide:** [USER_GUIDE.md](USER_GUIDE.md)
- **Developer Guide:** [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md)
- **GitHub:** https://github.com/chango112595-cell/Aurora-x
- **Issues:** https://github.com/chango112595-cell/Aurora-x/issues

---

**Production deployment complete!** 🚀

*Last Updated: November 10, 2025*
