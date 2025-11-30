#!/usr/bin/env bash
set -euo pipefail
# Start core in background, wait, test health, then stop
PKGDIR="$(cd "$(dirname "$0")/.." && pwd)"
bash "$PKGDIR/start.sh"
sleep 1
bash "$PKGDIR/health_check.sh"
RC=$?
echo "health rc=$RC"
bash "$PKGDIR/stop.sh"
exit $RC
