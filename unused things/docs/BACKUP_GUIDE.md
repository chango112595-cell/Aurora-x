# Aurora-X Backup & Recovery Guide

Complete guide for backup operations, restoration procedures, and disaster recovery.

## 📋 Table of Contents

- [Overview](#overview)
- [Backup System](#backup-system)
- [Backup Scripts](#backup-scripts)
- [Restoration](#restoration)
- [Automated Scheduling](#automated-scheduling)
- [Monitoring](#monitoring)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

### Backup Strategy

Aurora-X implements a **3-2-1 backup strategy**:
- **3** copies of data (production + 2 backups)
- **2** different storage types (local + cloud/remote)
- **1** off-site backup

### What Gets Backed Up

1. **Database** - PostgreSQL data (users, corpus, analytics)
2. **Configuration** - Environment files, Docker configs, app configs
3. **Logs** - Application logs and audit trails (optional)
4. **Docker Volumes** - Persistent data volumes

### Backup Schedule

| Type | Frequency | Retention | Script |
|------|-----------|-----------|--------|
| Database (Full) | Daily at 2 AM | 30 days | `backup-database.sh` |
| Configuration | Daily at 2:30 AM | 30 days | `backup-config.sh` |
| Database (Incremental) | Hourly (9 AM-5 PM) | 7 days | `backup-database.sh` |
| Full System | Weekly (Sunday 3 AM) | 60 days | `backup-all.sh` |

### Recovery Objectives

- **RPO** (Recovery Point Objective): 1 hour - Maximum acceptable data loss
- **RTO** (Recovery Time Objective): 30 minutes - Maximum acceptable downtime

---

## 💾 Backup System

### Directory Structure

```
/workspaces/Aurora-x/
├── backups/
│   ├── database/
│   │   ├── aurora_db_20251110_020000.sql.gz
│   │   ├── aurora_db_20251110_020000.sql.gz.sha256
│   │   └── ...
│   └── config/
│       ├── aurora_config_20251110_023000.tar.gz
│       ├── aurora_config_20251110_023000.tar.gz.sha256
│       └── ...
├── scripts/
│   ├── backup-database.sh
│   ├── backup-config.sh
│   ├── backup-all.sh
│   ├── restore.sh
│   └── backup-cron.txt
└── logs/
    ├── backup-20251110.log
    ├── restore-20251110_153000.log
    └── cron-backup.log
```

### Backup Features

- ✅ **Compression** - gzip compression (70-90% size reduction)
- ✅ **Checksums** - SHA-256 integrity verification
- ✅ **Rotation** - Automatic cleanup of old backups
- ✅ **Logging** - Detailed operation logs
- ✅ **Verification** - Automatic integrity checks
- ✅ **Notifications** - Webhook alerts (optional)
- ✅ **Atomic Operations** - All-or-nothing backups

---

## 🔧 Backup Scripts

### 1. Database Backup (`backup-database.sh`)

Backs up PostgreSQL database with compression and verification.

**Usage:**
```bash
# Basic backup
./scripts/backup-database.sh

# Custom retention (14 days)
./scripts/backup-database.sh --retention 14

# Help
./scripts/backup-database.sh --help
```

**What it does:**
1. Pre-flight checks (disk space, pg_dump availability)
2. Performs `pg_dump` with optimal settings
3. Compresses with gzip
4. Generates SHA-256 checksum
5. Verifies backup integrity
6. Rotates old backups
7. Logs all operations

**Environment Variables:**
```bash
DB_HOST=localhost
DB_PORT=5432
DB_NAME=aurora
DB_USER=postgres
DB_PASSWORD=postgres
BACKUP_DIR=/workspaces/Aurora-x/backups/database
BACKUP_RETENTION_DAYS=30
BACKUP_WEBHOOK_URL=https://hooks.slack.com/...  # Optional
```

**Output:**
```
/workspaces/Aurora-x/backups/database/
├── aurora_db_20251110_020000.sql.gz       # Compressed backup
└── aurora_db_20251110_020000.sql.gz.sha256  # Checksum
```

---

### 2. Configuration Backup (`backup-config.sh`)

Backs up all configuration files and Docker configs.

**Usage:**
```bash
# Backup configurations
./scripts/backup-config.sh
```

**What it backs up:**
- `.env`, `.env.production`, `.env.local`
- `docker-compose.yml`, all Dockerfiles
- `package.json`, `requirements.txt`
- `aurora_server_config.json`, `logging.conf`
- `pytest.ini`, `jest.config.js`, `tsconfig.json`
- `.github/workflows/` (CI/CD configs)

**Output:**
```
/workspaces/Aurora-x/backups/config/
├── aurora_config_20251110_023000.tar.gz       # Compressed archive
└── aurora_config_20251110_023000.tar.gz.sha256  # Checksum
```

---

### 3. Master Backup (`backup-all.sh`)

Orchestrates all backup operations.

**Usage:**
```bash
# Full backup (database + config)
./scripts/backup-all.sh

# Database only
./scripts/backup-all.sh --no-config

# Config only
./scripts/backup-all.sh --no-db
```

**Use Cases:**
- Scheduled weekly full backups
- Pre-deployment backups
- Manual full system snapshots

---

### 4. Restore Script (`restore.sh`)

Restores from backups with integrity verification.

**Usage:**
```bash
# List available backups
./scripts/restore.sh --list

# Restore latest database
./scripts/restore.sh --database --latest

# Restore latest config
./scripts/restore.sh --config --latest

# Restore both (latest)
./scripts/restore.sh --database --config --latest

# Restore specific backup
./scripts/restore.sh --database /path/to/backup.sql.gz

# Help
./scripts/restore.sh --help
```

**What it does:**
1. Verifies backup integrity (checksum + gzip test)
2. Confirms restore operation (if interactive)
3. Performs restoration
4. Verifies successful restoration
5. Logs all operations

**⚠️ WARNING**: Restore operations will **overwrite existing data**!

---

## 🔄 Restoration

### Database Restoration

**Quick Restore (Latest):**
```bash
./scripts/restore.sh --database --latest
```

**Specific Backup:**
```bash
# List backups with dates
./scripts/restore.sh --list

# Restore specific one
./scripts/restore.sh --database /workspaces/Aurora-x/backups/database/aurora_db_20251110_020000.sql.gz
```

**Manual Restore:**
```bash
# Stop services
docker-compose stop backend bridge self-learn chat

# Restore database
export PGPASSWORD=postgres
gunzip -c backup.sql.gz | psql -h localhost -U postgres -d aurora

# Restart services
docker-compose up -d
```

### Configuration Restoration

**Quick Restore:**
```bash
./scripts/restore.sh --config --latest
```

**After restoration:**
1. Review restored files (especially `.env`)
2. Verify secrets and tokens
3. Rebuild Docker images if needed
4. Restart all services

### Full System Restoration

**Complete recovery:**
```bash
# 1. Restore everything
./scripts/restore.sh --database --config --latest

# 2. Install dependencies
npm install
pip install -r requirements.txt

# 3. Rebuild services
docker-compose build

# 4. Start services
docker-compose up -d

# 5. Verify health
curl http://localhost:5000/api/health
```

---

## ⏰ Automated Scheduling

### Using Cron (Linux/Mac)

**Install schedule:**
```bash
# Edit crontab
crontab -e

# Add lines from backup-cron.txt
# Daily database backup at 2 AM
0 2 * * * cd /workspaces/Aurora-x && ./scripts/backup-database.sh >> logs/cron-backup.log 2>&1

# Daily config backup at 2:30 AM
30 2 * * * cd /workspaces/Aurora-x && ./scripts/backup-config.sh >> logs/cron-backup.log 2>&1

# Weekly full backup on Sundays at 3 AM
0 3 * * 0 cd /workspaces/Aurora-x && ./scripts/backup-all.sh >> logs/cron-backup.log 2>&1

# Save and exit
```

**Verify schedule:**
```bash
crontab -l
```

**Check cron logs:**
```bash
tail -f /workspaces/Aurora-x/logs/cron-backup.log
```

### Using Systemd Timers

**Create service** (`/etc/systemd/system/aurora-backup.service`):
```ini
[Unit]
Description=Aurora-X Database Backup
After=network.target

[Service]
Type=oneshot
User=your-user
WorkingDirectory=/workspaces/Aurora-x
ExecStart=/workspaces/Aurora-x/scripts/backup-database.sh
StandardOutput=append:/workspaces/Aurora-x/logs/systemd-backup.log
StandardError=append:/workspaces/Aurora-x/logs/systemd-backup.log
```

**Create timer** (`/etc/systemd/system/aurora-backup.timer`):
```ini
[Unit]
Description=Aurora-X Backup Timer
Requires=aurora-backup.service

[Timer]
OnCalendar=daily
OnCalendar=02:00
Persistent=true

[Install]
WantedBy=timers.target
```

**Enable and start:**
```bash
sudo systemctl enable aurora-backup.timer
sudo systemctl start aurora-backup.timer
sudo systemctl status aurora-backup.timer
```

### Docker-based Scheduling

**Using `ofelia` scheduler:**
```yaml
# In docker-compose.yml
services:
  scheduler:
    image: mcuadros/ofelia:latest
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - ./scripts:/scripts
    command: daemon --docker
    labels:
      ofelia.job-exec.database-backup.schedule: "0 2 * * *"
      ofelia.job-exec.database-backup.command: "/scripts/backup-database.sh"
```

---

## 📊 Monitoring

### Backup Health Checks

**Daily verification:**
```bash
# Check recent backups exist
ls -lh backups/database/ | head -5
ls -lh backups/config/ | head -5

# Verify backup sizes (should be > 0)
du -sh backups/*

# Check checksums
cd backups/database
for f in *.sha256; do
    sha256sum -c "$f" && echo "✅ $f OK" || echo "❌ $f FAILED"
done
```

### Backup Metrics

**Monitor these metrics:**
- Backup completion rate (should be 100%)
- Backup file sizes (watch for anomalies)
- Backup duration (should be consistent)
- Disk space usage (backups directory)
- Failed backup count (should be 0)

### Alerts

**Set up alerts for:**
- ❌ Backup failures
- ⚠️ Disk space < 10% free
- ⚠️ Backup size anomaly (>50% change)
- ⚠️ Backup not run for 24 hours
- ❌ Checksum verification failures

**Example webhook notification:**
```bash
# In backup scripts
send_notification() {
    curl -X POST "${BACKUP_WEBHOOK_URL}" \
        -H "Content-Type: application/json" \
        -d "{
            \"status\": \"$1\",
            \"message\": \"$2\",
            \"timestamp\": \"$(date -Iseconds)\"
        }"
}
```

---

## ✅ Best Practices

### Security

1. **Encrypt backups** (especially off-site)
   ```bash
   # Encrypt backup
   gpg --encrypt --recipient admin@aurora.local backup.sql.gz
   
   # Decrypt backup
   gpg --decrypt backup.sql.gz.gpg > backup.sql.gz
   ```

2. **Secure credentials**
   - Store DB passwords in environment variables
   - Use `.pgpass` file for passwordless access
   - Restrict backup file permissions (600)

3. **Access control**
   ```bash
   # Set proper permissions
   chmod 700 backups/
   chmod 600 backups/**/*.sql.gz
   chmod 755 scripts/backup-*.sh
   ```

### Off-site Backups

**Sync to S3:**
```bash
# Install AWS CLI
pip install awscli

# Sync backups to S3
aws s3 sync /workspaces/Aurora-x/backups/ s3://aurora-backups/ \
    --exclude "*" \
    --include "*.gz" \
    --include "*.sha256"
```

**Sync to remote server:**
```bash
# Using rsync
rsync -avz --delete \
    /workspaces/Aurora-x/backups/ \
    user@backup-server:/backups/aurora/
```

### Testing

**Monthly restore test:**
```bash
# 1. Create test environment
docker-compose -f docker-compose.test.yml up -d

# 2. Restore from backup
./scripts/restore.sh --database --latest

# 3. Run tests
npm test
pytest

# 4. Cleanup
docker-compose -f docker-compose.test.yml down
```

**Document tests:**
```markdown
## Restore Test - 2025-11-10

- Backup used: aurora_db_20251110_020000.sql.gz
- Restore time: 3 minutes 42 seconds
- Data integrity: ✅ PASS
- Application tests: ✅ PASS (127/127)
- Issues: None
```

### Documentation

Keep updated:
- Backup schedule
- Retention policies
- Recovery procedures
- Contact information
- Incident logs

---

## 🔧 Troubleshooting

### Backup Fails

**"Insufficient disk space":**
```bash
# Check available space
df -h /workspaces/Aurora-x/backups

# Clean old backups
find backups/ -mtime +60 -delete

# Or increase retention
export BACKUP_RETENTION_DAYS=14
```

**"pg_dump not found":**
```bash
# Install PostgreSQL client
sudo apt-get install postgresql-client

# Or use Docker
docker exec aurora-db pg_dump -U postgres aurora | gzip > backup.sql.gz
```

**"Permission denied":**
```bash
# Fix script permissions
chmod +x scripts/backup-*.sh

# Fix backup directory permissions
chmod 700 backups/
```

### Restore Fails

**"Checksum mismatch":**
```bash
# Backup may be corrupted, use previous backup
./scripts/restore.sh --list

# Or skip checksum (not recommended)
gunzip -c backup.sql.gz | psql -h localhost -U postgres -d aurora
```

**"Database already exists":**
```bash
# Drop database first
psql -h localhost -U postgres -c "DROP DATABASE IF EXISTS aurora;"

# Then restore
./scripts/restore.sh --database backup.sql.gz
```

### Log Analysis

**Check backup logs:**
```bash
# Today's logs
tail -100 logs/backup-$(date +%Y%m%d).log

# Search for errors
grep ERROR logs/backup-*.log

# Watch live
tail -f logs/backup-*.log
```

**Common log patterns:**
```
✅ SUCCESS - Backup completed
❌ ERROR - Backup failed
⚠️  WARN - Warning condition
ℹ️  INFO - Informational message
```

---

## 📚 Related Documentation

- [Disaster Recovery Plan](DISASTER_RECOVERY.md)
- [Docker Deployment](DOCKER_DEPLOYMENT.md)
- [System Architecture](../AURORA_ARCHITECTURE_DECISION.md)

---

## 🔄 Maintenance Schedule

| Task | Frequency | Owner |
|------|-----------|-------|
| Verify backups | Daily | Automated |
| Test restore | Weekly | DevOps |
| Review logs | Weekly | DevOps |
| Full recovery test | Monthly | Team |
| Update documentation | Quarterly | Team |
| Review retention policy | Annually | Management |

---

**Created by**: Aurora AI Assistant  
**Date**: November 10, 2025  
**Version**: 1.0.0  
**Status**: ✅ Production Ready
