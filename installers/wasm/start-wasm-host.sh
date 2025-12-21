#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYODIDE_DIR="$ROOT_DIR/pyodide"

if [ ! -f "$PYODIDE_DIR/pyodide.js" ]; then
  echo "Missing pyodide assets in $PYODIDE_DIR"
  echo "Place pyodide.js, pyodide.wasm, and python_stdlib.zip there."
  exit 1
fi

python -m http.server 8123 --directory "$ROOT_DIR"
