#!/bin/bash
#
# Aurora-X Configuration Backup Script
# Backup environment files, configs, and critical system files
#
# Usage: ./backup-config.sh
#

set -euo pipefail

# ══════════════════════════════════════════════════════════════
# 🔧 CONFIGURATION
# ══════════════════════════════════════════════════════════════

BACKUP_DIR="${BACKUP_DIR:-/workspaces/Aurora-x/backups/config}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="aurora_config_${TIMESTAMP}.tar.gz"
BACKUP_PATH="${BACKUP_DIR}/${BACKUP_FILE}"
LOG_DIR="${LOG_DIR:-/workspaces/Aurora-x/logs}"
LOG_FILE="${LOG_DIR}/backup-config-$(date +%Y%m%d).log"
RETENTION_DAYS="${BACKUP_RETENTION_DAYS:-30}"

# ══════════════════════════════════════════════════════════════
# 📝 LOGGING
# ══════════════════════════════════════════════════════════════

log() {
    local level="$1"
    shift
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [${level}] $*" | tee -a "${LOG_FILE}"
}

# ══════════════════════════════════════════════════════════════
# 💾 BACKUP CONFIGURATION
# ══════════════════════════════════════════════════════════════

backup_config() {
    log "INFO" "Starting configuration backup..."
    
    mkdir -p "${BACKUP_DIR}"
    mkdir -p "${LOG_DIR}"
    
    # Create temporary directory for staging
    local temp_dir=$(mktemp -d)
    local backup_staging="${temp_dir}/aurora-config"
    mkdir -p "${backup_staging}"
    
    log "INFO" "Staging files in: ${backup_staging}"
    
    # Backup environment files (if they exist)
    [ -f .env ] && cp .env "${backup_staging}/" && log "INFO" "Backed up: .env"
    [ -f .env.production ] && cp .env.production "${backup_staging}/" && log "INFO" "Backed up: .env.production"
    [ -f .env.local ] && cp .env.local "${backup_staging}/" && log "INFO" "Backed up: .env.local"
    
    # Backup Docker configuration
    [ -f docker-compose.yml ] && cp docker-compose.yml "${backup_staging}/" && log "INFO" "Backed up: docker-compose.yml"
    [ -f Dockerfile.backend ] && cp Dockerfile.backend "${backup_staging}/" && log "INFO" "Backed up: Dockerfile.backend"
    [ -f Dockerfile.frontend ] && cp Dockerfile.frontend "${backup_staging}/" && log "INFO" "Backed up: Dockerfile.frontend"
    
    # Backup Python service Dockerfiles
    [ -f aurora_x/bridge/Dockerfile ] && mkdir -p "${backup_staging}/aurora_x/bridge" && cp aurora_x/bridge/Dockerfile "${backup_staging}/aurora_x/bridge/" && log "INFO" "Backed up: bridge/Dockerfile"
    [ -f Dockerfile.self-learn ] && cp Dockerfile.self-learn "${backup_staging}/" && log "INFO" "Backed up: Dockerfile.self-learn"
    [ -f Dockerfile.chat ] && cp Dockerfile.chat "${backup_staging}/" && log "INFO" "Backed up: Dockerfile.chat"
    
    # Backup package configuration
    [ -f package.json ] && cp package.json "${backup_staging}/" && log "INFO" "Backed up: package.json"
    [ -f package-lock.json ] && cp package-lock.json "${backup_staging}/" && log "INFO" "Backed up: package-lock.json"
    [ -f requirements.txt ] && cp requirements.txt "${backup_staging}/" && log "INFO" "Backed up: requirements.txt"
    [ -f requirements-security.txt ] && cp requirements-security.txt "${backup_staging}/" && log "INFO" "Backed up: requirements-security.txt"
    
    # Backup Aurora configuration files
    [ -f aurora_server_config.json ] && cp aurora_server_config.json "${backup_staging}/" && log "INFO" "Backed up: aurora_server_config.json"
    [ -f aurora_supervisor_config.json ] && cp aurora_supervisor_config.json "${backup_staging}/" && log "INFO" "Backed up: aurora_supervisor_config.json"
    
    # Backup logging configuration
    [ -f logging.conf ] && cp logging.conf "${backup_staging}/" && log "INFO" "Backed up: logging.conf"
    
    # Backup test configuration
    [ -f pytest.ini ] && cp pytest.ini "${backup_staging}/" && log "INFO" "Backed up: pytest.ini"
    [ -f jest.config.js ] && cp jest.config.js "${backup_staging}/" && log "INFO" "Backed up: jest.config.js"
    
    # Backup TypeScript configuration
    [ -f tsconfig.json ] && cp tsconfig.json "${backup_staging}/" && log "INFO" "Backed up: tsconfig.json"
    
    # Backup Vite configuration
    [ -f vite.config.ts ] && cp vite.config.ts "${backup_staging}/" && log "INFO" "Backed up: vite.config.ts"
    
    # Backup nginx configuration (if exists)
    [ -f nginx.conf ] && cp nginx.conf "${backup_staging}/" && log "INFO" "Backed up: nginx.conf"
    
    # Backup GitHub workflows
    if [ -d .github/workflows ]; then
        mkdir -p "${backup_staging}/.github"
        cp -r .github/workflows "${backup_staging}/.github/" && log "INFO" "Backed up: .github/workflows/"
    fi
    
    # Create tarball
    log "INFO" "Creating compressed archive..."
    tar -czf "${BACKUP_PATH}" -C "${temp_dir}" aurora-config
    
    # Cleanup
    rm -rf "${temp_dir}"
    
    # Generate checksum
    sha256sum "${BACKUP_PATH}" | cut -d' ' -f1 > "${BACKUP_PATH}.sha256"
    
    log "SUCCESS" "Configuration backup completed: ${BACKUP_FILE}"
    log "INFO" "Backup size: $(du -h "${BACKUP_PATH}" | cut -f1)"
}

# ══════════════════════════════════════════════════════════════
# 🗑️ ROTATION
# ══════════════════════════════════════════════════════════════

rotate_backups() {
    log "INFO" "Rotating old backups (retention: ${RETENTION_DAYS} days)..."
    
    find "${BACKUP_DIR}" -name "aurora_config_*.tar.gz" -type f -mtime +${RETENTION_DAYS} -delete
    
    local count=$(find "${BACKUP_DIR}" -name "aurora_config_*.tar.gz" -type f | wc -l)
    log "INFO" "Current backup count: ${count}"
}

# ══════════════════════════════════════════════════════════════
# 🚀 MAIN
# ══════════════════════════════════════════════════════════════

main() {
    log "INFO" "╔════════════════════════════════════════════════════╗"
    log "INFO" "║   Aurora-X Configuration Backup Script            ║"
    log "INFO" "╚════════════════════════════════════════════════════╝"
    
    backup_config
    rotate_backups
    
    log "SUCCESS" "Backup process completed!"
}

trap 'log "ERROR" "Backup failed on line $LINENO"; exit 1' ERR

main "$@"
