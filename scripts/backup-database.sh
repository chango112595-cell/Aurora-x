#!/bin/bash
#
# Aurora-X Database Backup Script
# Automated PostgreSQL database backup with compression and rotation
#
# Usage: ./backup-database.sh [--full] [--retention DAYS]
#

set -euo pipefail

# ══════════════════════════════════════════════════════════════
# 🔧 CONFIGURATION
# ══════════════════════════════════════════════════════════════

# Backup directory
BACKUP_DIR="${BACKUP_DIR:-/workspaces/Aurora-x/backups/database}"
BACKUP_RETENTION_DAYS="${BACKUP_RETENTION_DAYS:-30}"

# Database configuration (from environment or docker-compose)
DB_HOST="${DB_HOST:-127.0.0.1}"
DB_PORT="${DB_PORT:-5432}"
DB_NAME="${DB_NAME:-aurora}"
DB_USER="${DB_USER:-postgres}"
DB_PASSWORD="${DB_PASSWORD:-postgres}"

# Backup settings
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="aurora_db_${TIMESTAMP}.sql"
BACKUP_COMPRESSED="${BACKUP_FILE}.gz"
BACKUP_PATH="${BACKUP_DIR}/${BACKUP_COMPRESSED}"

# Logging
LOG_DIR="${LOG_DIR:-/workspaces/Aurora-x/logs}"
LOG_FILE="${LOG_DIR}/backup-$(date +%Y%m%d).log"

# ══════════════════════════════════════════════════════════════
# 📝 LOGGING FUNCTIONS
# ══════════════════════════════════════════════════════════════

log() {
    local level="$1"
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[${timestamp}] [${level}] ${message}" | tee -a "${LOG_FILE}"
}

log_info() {
    log "INFO" "$@"
}

log_error() {
    log "ERROR" "$@"
}

log_success() {
    log "SUCCESS" "$@"
}

# ══════════════════════════════════════════════════════════════
# 🔍 PRE-FLIGHT CHECKS
# ══════════════════════════════════════════════════════════════

preflight_checks() {
    log_info "Starting pre-flight checks..."

    # Create backup directory if it doesn't exist
    if [ ! -d "${BACKUP_DIR}" ]; then
        log_info "Creating backup directory: ${BACKUP_DIR}"
        mkdir -p "${BACKUP_DIR}"
    fi

    # Create log directory if it doesn't exist
    if [ ! -d "${LOG_DIR}" ]; then
        mkdir -p "${LOG_DIR}"
    fi

    # Check if pg_dump is available
    if ! command -v pg_dump &> /dev/null; then
        log_error "pg_dump not found. Please install PostgreSQL client tools."
        exit 1
    fi

    # Check disk space (require at least 1GB free)
    local available_space=$(df "${BACKUP_DIR}" | tail -1 | awk '{print $4}')
    if [ "${available_space}" -lt 1048576 ]; then
        log_error "Insufficient disk space. At least 1GB required."
        exit 1
    fi

    log_success "Pre-flight checks completed"
}

# ══════════════════════════════════════════════════════════════
# 💾 DATABASE BACKUP
# ══════════════════════════════════════════════════════════════

backup_database() {
    log_info "Starting database backup..."
    log_info "Database: ${DB_NAME}@${DB_HOST}:${DB_PORT}"
    log_info "Backup file: ${BACKUP_PATH}"

    # Set password for pg_dump
    export PGPASSWORD="${DB_PASSWORD}"

    # Perform database dump
    log_info "Running pg_dump..."
    if pg_dump -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" -d "${DB_NAME}" \
        --format=plain \
        --no-owner \
        --no-acl \
        --verbose \
        2>> "${LOG_FILE}" | gzip > "${BACKUP_PATH}"; then

        log_success "Database backup completed"
    else
        log_error "Database backup failed"
        exit 1
    fi

    # Unset password
    unset PGPASSWORD

    # Get backup file size
    local backup_size=$(du -h "${BACKUP_PATH}" | cut -f1)
    log_info "Backup size: ${backup_size}"
}

# ══════════════════════════════════════════════════════════════
# ✅ BACKUP VERIFICATION
# ══════════════════════════════════════════════════════════════

verify_backup() {
    log_info "Verifying backup integrity..."

    # Check if file exists and is not empty
    if [ ! -f "${BACKUP_PATH}" ]; then
        log_error "Backup file not found: ${BACKUP_PATH}"
        exit 1
    fi

    if [ ! -s "${BACKUP_PATH}" ]; then
        log_error "Backup file is empty: ${BACKUP_PATH}"
        exit 1
    fi

    # Test gzip integrity
    if gzip -t "${BACKUP_PATH}" 2>> "${LOG_FILE}"; then
        log_success "Backup file integrity verified"
    else
        log_error "Backup file is corrupted"
        exit 1
    fi

    # Generate checksum
    local checksum=$(sha256sum "${BACKUP_PATH}" | cut -d' ' -f1)
    echo "${checksum}" > "${BACKUP_PATH}.sha256"
    log_info "Checksum: ${checksum}"
}

# ══════════════════════════════════════════════════════════════
# 🗑️ BACKUP ROTATION
# ══════════════════════════════════════════════════════════════

rotate_backups() {
    log_info "Rotating old backups (retention: ${BACKUP_RETENTION_DAYS} days)..."

    # Find and delete backups older than retention period
    local deleted_count=0
    while IFS= read -r -d '' old_backup; do
        log_info "Deleting old backup: $(basename "${old_backup}")"
        rm -f "${old_backup}" "${old_backup}.sha256"
        ((deleted_count++))
    done < <(find "${BACKUP_DIR}" -name "aurora_db_*.sql.gz" -type f -mtime +${BACKUP_RETENTION_DAYS} -print0)

    if [ ${deleted_count} -gt 0 ]; then
        log_info "Deleted ${deleted_count} old backup(s)"
    else
        log_info "No old backups to delete"
    fi

    # List current backups
    local backup_count=$(find "${BACKUP_DIR}" -name "aurora_db_*.sql.gz" -type f | wc -l)
    log_info "Current backup count: ${backup_count}"
}

# ══════════════════════════════════════════════════════════════
# 📊 BACKUP SUMMARY
# ══════════════════════════════════════════════════════════════

backup_summary() {
    log_info "═══════════════════════════════════════════════════"
    log_info "BACKUP SUMMARY"
    log_info "═══════════════════════════════════════════════════"
    log_info "Database: ${DB_NAME}"
    log_info "Backup file: ${BACKUP_PATH}"
    log_info "Backup size: $(du -h "${BACKUP_PATH}" | cut -f1)"
    log_info "Timestamp: ${TIMESTAMP}"
    log_info "Retention: ${BACKUP_RETENTION_DAYS} days"
    log_info "Total backups: $(find "${BACKUP_DIR}" -name "aurora_db_*.sql.gz" -type f | wc -l)"
    log_info "═══════════════════════════════════════════════════"
}

# ══════════════════════════════════════════════════════════════
# 📧 NOTIFICATION (Optional)
# ══════════════════════════════════════════════════════════════

send_notification() {
    local status="$1"
    local message="$2"

    # Check if notification webhook is configured
    if [ -n "${BACKUP_WEBHOOK_URL:-}" ]; then
        log_info "Sending notification..."

        curl -X POST "${BACKUP_WEBHOOK_URL}" \
            -H "Content-Type: application/json" \
            -d "{
                \"status\": \"${status}\",
                \"message\": \"${message}\",
                \"timestamp\": \"${TIMESTAMP}\",
                \"database\": \"${DB_NAME}\",
                \"backup_file\": \"${BACKUP_COMPRESSED}\"
            }" \
            2>> "${LOG_FILE}" || log_error "Failed to send notification"
    fi
}

# ══════════════════════════════════════════════════════════════
# 🚀 MAIN EXECUTION
# ══════════════════════════════════════════════════════════════

main() {
    log_info "╔════════════════════════════════════════════════════╗"
    log_info "║     Aurora-X Database Backup Script               ║"
    log_info "╚════════════════════════════════════════════════════╝"

    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --retention)
                BACKUP_RETENTION_DAYS="$2"
                shift 2
                ;;
            --help)
                echo "Usage: $0 [--retention DAYS]"
                echo ""
                echo "Options:"
                echo "  --retention DAYS    Set backup retention period (default: 30 days)"
                echo "  --help              Show this help message"
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                exit 1
                ;;
        esac
    done

    # Execute backup process
    preflight_checks
    backup_database
    verify_backup
    rotate_backups
    backup_summary

    # Send success notification
    send_notification "success" "Database backup completed successfully"

    log_success "Backup process completed successfully!"
    exit 0
}

# ══════════════════════════════════════════════════════════════
# 🔥 ERROR HANDLING
# ══════════════════════════════════════════════════════════════

trap 'log_error "Backup failed with error on line $LINENO"; send_notification "error" "Backup failed with error"; exit 1' ERR

# Run main function
main "$@"
