#!/bin/bash
#
# Aurora-X Master Backup Script
# Orchestrates all backup operations
#
# Usage: ./backup-all.sh [--no-db] [--no-config]
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="${LOG_DIR:-/workspaces/Aurora-x/logs}"
LOG_FILE="${LOG_DIR}/backup-all-$(date +%Y%m%d_%H%M%S).log"

mkdir -p "${LOG_DIR}"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "${LOG_FILE}"
}

log "╔════════════════════════════════════════════════════╗"
log "║       Aurora-X Master Backup Orchestrator         ║"
log "╚════════════════════════════════════════════════════╝"

# Parse arguments
BACKUP_DB=true
BACKUP_CONFIG=true

while [[ $# -gt 0 ]]; do
    case $1 in
        --no-db)
            BACKUP_DB=false
            shift
            ;;
        --no-config)
            BACKUP_CONFIG=false
            shift
            ;;
        *)
            log "ERROR: Unknown option: $1"
            exit 1
            ;;
    esac
done

# Run database backup
if [ "${BACKUP_DB}" = true ]; then
    log "Starting database backup..."
    if "${SCRIPT_DIR}/backup-database.sh"; then
        log "✅ Database backup completed"
    else
        log "❌ Database backup failed"
        exit 1
    fi
fi

# Run configuration backup
if [ "${BACKUP_CONFIG}" = true ]; then
    log "Starting configuration backup..."
    if "${SCRIPT_DIR}/backup-config.sh"; then
        log "✅ Configuration backup completed"
    else
        log "❌ Configuration backup failed"
        exit 1
    fi
fi

log "╔════════════════════════════════════════════════════╗"
log "║          All Backups Completed Successfully       ║"
log "╚════════════════════════════════════════════════════╝"
