#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PACKS="$ROOT/packs"
STAGING="$ROOT/staging"
LIVE="$ROOT/live"
BACKUPS="$ROOT/backups"
AUDIT="$ROOT/audit"
DEVTOOLS="$ROOT/dev-tools"

mkdir -p "$PACKS" "$STAGING" "$LIVE" "$BACKUPS" "$AUDIT" "$DEVTOOLS"

for i in $(seq 1 15); do
  pack="pack$(printf "%02d" $i)_pack$(printf "%02d" $i)"
  dir="$PACKS/$pack"
  mkdir -p "$dir"
  cat > "$dir/install.sh" <<'SH2'
#!/usr/bin/env bash
echo "Install stub for PACK"
exit 0
SH2
  cat > "$dir/start.sh" <<'SH2'
#!/usr/bin/env bash
echo "Start stub"
exit 0
SH2
  cat > "$dir/stop.sh" <<'SH2'
#!/usr/bin/env bash
echo "Stop stub"
exit 0
SH2
  cat > "$dir/health_check.sh" <<'SH2'
#!/usr/bin/env bash
# default healthy
exit 0
SH2
  chmod +x "$dir"/*.sh
done

echo "Skeleton packs created under $PACKS"
echo "Safety dirs created: $STAGING $LIVE $BACKUPS $AUDIT $DEVTOOLS"
