#!/usr/bin/env bash
set -euo pipefail
CATALOG="$(cd "$(dirname "$0")/catalog" && pwd)"
mkdir -p "$CATALOG"
SRC="$1"
if [[ ! -f "$SRC" ]]; then
  echo "usage: $0 path/to/plugin.tar.gz"
  exit 1
fi
cp "$SRC" "$CATALOG/$(basename "$SRC")"
echo "Published $(basename "$SRC") to marketplace catalog"
