#!/usr/bin/env bash
set -euo pipefail
DST=".progress_history"
KEEP=30
mkdir -p "$DST"
STAMP="$(date -u +%Y%m%d_%H%M%S)"

# Seeds + progress snapshots
[ -f .aurora/seeds.json ] && cp .aurora/seeds.json "$DST/seeds_$STAMP.json" || true
[ -f progress.json ] && cp progress.json "$DST/progress_$STAMP.json" || true

# prune old
ls -1t "$DST" | awk "NR>$KEEP" | while read -r f; do rm -f "$DST/$f"; done
echo "Snapshot complete: $STAMP"