#!/bin/bash
#
# Aurora Database Migration Helper Scripts
# Convenient wrappers for common Alembic operations
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "${PROJECT_ROOT}"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

echo_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

echo_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Show current migration status
status() {
    echo "📊 Current Migration Status:"
    echo "=============================="
    alembic current
    echo ""
    echo "📋 Migration History:"
    alembic history --verbose
}

# Create a new migration
create() {
    local message="$1"

    if [ -z "$message" ]; then
        echo_error "Migration message required"
        echo "Usage: $0 create \"Description of changes\""
        exit 1
    fi

    echo "🔨 Creating new migration: $message"
    alembic revision --autogenerate -m "$message"
    echo_success "Migration created successfully"
}

# Upgrade to latest version
upgrade() {
    echo "⬆️  Upgrading database to latest version..."
    alembic upgrade head
    echo_success "Database upgraded successfully"
    status
}

# Downgrade one version
downgrade() {
    local steps="${1:-1}"
    echo "⬇️  Downgrading database by $steps version(s)..."

    # Confirmation for safety
    read -p "Are you sure you want to downgrade? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo_warning "Downgrade cancelled"
        exit 0
    fi

    if [ "$steps" = "all" ]; then
        alembic downgrade base
    else
        alembic downgrade -$steps
    fi
    echo_success "Database downgraded successfully"
    status
}

# Show migration history
history() {
    echo "📜 Migration History:"
    echo "===================="
    alembic history --verbose
}

# Show current version
current() {
    echo "📍 Current Migration Version:"
    alembic current
}

# Upgrade to specific version
upgrade_to() {
    local version="$1"

    if [ -z "$version" ]; then
        echo_error "Version required"
        echo "Usage: $0 upgrade-to <revision_id>"
        exit 1
    fi

    echo "⬆️  Upgrading to version: $version"
    alembic upgrade "$version"
    echo_success "Database upgraded successfully"
}

# Downgrade to specific version
downgrade_to() {
    local version="$1"

    if [ -z "$version" ]; then
        echo_error "Version required"
        echo "Usage: $0 downgrade-to <revision_id>"
        exit 1
    fi

    echo "⬇️  Downgrading to version: $version"

    # Confirmation for safety
    read -p "Are you sure you want to downgrade to $version? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo_warning "Downgrade cancelled"
        exit 0
    fi

    alembic downgrade "$version"
    echo_success "Database downgraded successfully"
}

# Show SQL for migration without applying
show_sql() {
    local version="${1:-head}"
    echo "📄 SQL for migration to $version:"
    echo "================================="
    alembic upgrade "$version" --sql
}

# Stamp database with specific version (without running migrations)
stamp() {
    local version="${1:-head}"
    echo "🏷️  Stamping database with version: $version"

    echo_warning "This will mark the database as being at version $version without running migrations"
    read -p "Are you sure? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo_warning "Stamp cancelled"
        exit 0
    fi

    alembic stamp "$version"
    echo_success "Database stamped successfully"
}

# Reset database (downgrade all, then upgrade)
reset() {
    echo "🔄 Resetting database..."

    echo_warning "This will downgrade to base and then upgrade to head"
    read -p "Are you sure? This will reset all data! (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo_warning "Reset cancelled"
        exit 0
    fi

    alembic downgrade base
    alembic upgrade head
    echo_success "Database reset successfully"
}

# Show help
help() {
    cat << EOF
Aurora Database Migration Helper

Usage: $0 <command> [arguments]

Commands:
    status              Show current migration status and history
    create <message>    Create a new migration with autogenerate
    upgrade             Upgrade to latest version (head)
    downgrade [steps]   Downgrade by N steps (default: 1, use 'all' for base)
    history             Show complete migration history
    current             Show current migration version
    upgrade-to <rev>    Upgrade to specific revision
    downgrade-to <rev>  Downgrade to specific revision
    show-sql [version]  Show SQL for migration without applying
    stamp [version]     Mark database as being at version (default: head)
    reset               Reset database (downgrade to base, then upgrade to head)
    help                Show this help message

Examples:
    $0 status
    $0 create "Add user preferences table"
    $0 upgrade
    $0 downgrade 2
    $0 upgrade-to abc123
    $0 show-sql head
    $0 reset

Note: Always backup your database before running migrations!

EOF
}

# Main command dispatcher
case "${1:-help}" in
    status)
        status
        ;;
    create)
        create "$2"
        ;;
    upgrade)
        upgrade
        ;;
    downgrade)
        downgrade "$2"
        ;;
    history)
        history
        ;;
    current)
        current
        ;;
    upgrade-to)
        upgrade_to "$2"
        ;;
    downgrade-to)
        downgrade_to "$2"
        ;;
    show-sql)
        show_sql "$2"
        ;;
    stamp)
        stamp "$2"
        ;;
    reset)
        reset
        ;;
    help|--help|-h)
        help
        ;;
    *)
        echo_error "Unknown command: $1"
        help
        exit 1
        ;;
esac
