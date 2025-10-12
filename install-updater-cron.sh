#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
UPDATER="$SCRIPT_DIR/update-aurora.sh"

chmod +x "$UPDATER"

# Write a temp cron file
TMP_CRON="$(mktemp)"
crontab -l 2>/dev/null | grep -v 'update-aurora.sh' > "$TMP_CRON" || true

{
  echo "*/15 * * * * ${UPDATER} >/tmp/aurora-update.log 2>&1"
  echo "0 3 * * * ${UPDATER} >/tmp/aurora-update-nightly.log 2>&1"
} >> "$TMP_CRON"

crontab "$TMP_CRON"
rm -f "$TMP_CRON"

echo "✅ Cron installed:"
crontab -l