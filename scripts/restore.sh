#!/bin/bash
#
# Aurora-X Restore Script
# Restore database and configuration from backups
#
# Usage: ./restore.sh [--database BACKUP_FILE] [--config BACKUP_FILE] [--latest]
#

set -euo pipefail

# ══════════════════════════════════════════════════════════════
# 🔧 CONFIGURATION
# ══════════════════════════════════════════════════════════════

BACKUP_DIR="${BACKUP_DIR:-/workspaces/Aurora-x/backups}"
DB_BACKUP_DIR="${BACKUP_DIR}/database"
CONFIG_BACKUP_DIR="${BACKUP_DIR}/config"
LOG_DIR="${LOG_DIR:-/workspaces/Aurora-x/logs}"
LOG_FILE="${LOG_DIR}/restore-$(date +%Y%m%d_%H%M%S).log"

# Database configuration
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
DB_NAME="${DB_NAME:-aurora}"
DB_USER="${DB_USER:-postgres}"
DB_PASSWORD="${DB_PASSWORD:-postgres}"

# ══════════════════════════════════════════════════════════════
# 📝 LOGGING
# ══════════════════════════════════════════════════════════════

log() {
    local level="$1"
    shift
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [${level}] $*" | tee -a "${LOG_FILE}"
}

# ══════════════════════════════════════════════════════════════
# 🔍 LIST AVAILABLE BACKUPS
# ══════════════════════════════════════════════════════════════

list_database_backups() {
    log "INFO" "Available database backups:"
    if [ -d "${DB_BACKUP_DIR}" ]; then
        find "${DB_BACKUP_DIR}" -name "aurora_db_*.sql.gz" -type f -printf "%T@ %p\n" | sort -rn | awk '{print $2}' | nl
    else
        log "WARN" "No database backups found"
    fi
}

list_config_backups() {
    log "INFO" "Available configuration backups:"
    if [ -d "${CONFIG_BACKUP_DIR}" ]; then
        find "${CONFIG_BACKUP_DIR}" -name "aurora_config_*.tar.gz" -type f -printf "%T@ %p\n" | sort -rn | awk '{print $2}' | nl
    else
        log "WARN" "No configuration backups found"
    fi
}

# ══════════════════════════════════════════════════════════════
# 💾 RESTORE DATABASE
# ══════════════════════════════════════════════════════════════

restore_database() {
    local backup_file="$1"
    
    log "INFO" "╔════════════════════════════════════════════════════╗"
    log "INFO" "║          DATABASE RESTORE                          ║"
    log "INFO" "╚════════════════════════════════════════════════════╝"
    
    if [ ! -f "${backup_file}" ]; then
        log "ERROR" "Backup file not found: ${backup_file}"
        exit 1
    fi
    
    log "INFO" "Restoring from: ${backup_file}"
    log "INFO" "Database: ${DB_NAME}@${DB_HOST}:${DB_PORT}"
    
    # Verify checksum if available
    if [ -f "${backup_file}.sha256" ]; then
        log "INFO" "Verifying backup integrity..."
        local expected_checksum=$(cat "${backup_file}.sha256")
        local actual_checksum=$(sha256sum "${backup_file}" | cut -d' ' -f1)
        
        if [ "${expected_checksum}" != "${actual_checksum}" ]; then
            log "ERROR" "Checksum mismatch! Backup may be corrupted."
            log "ERROR" "Expected: ${expected_checksum}"
            log "ERROR" "Actual: ${actual_checksum}"
            exit 1
        fi
        log "SUCCESS" "Checksum verified"
    fi
    
    # Verify gzip integrity
    if ! gzip -t "${backup_file}" 2>> "${LOG_FILE}"; then
        log "ERROR" "Backup file is corrupted"
        exit 1
    fi
    
    # Confirm restore (if interactive)
    if [ -t 0 ]; then
        log "WARN" "⚠️  This will DROP and recreate the database: ${DB_NAME}"
        read -p "Are you sure you want to continue? (yes/no): " confirm
        if [ "${confirm}" != "yes" ]; then
            log "INFO" "Restore cancelled by user"
            exit 0
        fi
    fi
    
    export PGPASSWORD="${DB_PASSWORD}"
    
    # Drop existing database (if exists)
    log "INFO" "Dropping existing database (if exists)..."
    psql -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" -c "DROP DATABASE IF EXISTS ${DB_NAME};" 2>> "${LOG_FILE}" || true
    
    # Create new database
    log "INFO" "Creating new database..."
    psql -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" -c "CREATE DATABASE ${DB_NAME};" 2>> "${LOG_FILE}"
    
    # Restore from backup
    log "INFO" "Restoring database..."
    gunzip -c "${backup_file}" | psql -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" -d "${DB_NAME}" 2>> "${LOG_FILE}"
    
    unset PGPASSWORD
    
    log "SUCCESS" "Database restored successfully!"
}

# ══════════════════════════════════════════════════════════════
# ⚙️ RESTORE CONFIGURATION
# ══════════════════════════════════════════════════════════════

restore_config() {
    local backup_file="$1"
    
    log "INFO" "╔════════════════════════════════════════════════════╗"
    log "INFO" "║       CONFIGURATION RESTORE                        ║"
    log "INFO" "╚════════════════════════════════════════════════════╝"
    
    if [ ! -f "${backup_file}" ]; then
        log "ERROR" "Backup file not found: ${backup_file}"
        exit 1
    fi
    
    log "INFO" "Restoring from: ${backup_file}"
    
    # Verify checksum
    if [ -f "${backup_file}.sha256" ]; then
        log "INFO" "Verifying backup integrity..."
        local expected_checksum=$(cat "${backup_file}.sha256")
        local actual_checksum=$(sha256sum "${backup_file}" | cut -d' ' -f1)
        
        if [ "${expected_checksum}" != "${actual_checksum}" ]; then
            log "ERROR" "Checksum mismatch! Backup may be corrupted."
            exit 1
        fi
        log "SUCCESS" "Checksum verified"
    fi
    
    # Create temporary directory
    local temp_dir=$(mktemp -d)
    
    # Extract backup
    log "INFO" "Extracting configuration files..."
    tar -xzf "${backup_file}" -C "${temp_dir}"
    
    # Restore files to workspace
    log "INFO" "Restoring configuration files to workspace..."
    if [ -d "${temp_dir}/aurora-config" ]; then
        cp -rv "${temp_dir}/aurora-config/"* /workspaces/Aurora-x/ 2>&1 | tee -a "${LOG_FILE}"
    fi
    
    # Cleanup
    rm -rf "${temp_dir}"
    
    log "SUCCESS" "Configuration restored successfully!"
    log "WARN" "⚠️  Please review restored files and restart services if needed"
}

# ══════════════════════════════════════════════════════════════
# 🚀 MAIN
# ══════════════════════════════════════════════════════════════

main() {
    mkdir -p "${LOG_DIR}"
    
    log "INFO" "╔════════════════════════════════════════════════════╗"
    log "INFO" "║         Aurora-X Restore Script                    ║"
    log "INFO" "╚════════════════════════════════════════════════════╝"
    
    local restore_db=false
    local restore_cfg=false
    local db_backup=""
    local cfg_backup=""
    local use_latest=false
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --database)
                restore_db=true
                db_backup="$2"
                shift 2
                ;;
            --config)
                restore_cfg=true
                cfg_backup="$2"
                shift 2
                ;;
            --latest)
                use_latest=true
                shift
                ;;
            --list)
                list_database_backups
                echo ""
                list_config_backups
                exit 0
                ;;
            --help)
                echo "Usage: $0 [OPTIONS]"
                echo ""
                echo "Options:"
                echo "  --database FILE     Restore database from specified backup"
                echo "  --config FILE       Restore configuration from specified backup"
                echo "  --latest            Use latest backups"
                echo "  --list              List available backups"
                echo "  --help              Show this help message"
                exit 0
                ;;
            *)
                log "ERROR" "Unknown option: $1"
                exit 1
                ;;
        esac
    done
    
    # If --latest flag, find most recent backups
    if [ "${use_latest}" = true ]; then
        if [ "${restore_db}" = false ] && [ "${restore_cfg}" = false ]; then
            restore_db=true
            restore_cfg=true
        fi
        
        if [ "${restore_db}" = true ]; then
            db_backup=$(find "${DB_BACKUP_DIR}" -name "aurora_db_*.sql.gz" -type f -printf "%T@ %p\n" 2>/dev/null | sort -rn | head -1 | awk '{print $2}')
        fi
        
        if [ "${restore_cfg}" = true ]; then
            cfg_backup=$(find "${CONFIG_BACKUP_DIR}" -name "aurora_config_*.tar.gz" -type f -printf "%T@ %p\n" 2>/dev/null | sort -rn | head -1 | awk '{print $2}')
        fi
    fi
    
    # Perform restores
    if [ "${restore_db}" = true ]; then
        if [ -z "${db_backup}" ]; then
            log "ERROR" "No database backup specified"
            exit 1
        fi
        restore_database "${db_backup}"
    fi
    
    if [ "${restore_cfg}" = true ]; then
        if [ -z "${cfg_backup}" ]; then
            log "ERROR" "No configuration backup specified"
            exit 1
        fi
        restore_config "${cfg_backup}"
    fi
    
    if [ "${restore_db}" = false ] && [ "${restore_cfg}" = false ]; then
        log "INFO" "No restore operation specified. Use --database or --config"
        log "INFO" "Run with --help for usage information"
        log "INFO" "Run with --list to see available backups"
        exit 0
    fi
    
    log "SUCCESS" "Restore completed successfully!"
}

trap 'log "ERROR" "Restore failed on line $LINENO"; exit 1' ERR

main "$@"
