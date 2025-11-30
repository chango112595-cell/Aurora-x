#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
echo "[pack04] activate hook running: registering launcher manifest"

# generate a minimal launch_manifest.json if absent
MAN="$ROOT/data/launch_manifest.json"
mkdir -p "$ROOT/data"
if [[ ! -f "$MAN" ]]; then
  cat > "$MAN" <<'JSON'
{
  "jobs": [
    {"name": "example_job", "cmd": "echo example", "depends_on": []}
  ]
}
JSON
  echo "[pack04] generated default launch manifest"
fi

echo "[pack04] activate hook complete"
