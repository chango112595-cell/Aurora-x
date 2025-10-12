#!/usr/bin/env bash
# Aurora-X Auto-Updater Cron Installer
# This script installs cron jobs to automatically check for updates

set -Eeuo pipefail

# Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
UPDATER="$SCRIPT_DIR/update-aurora.sh"

# Ensure the updater script exists
if [[ ! -f "$UPDATER" ]]; then
    echo "❌ Error: update-aurora.sh not found at: $UPDATER"
    exit 1
fi

# Make the updater script executable
chmod +x "$UPDATER"

echo "🔧 Installing Aurora-X auto-updater cron jobs..."

# Create a temporary file for the new crontab
TMP_CRON="$(mktemp)"

# Get existing crontab (if any) and remove any existing aurora update entries
crontab -l 2>/dev/null | grep -v 'update-aurora.sh' > "$TMP_CRON" || true

# Add our cron jobs
{
    echo "# Aurora-X Auto-Updater Cron Jobs"
    echo "# Quick update check every 15 minutes"
    echo "*/15 * * * * ${UPDATER} >/tmp/aurora-update.log 2>&1"
    echo ""
    echo "# Full refresh nightly at 3:00 AM"
    echo "0 3 * * * ${UPDATER} >/tmp/aurora-update-nightly.log 2>&1"
    echo ""
} >> "$TMP_CRON"

# Install the new crontab
crontab "$TMP_CRON"
rm -f "$TMP_CRON"

echo "✅ Cron jobs installed successfully!"
echo ""
echo "📋 Current crontab entries for Aurora-X:"
crontab -l | grep 'update-aurora.sh' || echo "No Aurora-X cron jobs found"
echo ""
echo "📊 Cron schedule:"
echo "  • Every 15 minutes: Quick update check"
echo "  • Daily at 3:00 AM: Full refresh"
echo ""
echo "📁 Log files:"
echo "  • /tmp/aurora-update.log - Quick update logs"
echo "  • /tmp/aurora-update-nightly.log - Nightly refresh logs"
echo ""
echo "💡 To view logs:"
echo "  tail -f /tmp/aurora-update.log"
echo "  tail -f /tmp/aurora-update-nightly.log"
echo ""
echo "💡 To remove cron jobs later:"
echo "  crontab -l | grep -v 'update-aurora.sh' | crontab -"