#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
echo "[pack03] Running activation hooks..."

# Ensure data directories exist
mkdir -p "$ROOT/data/vfs" "$ROOT/data/gov" "$ROOT/data/security" "$ROOT/logs" "$ROOT/backups"

# Initialize namespace registry if needed
if [ ! -f "$ROOT/data/namespaces.json" ]; then
    echo '{}' > "$ROOT/data/namespaces.json"
fi

# Initialize vnet registry if needed
if [ ! -f "$ROOT/data/vnet_registry.json" ]; then
    echo '{}' > "$ROOT/data/vnet_registry.json"
fi

# Run diagnostics collection
python3 "$ROOT/core/diagnostics.py" || true

echo "[pack03] Activation hooks complete."
